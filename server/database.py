import postgresql

DB_NAME = 'quazi'
DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

db = postgresql.open('pq://' + DB_USER + ':' + DB_PASS +'@' + DB_HOST + ':' + DB_PORT + '/' + DB_NAME)
