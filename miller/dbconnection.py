import sys
import psycopg2
from . import settings

db_params = settings.DATABASES['default']

try:
    connection = psycopg2.connect(
        user=db_params['USER'],
        password=db_params['PASSWORD'],
        host=db_params['HOST'],
        port=db_params['PORT'],
        database=db_params['NAME']
    )

    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f'Connected to: {record}')
    sys.exit(0)
except Exception as e:
    print('DB is not ready', e)
    sys.exit(1)
