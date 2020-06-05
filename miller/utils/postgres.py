import re
from django.contrib.postgres.search import SearchQuery


class RawSearchQuery(SearchQuery):
    """
    Extends SearchQuery to allow to_tsquery instead of plainto_tsquery

    Transform and in AND, or in OR
    e.g. claude & juncker or claude AND
    then throw away all punctuation and AND and OR
    substitute * with :*
    """
    parsed_value = ''
    parsed_query = ''

    def qparse(self, query):
        # print query
        query = query.strip()
        # 1 check for ANDS or &
        ands = re.split(r'\s+or\s+|\s+&\s+', query, flags=re.IGNORECASE)
        if len(ands) > 1:
            return ' & '.join(map(lambda x: self.qparse(x), ands))

        ors = re.split(r'\s+or\s+|,', query, flags=re.IGNORECASE)
        if len(ors) > 1:
            return ' | '.join(map(lambda x: self.qparse(x), ors))

        # get rid of quotes at the beginning and at the end
        query = re.sub(r'^\'+|\'+$|\'\*|\'\:\*', '', query).strip()

        # substitute :* or * if they are at the end of a word
        query = ':* '.join(re.split(
            r'\:\*|\*',
            query,
            flags=re.IGNORECASE
        )).strip()

        # substitute escaped chars with spaces, then strip
        query = re.sub(r'\'+', ' ', query).strip()

        query = re.sub(r'[\?\(\)\|\&]', '', query)
        # print query
        self.parsed_query = ' & '.join(filter(None, re.split(r'\s+', query)))
        # concat spaces.
        # print self.parsed_query
        return self.parsed_query

    def as_sql(self, compiler, connection):
        if not self.parsed_value:
            self.parsed_value = self.qparse(self.value)
        params = [self.parsed_value]

        if self.config:
            config_sql, config_params = compiler.compile(self.config)
            template = 'to_tsquery({}::regconfig, %s)'.format(config_sql)
            params = config_params + [self.parsed_value]
        else:
            template = 'to_tsquery(%s)'
        if self.invert:
            template = '!!({})'.format(template)
        return template, params
