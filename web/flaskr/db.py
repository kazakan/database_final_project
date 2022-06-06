import dotenv
import pymysql
import os
import pymysql

def init_db():
    dotenv.load_dotenv()
    SQL_URL = os.getenv("SQL_URL")
    SQL_DB = os.getenv("SQL_DB")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWD = os.getenv("SQL_PASSWD")

    db = pymysql.connect(
        user=SQL_USER,
        passwd=SQL_PASSWD,
        host=SQL_URL,
        db=SQL_DB,
        charset='utf8'
    )

    cursor = db.cursor()

    return db, cursor