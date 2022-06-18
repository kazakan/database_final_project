from glob import iglob
import pickle
from pathlib import Path
from typing import Tuple
import dotenv
import os
import pymysql


def create_insert_sql(table_name, n_cols, ignore=True):
    statement = "INSERT "
    if ignore:
        statement += "IGNORE "
    statement += "INTO "
    statement += table_name
    statement += " VALUES ( "
    statement += ("%s,"*n_cols)[:-1]
    statement += " )"
    return statement


MOVIE_COLUMNS = [
    'mv_code', "mv_name", "altname", "playtime",
    "watched_rating_num", "watched_rating", "commentor_rating", "netizen_rating_num", "netizen_rating",
    "poster_url", "year","story"
]

ACTOR_COLUMNS = ["ac_code", "ac_name", "img_url"]

DIRECTOR_COLUMNS = ["dr_code", "dr_name", " img_url"]

INSERT_INTO_MOVIE = create_insert_sql("movie", len(MOVIE_COLUMNS))
INSERT_INTO_ACTOR = create_insert_sql("actor", len(ACTOR_COLUMNS))
INSERT_INTO_DIRECTOR = create_insert_sql("director", len(DIRECTOR_COLUMNS))

INSERT_INTO_WHO_DIRECTED = create_insert_sql("who_directed", 2)
INSERT_INTO_WHO_ACTED = create_insert_sql("who_acted", 4)
INSERT_INTO_WHERE_MADE = create_insert_sql("where_made", 2)
INSERT_INTO_WHAT_GRADE = create_insert_sql("what_grade", 2)

INSERT_INTO_REPLY = create_insert_sql("reply", 5)
INSERT_INTO_GENRES = create_insert_sql("genres",2)

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


def insert_movie_param(code, data, basic_data) -> Tuple or None:
    mv = data['mv']
    
    story = basic_data.get("story","") if basic_data is not None else ""
    return (
        code,  # mv_code
        mv.get("name",""),        # "mv_name"
        mv.get("altname",""),        # "altname"
        mv.get("minute"),        # "playtime"
        mv.get("watched_rating_num"),  # "watched_rating_num"
        mv.get("watched_rating"),  # "watched_rating"
        mv.get("commentor_rating"),  # "commentor_rating"
        mv.get("netizen_rating_num"),  # "netizen_rating_num"
        mv.get("netizen_rating"),  # "netizen_rating"
        data.get('poster',""),  # "poster_url"
        mv.get("year"),  # "year"
        story
    )


def insert_actor_param(code, data) -> tuple[list[tuple]]:
    """
    Returns 2 list of tuples.

    One is for 'actor' table, another is for 'who_acted' table 
    """
    actors = data.get("actor")
    if actors is None or len(actors) == 0:
        return None, None

    params_actor = []
    params_who_acted = []

    for actor in actors:
        ismain = actor.get('ismain')
        if ismain is not None:
            ismain = 1 if ismain == "주연" else 0

        param_actor = (
            actor['code'],  # "ac_code",
            actor.get('name'),  # "ac_name",
            actor.get('img'),  # "img_url"
        )

        param_who_acted = (
            code,
            actor['code'],
            ismain,  # "ismain",
            actor.get('role')  # "ac_role",
        )

        params_actor.append(param_actor)
        params_who_acted.append(param_who_acted)
        
    return params_actor, params_who_acted


def insert_director_param(code, data) -> tuple[list[tuple]]:
    """
    Returns 2 list of tuples.

    One is for 'actor' table, another is for 'who_acted' table 
    """
    directors = data.get("director")
    if directors is None or len(directors) == 0:
        return None, None

    params_director = []
    params_who_directed = []

    for director in directors:
        dr_code = director.get('code')
        if dr_code is None:
            continue

        param_director = (
            dr_code,  # "dr_code",
            director.get('name'), # dr_name
            director.get('img') # img_url
        )

        param_who_directed = (code, director['code'])

        params_director.append(param_director)
        params_who_directed.append(param_who_directed)
        
    return params_director, params_who_directed


def insert_where_made_param(code, data) -> list[Tuple] or None:
    countries = data['mv'].get('nation')
    if countries is None or len(countries) == 0:
        return None

    params_country = []
    for country in countries:
        params_country.append((code,country))
    return params_country


def insert_what_grade_param(code, data) -> Tuple or None:
    grades = data['mv'].get('grade')
    if grades is None or len(grades) == 0:
        return None

    params_grade = []
    for grade in grades:
        params_grade.append((code,grade))
    return params_grade

def insert_genres_param(code, data) -> Tuple or None:
    genres = data['mv'].get('summarys')
    if genres is None or len(genres) == 0:
        return None

    params_genres = []
    for genre in genres:
        params_genres.append((code,genre))
    return params_genres

def insert_reply(code,basic_data):
    if basic_data is None:
        return None
        
    comments = basic_data.get("comments")
    if comments is None or len(comments) == 0:
        return None
    
    params_comments = []
    for comment in comments:
        params_comments.append(
            (
                code,
                comment.get("star"),
                comment.get("good"),
                comment.get("bad"),
                comment.get("reple","")
            )
        )
    return params_comments


def main():
    db, cur = init_db()

    PICKLE_PATH_ROOT = Path("./out")
    for pickle_path in PICKLE_PATH_ROOT.glob("*.pickle"):
        if("basic" in pickle_path.name) : continue

        code_start, code_end = pickle_path.name.split('.')[-2].split('_')[:2]
        code_range = range(int(code_start), int(code_end))

        params_movie = []
        params_actor = []
        params_director = []
        params_who_acted = []
        params_who_directed = []
        params_where_made = []
        params_what_grade = []
        params_reply = []
        params_genres = []

        with open(pickle_path, 'rb') as f:
            datas = pickle.load(f)

        with open(str(PICKLE_PATH_ROOT)+f"/{code_start}_{code_end}_basic.pickle",'rb') as f:
            basic_data = pickle.load(f)

        for mv_code, data ,basic in zip(code_range, datas, basic_data):

            if data is None:
                continue

            # create params
            p1 = insert_movie_param(mv_code,data,basic)
            if p1 is not None:
                params_movie.append(p1)

            p1, p2 = insert_actor_param(mv_code,data)
            if p1 is not None:
                params_actor.extend(p1)
                params_who_acted.extend(p2)

            p1, p2 = insert_director_param(mv_code,data)
            if p1 is not None:
                params_director.extend(p1)
                params_who_directed.extend(p2)

            p1 = insert_what_grade_param(mv_code,data)
            if p1 is not None:
                params_what_grade.extend(p1)

            p1 = insert_where_made_param(mv_code,data)
            if p1 is not None:
                params_where_made.extend(p1)

            p1 = insert_reply(mv_code,basic)
            if p1 is not None:
                params_reply.extend(p1)
         
            p1 = insert_genres_param(mv_code,data)
            if p1 is not None:
                params_genres.extend(p1)

        # insert
        cur.executemany(INSERT_INTO_MOVIE,params_movie)
        db.commit()
        cur.executemany(INSERT_INTO_ACTOR,params_actor)
        db.commit()
        cur.executemany(INSERT_INTO_DIRECTOR,params_director)
        db.commit()
        cur.executemany(INSERT_INTO_WHO_ACTED,params_who_acted)
        db.commit()
        cur.executemany(INSERT_INTO_WHO_DIRECTED,params_who_directed)
        db.commit()
        cur.executemany(INSERT_INTO_WHAT_GRADE,params_what_grade)
        db.commit()
        cur.executemany(INSERT_INTO_WHERE_MADE,params_where_made)
        db.commit()
        cur.executemany(INSERT_INTO_REPLY,params_reply)
        db.commit()
        cur.executemany(INSERT_INTO_GENRES,params_genres)
        db.commit()

if __name__ == "__main__":
    main()
