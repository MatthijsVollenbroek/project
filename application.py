from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
from werkzeug.utils import secure_filename
import time, threading

from helpers import *

# configure application
app = Flask(__name__)
cwd = os.getcwd()
# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
UPLOAD_FOLDER = os.path.join(cwd, 'static/posts/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/")
@login_required
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    # forget any user_id
    session.clear()
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html", errormessage="Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", errormessage="Must provide password")

        check = login_user(request.form.get("username"), request.form.get("password"))
        # check dat username is ingevuld
        if check == -1:
            return render_template("login.html", errormessage="Must provide username")

        # check dat wachtwoord is ingevuld
        elif check == -2:
            return redirect(url_for('login'))

        elif check == -3:
            return render_template("login.html", errormessage="Password and username do not match")
        elif check == True:
            return redirect(url_for('homepage'))
    else:
        return render_template("login.html", errormessage=None)


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/homepage")
@login_required
def homepage():
    username = userIDtoName(session['user_id'])
    posts = recent_following(session['user_id'])
    following = followers(session['user_id'])
    return render_template("homepage.html", errormessage=None, username=username, posts=posts, following=following)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", errormessage="Must provide username to register")

        # check dat gebruikersnaam alleen letters en cijfers bevat
        elif request.form.get("username").isalnum() == False:
            return render_template("register.html", errormessage="Use only letters and numbers (also no spaces in name)")

        # check dat username niet te lang is
        elif len(request.form.get("username")) > 30:
            return render_template("register.html", errormessage="username has maximum of 30 characters")
        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", errormessage="must provide password to register")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", errormessage="must provide matching passwords")

        check = register_user(request.form.get("username"), request.form.get("password"))
        if check == False:
            return render_template("register.html", errormessage="username already in use")
        else:
            session["user_id"] = check
            return redirect(url_for('homepage'))

    else:
        return render_template("register.html", errormessage=None)


@app.route("/homepage_recent", methods=["GET", "POST"])
@login_required
def homepage_recent():
    posts = recent_posts()
    return render_template("homepage_recent.html", posts=posts, errormessage=None)

@app.route("/homepage_shame", methods=["GET", "POST"])
@login_required
def homepage_shame():
    lijst = trending_shame('shame')
    return render_template("homepage_shame.html", posts=lijst, errormessage=None)

@app.route("/homepage_trending", methods=["GET", "POST"])
@login_required
def homepage_trending():
    lijst = trending_shame('trending')
    return render_template("homepage_trending.html", posts=lijst, errormessage=None)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    # lijst van alle gebruikers
    users = table_list()
    # lijst verwerken in html tabel
    return render_template("search.html", users=users, errormessage=None)

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file_post' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file_post']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('homepage_trending'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filesort = filename.split('.')
            filesort = filesort[1]
            description = request.form.get("description")
            post_made(session["user_id"], filename, description)
            post_id = db.execute("SELECT post_id FROM posts WHERE user_id =:user_id AND file = :file", user_id=session['user_id'], file=filename)
            filename = url_for('static', filename='posts/') + 'post' + str(post_id[0]['post_id']) + '.' + filesort
            filenamelocal = 'post' + str(post_id[0]['post_id']) + '.' + filesort
            db.execute("UPDATE posts SET file = :file WHERE post_id=:post_id", file=filename, post_id=post_id[0]['post_id'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(filenamelocal)))
            return redirect(url_for("homepage"))
    else:
        return render_template("post.html", errormessage=None)

@app.route("/preview_gif", methods=["GET", "POST"])
@login_required
def preview_gif():
    if request.method == 'POST':
        zoekterm = request.form.get("query")
        results = preview_GIF(zoekterm)
        gifs = []
        for gif in range(len(results['data'])):
            url = results['data'][gif]['images']['original']['url']
            preview = results['data'][gif]['images']['fixed_height']['url']
            temp = [url, preview]
            gifs.append(temp)
        return render_template("preview_gif.html", data=gifs, errormessage=None)

@app.route("/post_gif", methods=["GET", "POST"])
@login_required
def post_gif():
    if request.method == "POST":
        url = request.form.get("giftopost")
        description = request.form.get("description")
        post_made(session['user_id'], url, description)
        return redirect(url_for('homepage'))


@app.route("/like/<postid>/<dest>", methods=['GET', 'POST'])
@login_required
def like(postid, dest):
    user_id = session['user_id']
    post_id = postid
    check = post_like(user_id, post_id)
    dest_template = dest + ".html"
    if check == False:
        return render_template(dest_template, errormessage="post already liked")
    else:
        return redirect(url_for(dest))

@app.route("/dislike/<postid>/<dest>", methods=['GET', 'POST'])
@login_required
def dislike(postid, dest):
    user_id = session['user_id']
    post_id = postid
    dest_template = dest + ".html"
    check = post_dislike(user_id, post_id)
    if check == False:
        return render_template(dest_template, errormessage="post already disliked")
    else:
        return redirect(url_for(dest))

@app.route("/myprofile", methods=['GET', 'POST'])
@login_required
def myprofile():
    user_data = profile_info(session['user_id'])
    username = user_data['user_info']['username']
    most_likes = user_data['user_info']['most_likes']
    most_dislikes = user_data['user_info']['most_dislikes']
    followers = user_data['user_info']['followers']
    if request.method == 'POST':
        bio = request.form.get("newbio")
        editbio(session['user_id'], bio)
    bio = profile_info(session['user_id'])['user_info']['description']
    return render_template('own_profile.html', username=username, most_likes=most_likes, most_dislikes=most_dislikes, errormessage=None, followers=followers, bio=bio)

@app.route("/profile/<userid>", methods=['GET', 'POST'])
@login_required
def profile(userid):
    if int(userid) == session['user_id']:
        return redirect(url_for('myprofile'))
    user_data = profile_info(userid)
    username = user_data['user_info']['username']
    most_likes = user_data['user_info']['most_likes']
    most_dislikes = user_data['user_info']['most_dislikes']
    followers = user_data['user_info']['followers']
    bio = user_data['user_info']['description']
    return render_template('profile.html', username=username, most_likes=most_likes, most_dislikes=most_dislikes, errormessage=None, followers=followers, bio=bio)