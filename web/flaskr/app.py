import os

from flask import Flask, render_template, request

app = Flask(__name__)

lll = [
    {"name": "Halo", "poster": "https://movie-phinf.pstatic.net/20220516_144/1652665409592Chvey_JPEG/movie_image.jpg?type=m203_290_2","altname":""},
    {"name": "strange", "poster": "https://movie-phinf.pstatic.net/20220504_33/165164173504831gKe_JPEG/movie_image.jpg?type=m203_290_2","altname":"Alternative Name"}]


@app.route("/", methods=('GET', 'POST'))
def index():
    movieList = lll
    if request.method == "GET":
        return render_template("base.html", movie_list=movieList)
    elif request.method == "POST":
        return render_template('base.html', movie_list=movieList)


if __name__ == "__main__":
    app.run(debug=True)
