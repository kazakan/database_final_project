import os

from flask import Flask, render_template, request

from db import *

app = Flask(__name__)

db, _ = init_db()

@app.route("/", methods=('GET', 'POST'))
def index():
    movieList = []
    if request.method == "GET":
        return render_template("base.html", movie_list=movieList)
    elif request.method == "POST":
        cur = db.cursor(pymysql.cursors.DictCursor)
        query = request.form.get('query')
        cur.execute(f"SELECT * FROM movie WHERE mv_name like '%{query}%'")
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
            cur.execute(f"SELECT country FROM db_final.where_made WHERE mv_code=%s;",c)
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

        return render_template('base.html', movie_list=movieList)

@app.route("/detail")
def detail():
    mvcode = request.args.get('mvcode')

    # Get movie info
    cur = db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM movie WHERE mv_code=%s",mvcode)
    movie = cur.fetchone()

    # get director infos
    cur.execute("SELECT * FROM director WHERE director.dr_code IN (SELECT who_directed.dr_code from who_directed where who_directed.mv_code=%s)",mvcode)
    directors = cur.fetchall()

    # actors
    cur.execute("SELECT * FROM actor WHERE actor.ac_code IN (SELECT who_acted.ac_code from who_acted where who_acted.mv_code=%s)",mvcode)
    actors = cur.fetchall()

    # genre
    cur.execute("SELECT genre FROM genres WHERE mv_code=%s",mvcode)
    genres = cur.fetchall()

    # country
    cur.execute("SELECT country FROM db_final.where_made WHERE mv_code=%s",mvcode)
    countries = cur.fetchall()


    return render_template(
        "detail.html",
        movie=movie,
        directors=directors,
        actors=actors,
        genres=genres,
        countries=countries
        )

if __name__ == "__main__":
    app.run(debug=True)
