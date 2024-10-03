# updated 21th septemper 2024

import psycopg2
import settings

# OPEN THE CONNECTION TO THE DATABASE
conn = psycopg2.connect(
    database=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)
conn.autocommit = True
