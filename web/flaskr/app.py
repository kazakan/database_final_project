import os

from flask import Flask, render_template, request

from db import *

app = Flask(__name__)

db, _ = init_db()
_.close()

# get all countries
all_country = []

# get all genres
all_genre = []

# get all grade
all_grade = []

@app.route("/", methods=('GET', 'POST'))
def index():
    movieList = []
    cur = db.cursor()
    global all_country
    if len(all_country) == 0:
        cur.execute("select distinct(country) from where_made")
        all_country = [x[0] for x in _.fetchall()]

    global all_genre
    if len(all_genre) == 0:
        cur.execute("select distinct(genre) from genres")
        all_genre = [x[0] for x in _.fetchall()]

    global all_grade
    if len(all_grade) == 0:
       cur.execute("select distinct(grade) from what_grade")
       all_grade = [x[0] for x in _.fetchall()]
    cur.close()


    if request.method == "GET":
        return render_template("base.html", movie_list=movieList,all_country=all_country, all_genre=all_genre, all_grade=all_grade)
    elif request.method == "POST":
        # get constraints
        query = request.form.get('query')
        searchby = request.form.get('searchby')
        orderby = request.form.get('orderby')
        countryfilter = request.form.get('countryfilter')
        genrefilter = request.form.get('genrefilter')
        yearfilter = request.form.get('year')
        gradefilter = request.form.get('gradefilter')
            
        is_where_in = False
        if searchby == "drname":
            sql = f"select m.* from movie m join (select distinct mv_code from who_directed wd join( select * from director where dr_name = '{query}') t using(dr_code)) aaa using(mv_code)"
        elif searchby == "acname":
            sql = f"select m.* from movie m join (select distinct mv_code from who_acted wd join( select * from actor where ac_name = '{query}') t using(ac_code)) aaa using(mv_code)"
        else:
            sql = f"SELECT * FROM movie WHERE mv_name like '%{query}%'"
            is_where_in = True

        if yearfilter != "":
            cond = f" mv_year={yearfilter}"
            if not is_where_in : sql += f" where "
            else : sql += " and "
            sql += cond

        if countryfilter != "noapply":
            sql = "select m.* from ("+sql+f") m join (select mv_code from where_made where country='{countryfilter}') wm using (mv_code)"

        if genrefilter != "noapply":
            sql = "select m.* from ("+sql+f") m join (select mv_code from genres where genre='{genrefilter}') wm using (mv_code)"

        if gradefilter != "noapply":
            sql = "select m.* from ("+sql+f") m join (select mv_code from what_grade where grade='{gradefilter}') wm using (mv_code)"

        if orderby == "name":
            sql += " order by mv_name "
        elif orderby == "year":
            sql += " order by mv_year desc"
        elif orderby == "rating":
            sql += " order by netizen_rating desc"
        elif orderby == "watched":
            sql += " order by watched_rating_num desc"

        cur = db.cursor(pymysql.cursors.DictCursor)
        print(sql)
        cur.execute(sql)
        movieList = cur.fetchall()
        
        # get directors
        mv_codes = [(movie['mv_code'],) for movie in movieList]
        for idx, c in enumerate(mv_codes):
            cur.execute(f"SELECT director.dr_name FROM director WHERE director.dr_code IN (SELECT who_directed.dr_code from who_directed where who_directed.mv_code=%s)",c)
            res = cur.fetchall()
            if len(res) :
                directors_short = ','.join([ c['dr_name'] for c in res])
                movieList[idx]['directors'] = directors_short

        # get countries
        for idx, c in enumerate(mv_codes):
            cur.execute(f"SELECT country FROM where_made WHERE mv_code=%s;",c)
            res = cur.fetchall()
            if len(res) :
                country_short = ','.join([ c['country'] for c in res])
                movieList[idx]['countries'] = country_short

        # get actors
        for idx, c in enumerate(mv_codes):
            cur.execute(f"SELECT actor.ac_name FROM actor WHERE actor.ac_code IN (SELECT who_acted.ac_code from who_acted where who_acted.mv_code=%s) LIMIT 5;",c)
            res = cur.fetchall()
            if len(res) :
                actors_short = ','.join([ c['ac_name'] for c in res])
                movieList[idx]['actors'] = actors_short

        # get genres
        for idx, c in enumerate(mv_codes):
            cur.execute(f"SELECT genre FROM genres WHERE mv_code=%s;",c)
            res = cur.fetchall()
            if len(res) :
                genre_short = ','.join([ c['genre'] for c in res])
                movieList[idx]['genre'] = genre_short

        # get grades
        for idx, c in enumerate(mv_codes):
            cur.execute(f"SELECT grade FROM what_grade WHERE mv_code=%s;",c)
            res = cur.fetchall()
            if len(res) :
                grade_short = ','.join([ c['grade'] for c in res])
                movieList[idx]['grade'] = grade_short

        cur.close()

        return render_template('base.html', movie_list=movieList,all_country = all_country, all_genre=all_genre, all_grade=all_grade)

@app.route("/detail")
def detail():
    mvcode = request.args.get('mvcode')

    # Get movie info
    cur = db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM movie WHERE mv_code=%s",mvcode)
    movie = cur.fetchone()

    # get director infos
    cur.execute("SELECT * FROM who_directed left join director USING(dr_code) where mv_code = %s",mvcode)
    directors = cur.fetchall()

    # actors
    cur.execute("SELECT * FROM who_acted left join actor USING(ac_code) where mv_code = %s order by ismain desc",mvcode)
    actors = cur.fetchall()

    # genre
    cur.execute("SELECT genre FROM genres WHERE mv_code=%s",mvcode)
    genres = cur.fetchall()

    # country
    cur.execute("SELECT country FROM where_made WHERE mv_code=%s",mvcode)
    countries = cur.fetchall()

    # reply
    cur.execute("SELECT * FROM reply WHERE mv_code=%s",mvcode)
    replies = cur.fetchall()

    #grade
    cur.execute("SELECT * FROM what_grade WHERE mv_code=%s",mvcode)
    grades = cur.fetchall()

    cur.close()

    return render_template(
        "detail.html",
        movie=movie,
        directors=directors,
        actors=actors,
        genres=genres,
        countries=countries,
        replies=replies,
        grades=grades
        )

if __name__ == "__main__":
    app.run(debug=True)
