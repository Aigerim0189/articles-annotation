import postgresql

DB_NAME = 'quazi'
DB_USER = 'usr'
DB_PASS = '12345'
DB_HOST = 'localhost'
DB_PORT = '5432'

db = postgresql.open('pq://' + DB_USER + ':' + DB_PASS +'@' + DB_HOST + ':' + DB_PORT + '/' + DB_NAME)
