import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from werkzeug.utils import secure_filename

from helpers import *

# configureren application
app = Flask(__name__)
cwd = os.getcwd()
# zorgen dat responses niet gecached zijn
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configureren van sessie om filesystem te gebruiken (in plaats van signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
UPLOAD_FOLDER = os.path.join(cwd, 'static/posts/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

# CS50 Library configureren om SQLite database te gebruiken
db = SQL("sqlite:///project.db")


@app.route("/")
@login_required
def index():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    # vergeet opgeslagen user_id
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html", errormessage="Must provide username")

        # check dat er wachtwoord is ingevuld
        elif not request.form.get("password"):
            return render_template("login.html", errormessage="Must provide password")

        check = login_user(request.form.get("username"), request.form.get("password"))
        # check dat username is ingevuld
        if check == -1:
            return render_template("login.html", errormessage="Must provide username")

        # check dat wachtwoord is ingevuld
        elif check == -2:
            return redirect(url_for('login'))
        # check dat wachtwoorden overeenkomen
        elif check == -3:
            return render_template("login.html", errormessage="Password and username do not match")
        elif check == True:
            return redirect(url_for('homepage'))
    else:
        return render_template("login.html", errormessage=None)


@app.route("/logout")
def logout():
    """Log user out."""

    # vergeet user_id
    session.clear()
    return redirect(url_for("login"))


@app.route("/homepage")
@login_required
def homepage():
    # username ophalen om te groeten
    username = userIDtoName(session['user_id'])
    # laden posts van accounts die gevolgd worden door user
    posts = recent_following(session['user_id'])
    # volgend lijst ophalen
    following = followers(session['user_id'])
    return render_template("homepage.html", errormessage=None, username=username, posts=posts, following=following)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # check dat username opgegeven is
        if not request.form.get("username"):
            return render_template("register.html", errormessage="Must provide username to register")

        # check dat gebruikersnaam alleen letters en cijfers bevat
        elif request.form.get("username").isalnum() == False:
            return render_template("register.html", errormessage="Use only letters and numbers (also no spaces in name)")

        # check dat username niet te lang is
        elif len(request.form.get("username")) > 30:
            return render_template("register.html", errormessage="username has maximum of 30 characters")
        # check dat er een wachtwoord opgegeven is
        elif not request.form.get("password"):
            return render_template("register.html", errormessage="must provide password to register")
        # check dat wachtwoorden overeenkomen
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", errormessage="must provide matching passwords")

        check = register_user(request.form.get("username"), request.form.get("password"))
        # check of username al in gebruik is
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
    # meest recente posts laden
    posts = recent_posts()
    return render_template("homepage_recent.html", posts=posts, errormessage=None)


@app.route("/homepage_shame", methods=["GET", "POST"])
@login_required
def homepage_shame():
    # top vijf meest gedislikete posts inladen
    lijst = trending_shame('shame')
    return render_template("homepage_shame.html", posts=lijst, errormessage=None)


@app.route("/homepage_trending", methods=["GET", "POST"])
@login_required
def homepage_trending():
    # top vijf meest gelikete posts inladen
    lijst = trending_shame('trending')
    return render_template("homepage_trending.html", posts=lijst, errormessage=None)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    # lijst van alle gebruikers en info
    users = table_list()
    # lijst verwerken in html tabel
    return render_template("search.html", users=users, errormessage=None)


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == 'POST':
        # check of post request file bevat
        if 'file_post' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file_post']
        # als user geen file selecteert, submit de browser ook
        # een leeg deel zonder filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('homepage_trending'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # filesoort apart nemen voor later bij opslaan
            filesort = filename.split('.')
            filesort = filesort[1]
            description = request.form.get("description")
            post_made(session["user_id"], filename, description)
            post_id = postid(session['user_id'], filename)
            # nieuwe filename voor in database aanmaken
            filename = url_for('static', filename='posts/') + 'post' + str(post_id[0]['post_id']) + '.' + filesort
            # naam voor in folder
            filenamelocal = 'post' + str(post_id[0]['post_id']) + '.' + filesort
            # opslaan in database
            postnameUpdate(post_id[0]['post_id'], filename)
            # opslaan in folder
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
        # juiste data uit giphy lijst halen
        for gif in range(len(results['data'])):
            url = results['data'][gif]['images']['original']['url']
            preview = results['data'][gif]['images']['fixed_height']['url']
            temp = [url, preview]
            gifs.append(temp)
        # gifs inladen op html pagina
        return render_template("preview_gif.html", data=gifs, errormessage=None)


@app.route("/post_gif", methods=["GET", "POST"])
@login_required
def post_gif():
    if request.method == "POST":
        # url ophalen van gif die gepost moet worden
        url = request.form.get("giftopost")
        description = request.form.get("description")
        # posten met description
        post_made(session['user_id'], url, description)
        return redirect(url_for('homepage'))


@app.route("/like", methods=['GET', 'POST'])
@login_required
def like():
    if request.method == "GET":
        user_id = session['user_id']
        post_id = request.args.get('postid')
        # check of je al gelikete hebt
        check = post_like(user_id, post_id)
        if check == False:
            return jsonify(success=False)
        # checken of er nieuwe most liked of most dislikete is op account van poster van post die je gelikete hebt
        most_liked_disliked(post_id)
        return jsonify(success=True)


@app.route("/dislike", methods=['GET', 'POST'])
@login_required
def dislike():
    if request.method == "GET":
        user_id = session['user_id']
        post_id = request.args.get('postid')
        # check of je al gedislikete hebt
        check = post_dislike(user_id, post_id)
        if check == False:
            return jsonify(success=False)
        # checken of er nieuwe most liked of most dislikete is op account van poster van post die je gedislikete hebt
        most_liked_disliked(post_id)
        return jsonify(success=True)


@app.route("/myprofile", methods=['GET', 'POST'])
@login_required
def myprofile():
    # data van eigen profiel ophalen
    user_data = profile_info(session['user_id'])
    username = user_data['user_info']['username']
    most_likes = user_data['user_info']['most_likes']
    most_dislikes = user_data['user_info']['most_dislikes']
    followers = user_data['user_info']['followers']
    # indien gebruiker bio edit
    if request.method == 'POST':
        bio = request.form.get("newbio")
        editbio(session['user_id'], bio)
    # bio inladen
    bio = profile_info(session['user_id'])['user_info']['description']
    # meest gelikete en meeste gedislikete post van profiel ophalen
    posts = liked_disliked_profile(session['user_id'])
    return render_template('own_profile.html', username=username, most_likes=most_likes, most_dislikes=most_dislikes, errormessage=None, followers=followers, bio=bio, posts=posts)


@app.route("/profile/<userid>", methods=['GET', 'POST'])
@login_required
def profile(userid):
    # indien link eigen userid bevat, automatisch redirecten naar my profile
    if int(userid) == session['user_id']:
        return redirect(url_for('myprofile'))
    # gebruikers data van profiel ophalen
    user_data = profile_info(userid)
    username = user_data['user_info']['username']
    userID = user_data['user_info']['user_id']
    most_likes = user_data['user_info']['most_likes']
    most_dislikes = user_data['user_info']['most_dislikes']
    followers = user_data['user_info']['followers']
    bio = user_data['user_info']['description']
    # check of user het account al volgt (bepaald of er volg of ontvolg knop verschijnt)
    alreadyfollows = already_follows(session['user_id'], userID)
    # meest gelikete en meest gedislikete post van profiel ophalen
    posts = liked_disliked_profile(int(userid))
    return render_template('profile.html', username=username, userid=userID, most_likes=most_likes, most_dislikes=most_dislikes, errormessage=None, followers=followers, bio=bio, alreadyfollows=alreadyfollows, posts=posts)


@app.route("/follow", methods=['GET', 'POST'])
@login_required
def followuser():
    if request.method == "GET":
        user_id = session['user_id']
        # account om te volgen uit link halen
        tofollow = request.args.get('userid')
        # check of user persoon al volgt
        check = follow(user_id, tofollow)
        if check == False:
            return jsonify(success=False)
        return jsonify(success=True)
