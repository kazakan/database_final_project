from glob import iglob
import pickle
from pathlib import Path
from typing import Tuple
import dotenv
import os
import pymysql

MOVIE_COLUMNS =[
    'mv_code',"mv_name","altname" ,"playtime" ,"release_date" ,
    "watched_rating_num" ,"watched_rating" ,"commentor_rating" ,"netizen_rating_num" ,"netizen_rating" ,
    "director_short" ,"country_short","actor_short","grade_short" ,"poster_url","year"
]

ACTOR_COLUMNS =["ac_code", "ac_name", "ismain", "ac_role", "img_url"]

DIRECTOR_COLUMNS =["dr_code", "dr_name", " img_url"]

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

def insert_movie_param(code,data) -> Tuple or None :
    mv = data['mv']
    return (
        code, # mv_code
        mv.get("name"),        # "mv_name"
        mv.get("altname"),        # "altname" 
        mv.get("minute"),        # "playtime" 
        None,        # "release_date" 
        mv.get("watched_rating_num"),        #"watched_rating_num" 
        mv.get("watched_rating"),         #"watched_rating" 
        mv.get("commentor_rating"),         #"commentor_rating" 
        mv.get("netizen_rating_num"),         #"netizen_rating_num" 
        mv.get("netizen_rating"),         #"netizen_rating" 
        mv.get("director_short"),         #"director_short" 
        None,         #"country_short"
        None,         #"actor_short"
        None,         #"grade_short" 
        data.get['poster'],         #"poster_url"
        mv.get("year"),         #"year"
    )

def insert_actor_param(code,data)  ->  Tuple or None :
    return ()

def insert_director_param(code,data) -> Tuple or None :
    return ()

def insert_movie_param(code,data) -> Tuple or None :
    return ()

def insert_movie_param(code,data) -> Tuple or None :
    return ()


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
