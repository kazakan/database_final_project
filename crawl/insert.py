from glob import iglob
import pickle
from pathlib import Path
from typing import Tuple
import dotenv
import os
import pymysql


def create_insert_sql(table_name, n_cols, ignore=False):
    statement = "INSERT "
    if ignore:
        statement += "IGNORE "
    statement += "INTO "
    statement += table_name
    statement += " VALUES ( "
    statement += ("%s,"*len(n_cols))[:-1]
    statement += " )"


MOVIE_COLUMNS = [
    'mv_code', "mv_name", "altname", "playtime", "release_date",
    "watched_rating_num", "watched_rating", "commentor_rating", "netizen_rating_num", "netizen_rating",
    "director_short", "country_short", "actor_short", "grade_short", "poster_url", "year"
]

ACTOR_COLUMNS = ["ac_code", "ac_name", "ismain", "ac_role", "img_url"]

DIRECTOR_COLUMNS = ["dr_code", "dr_name", " img_url"]

INSERT_INTO_MOVIE = create_insert_sql("movie", len(MOVIE_COLUMNS))
INSERT_INTO_ACTOR = create_insert_sql("actor", len(ACTOR_COLUMNS))
INSERT_INTO_DIRECTOR = create_insert_sql("director", len(DIRECTOR_COLUMNS))

INSERT_INTO_WHO_DIRECTED = create_insert_sql("who_directed", 2)
INSERT_INTO_WHO_ACTED = create_insert_sql("who_acted", 2)
INSERT_INTO_WHERE_MADE = create_insert_sql("where_made", 2)
INSERT_INTO_WHAT_GRADE = create_insert_sql("what_grade", 2)


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


def insert_movie_param(code, data) -> Tuple or None:
    mv = data['mv']
    return (
        code,  # mv_code
        mv.get("name"),        # "mv_name"
        mv.get("altname"),        # "altname"
        mv.get("minute"),        # "playtime"
        None,        # "release_date"
        mv.get("watched_rating_num"),  # "watched_rating_num"
        mv.get("watched_rating"),  # "watched_rating"
        mv.get("commentor_rating"),  # "commentor_rating"
        mv.get("netizen_rating_num"),  # "netizen_rating_num"
        mv.get("netizen_rating"),  # "netizen_rating"
        mv.get("director_short"),  # "director_short"
        None,  # "country_short"
        None,  # "actor_short"
        None,  # "grade_short"
        data.get['poster'],  # "poster_url"
        mv.get("year"),  # "year"
    )


def insert_actor_param(code, data) -> tuple[list[tuple]]:
    """
    Returns 2 list of tuples.

    One is for 'actor' table, another is for 'who_acted' table 
    """
    actors = data.get("actor")
    if actors is None or len(actor) == 0:
        return None

    params_actor = []
    params_who_acted = []

    for actor in actors:
        ismain = actor.get('ismain')
        if ismain is not None:
            ismain = 1 if ismain == "주연" else 0

        param_actor = (
            actor['code'],  # "ac_code",
            actor.get('name'),  # "ac_name",
            ismain,  # "ismain",
            actor.get('role'),  # "ac_role",
            actor.get('img'),  # "img_url"
        )

        param_who_acted = (code, actor['code'])

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
        return None

    params_director = []
    params_who_directed = []

    for director in directors:

        param_director = (
            director['code'],  # "dr_code",
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
        params_country.append(code,country)
    return params_country


def insert_what_grade_param(code, data) -> Tuple or None:
    grades = data['mv'].get('grade')
    if grades is None or len(grades) == 0:
        return None

    params_grade = []
    for grade in grades:
        params_grade.append(code,grade)
    return params_grade


def main():
    PICKLE_PATH_ROOT = Path("./out")
    for pickle_path in PICKLE_PATH_ROOT.glob("*.pickle"):
        code_start, code_end = pickle_path.name.split('.')[-2].split('_')[:2]
        code_range = range(int(code_start), int(code_end))

        with open(pickle_path, 'rb') as f:
            datas = pickle.load(f)

        for mv_code, data in zip(code_range, datas):

            if data is None:
                continue

            print(data)


if __name__ == "__main__":
    main()
