import csv
import urllib.request
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, flash, redirect, render_template, request, session, url_for
# nodig voor most_liked en most_disliked
from operator import itemgetter
# voor giphy API
import json
# configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def login_required(f):
    # check of iemand ingelogd is
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def most_liked(user_id):
    # returned voor bepaalde user_id meest gelikete post
    post_likes = db.execute("SELECT total_likes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_likes, key=itemgetter('total_likes'), reverse=True)
    return newlist[0]['post_id']


def most_disliked(user_id):
    # returned voor bepaalde user_id meest gedislikete post
    post_dislikes = db.execute("SELECT total_dislikes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_dislikes, key=itemgetter('total_dislikes'), reverse=True)
    return newlist[0]['post_id']


def register_user(user_name, password):
    # check of gebruikersnaam al in gebruik is
    match = db.execute("SELECT * FROM users WHERE username = :username", username=user_name)
    if len(match) != 0:
        return False
    # wachtwoord encrypten
    password_encrypt = pwd_context.hash(password)
    db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", username=user_name, password=password_encrypt)
    userid = db.execute("SELECT user_id FROM users WHERE username = :username", username=user_name)
    return userid[0]['user_id']

def login_user(user_name, password):
    # mogelijk user_id vergeten
    session.clear()
    # check of username ingevuld is
    if user_name == None:
        return -1
    # check of wachtwoord ingevuld is
    elif password == None:
        return -2
    account = db.execute("SELECT * FROM users WHERE username = :username", username=user_name)
    # check dat username en wachtwoord goed zijn
    if len(account) != 1 or not pwd_context.verify((password), account[0]["password"]):
        return -3
    # inlogde gebruiker onthouden
    session["user_id"] = account[0]["user_id"]
    return True

def post_like(user_id, post_id):
    rating = already_rated(user_id, post_id)
    if rating == False:
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 2)", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1, likes_today = likes_today + 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al dislike heeft gegeven op post
    elif rating == 3:
        db.execute("UPDATE likes_dislikes SET like_dislike = 2 WHERE user_id = :user_id AND post_id = :post_id", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1, likes_today = likes_today + 1, total_dislikes = total_dislikes - 1, dislikes_today = dislikes_today - 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al like heeft gegeven op post
    else:
        return False
def post_dislike(user_id, post_id):
    rating = already_rated(user_id, post_id)
    if rating == False:
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 3)", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_dislikes = total_dislikes + 1, dislikes_today = dislikes_today + 1 WHERE post_id =:post_id", post_id=post_id)
        return True
    # als user al like heeft gegeven op post
    elif rating == 2:
        db.execute("UPDATE likes_dislikes SET like_dislike = 3 WHERE user_id = :user_id AND post_id = :post_id", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes - 1, likes_today = likes_today - 1, total_dislikes = total_dislikes + 1, dislikes_today = dislikes_today + 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al dislike heeft gegeven op post
    else:
        return False

def already_rated(user_id, post_id):
    rate = db.execute("SELECT like_dislike FROM likes_dislikes WHERE user_id = :user_id AND post_id = :post_id", user_id=user_id, post_id=post_id)
    if len(rate) == 0:
        return False
    return rate[0]["like_dislike"]


def follow(user_id, user_id_follows):
    # zorgt ervoor dat user persoon volgt
    if already_follows(user_id, user_id_follows) == True:
        return False
    db.execute("INSERT INTO followers (user_id, follows) VALUES(:user_id, :follows)", user_id=user_id, follows=user_id_follows)
    db.execute("UPDATE users SET followers = follwers + 1 WHERE user_id = :user_id_follows", user_id_follows=user_id_follows)
    return True

def already_follows(user_id, user_id_follows):
    # check of user persoon al volgt
    check = db.execute("SELECT * FROM followers WHERE user_id = :user_id AND follows = :follows", user_id=user_id, follows=user_id_follows)
    if len(check) != 0:
        return True
    return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # upload bestand_url met user_id naar database
def post_made(user_id, filename):
    username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]['username']
    db.execute("INSERT INTO posts (username, user_id, file) VALUES(:username, :user_id, :file)", user_id=user_id, file=filename, username=username)

def table_list():
    # maak lijst met alle gebruikers om in tabel weer te geven
    gebruikers = db.execute("SELECT * FROM users")
    return gebruikers

def recent_posts():
    posts = db.execute("SELECT * from posts")
    posts_recent = sorted(posts, key=itemgetter("post_date"), reverse=True)
    posts = posts_recent[:10]
    return posts

def trending_shame(versie):
    posts = db.execute("SELECT * from posts")
    posts_likes = sorted(posts, key=itemgetter('likes_today'), reverse=True)
    posts_dislikes = sorted(posts, key=itemgetter('dislikes_today'), reverse=True)
    posts_likes = posts_likes[:10]
    posts_dislikes = posts_dislikes[:10]
    likes_temp = []
    dislikes_temp = []
    for post in posts_likes:
        if post in posts_dislikes:
            if post['likes_today'] >= post['dislikes_today']:
                likes_temp.append(post)
            else:
                dislikes_temp.append(post)
        else:
            likes_temp.append(post)
    for post in posts_dislikes:
        if post not in posts_likes:
            dislikes_temp.append(post)
    likes_temp = sorted(likes_temp, key=itemgetter('likes_today'), reverse=True)
    dislikes_temp = sorted(dislikes_temp, key=itemgetter('dislikes_today'), reverse=True)
    if versie == 'trending':
        return likes_temp[:5]
    else:
        return dislikes_temp[:5]

def preview_GIF(query):
    zoekterm = query.replace(" ", "+")
    link = "http://api.giphy.com/v1/gifs/search?q=" + zoekterm + "&api_key=az08ZN1d9Ek2JlYs2IVW8f1kvy7dtEDI&limit=5"
    data = json.loads(urllib.request.urlopen(link).read())
    return data