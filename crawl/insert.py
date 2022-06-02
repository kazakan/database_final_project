from glob import iglob
import pickle
from pathlib import Path
import dotenv
import os
import pymysql

def init_db():
    dotenv.load_dotenv()
    SQL_URL=os.getenv("SQL_URL")
    SQL_DB=os.getenv("SQL_DB")
    SQL_USER=os.getenv("SQL_USER")
    SQL_PASSWD=os.getenv("SQL_PASSWD")

    db = pymysql.connect(
        user=SQL_USER,
        passwd=SQL_PASSWD,
        host=SQL_URL,
        db=SQL_DB,
        charset='utf8'
    )

    cursor = db.cursor()

    return db, cursor


def main():
    PICKLE_PATH_ROOT = Path("./out")
    for pickle_path in PICKLE_PATH_ROOT.glob("*.pickle"):
        code_start, code_end = pickle_path.name.split('.')[-2].split('_')[:2]
        code_range = range(int(code_start),int(code_end))

        with open(pickle_path,'rb') as f:
            datas = pickle.load(f)
        
        for mv_code, data in zip(code_range,datas):
            
            if data is None:
                continue

            
            print(data) 

    

           


if __name__ == "__main__":
    main()