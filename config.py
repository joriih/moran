import os
import psycopg2

# Database
DATABASES_SELECTOR = {
    'postgresql': {
        'ENGINE': 'postgresql+psycopg2',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', '').rstrip(),
        'PASSWORD': os.environ.get('DB_PASSWORD', '').rstrip(),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    },
    'mariadb': {
        'ENGINE': 'mariadb',
        'NAME': os.environ.get('DB_NAME', 'gc'),
        'USER': os.environ.get('DB_USER', 'gc').rstrip(),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Driq1234').rstrip(),
        'HOST': os.environ.get('DB_HOST', '10.217.166.215'),
        'PORT': os.environ.get('DB_PORT', 40273),
    },
}



db = DATABASES_SELECTOR[os.environ.get('DB_TYPE', 'mariadb')]
DB_URL = f"{db['ENGINE']}://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}?charset=utf8"

if os.environ.get('DB_TYPE', 'postgresql') == 'postgresql':
    SCHEMA = db['NAME']

"""
def getConnection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, charset='utf8')
"""