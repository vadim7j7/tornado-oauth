from os.path import join
from os import getcwd


DB_PSQL = {
    'host': '192.168.33.10',
    'port': '5432',
    'database': 'woproc',
    'user': 'developer',
    'password': 'developer'
}

DIR = getcwd()
TEMPLATE_PATH = join(DIR, 'templates')
STATIC_PATCH = join(DIR, 'statics')

REFRESH_TOKEN_EXPIRATION_TIME = 36000
TOKEN_EXPIRATION_TIME = 3600
TOKEN_ALGORITHM = 'HS256'
TOKEN_SECRET = 'chdzxhjhsnjs3u9shdjadnxo17d66sbdjbbsdgad7335121asdadasd'

DB_PSQL_DSN = 'postgres://{user}:{password}@{host}:{port}/{dbname}'.format(
    dbname=DB_PSQL['database'], user=DB_PSQL['user'],
    password=DB_PSQL['password'], host=DB_PSQL['host'], port=DB_PSQL['port']
)
