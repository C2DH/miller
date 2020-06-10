import os
import json
import gspread
from django.core.management.base import BaseCommand
from django.conf import settings
from miller.utils.models import get_valid_serialized_docs


class Command(BaseCommand):
    """
    note: to setup google service account end ENV varialbles follow
    https://github.com/C2DH/miller/wiki/import-documents-from-google-spreadsheet

    usage:

        ENV=development \
        pipenv run ./manage.py document_import_from_google_spreadsheet

    or if in docker:

        docker exec -it docker_miller_1 \
        python manage.py document_import_from_google_spreadsheet \
        [gsid]
        [--noprompt]
        [--fake]

    """
    help = 'import documents from a google spreadsheet using the ENV varialbs'

    def add_arguments(self, parser):
        parser.add_argument(
            'gsid', nargs='?', type=str,
            help='google spredsheet identifier (optional if you set a '
                 'GOOGLE_SPREADHSEEET_ID in your .env file)'
        )
        parser.add_argument(
            '--noprompt',
            action='store_true',
            help='avoid prompt for actual deployment',
        )
        parser.add_argument(
            '--fake',
            action='store_true',
            help='just test connectivity and JSON schema validation',
        )

    def handle(self, gsid='', noprompt=False, fake=False, *args, **options):
        service_account_filepath = os.environ.get(
            'GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY',
            None
        )
        gsid = gsid if gsid else os.environ.get(
            'GOOGLE_SPREADHSEEET_ID',
            None
        )
        self.stdout.write(f'using:--noprompt:{noprompt}')
        self.stdout.write(f'using:--fake: {fake}')
        self.stdout.write(
            f'using service_account_filepath: {service_account_filepath}')
        self.stdout.write(f'using gsid: {gsid}')

        if not gsid:
            self.stderr.write(
                'it looks like you don\'t have any valid gsid...')
            return
        gc = gspread.service_account(filename=service_account_filepath)
        sheet = gc.open_by_key(gsid)
        worksheet_list = sheet.worksheets()
        self.stdout.write(f'list of worksheet available:{worksheet_list}')
        # get all data from all worksheet and save it in an external file
        all_data = []
        for worksheet in worksheet_list:
            docs = worksheet.get_all_records()
            # docs ready to be employed
            expected_docs = [x for x in docs if x.get('slug', None)]
            expected_docs_slugs = set([x.get('slug') for x in expected_docs])
            complete_docs = [
                x for x in docs
                if x.get('type', None) and x.get('slug', None) and x.get('data__type', None)
            ]
            complete_docs_slugs = set([x.get('slug') for x in complete_docs])
            validated_docs = list(get_valid_serialized_docs(
                docs=complete_docs,
                ignore_duplicates=True,
                raise_validation_errors=True
            ))
            validated_docs_slugs = set([x.get('slug') for x in validated_docs])
            all_data = all_data + validated_docs
            self.stdout.write(
                f'worksheet {worksheet}'
                f' n. docs valid: {len(list(complete_docs))}'
                f' / {len(list(expected_docs))}'
                f' n. docs validated: {len(list(validated_docs))}'
            )
            self.stdout.write(
                f'worksheet {worksheet}'
                f' incomplete docs: {expected_docs_slugs - complete_docs_slugs}'
                f' invalid docs: {complete_docs_slugs - validated_docs_slugs}'
            )

        if fake:
            self.stdout.write('fake mode enabled, that\'s all!')
        else:
            # save into cache for future uses
            filename = os.path.join(
                settings.MILLER_CONTENTS_ROOT,
                f'document_import_from_gs_{gsid}.json'
            )

            self.stdout.write(f'writing {len(all_data)} in {filename}...')

            with open(filename, 'w') as out:
                out.write(json.dumps(all_data, sort_keys=True, indent=2))

            self.stdout.write(f'done, file {filename} written.')
