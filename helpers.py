import csv
import urllib.request
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, flash, redirect, render_template, request, session, url_for
# nodig voor most_liked en most_disliked
from operator import itemgetter
# configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


def login_required(f):
    # check of iemand ingelogd is
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def most_liked(user_id):
    # returned voor bepaalde user_id meest gelikete post
    post_likes = db.execute("SELECT total_likes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_likes, key=itemgetter('total_likes'))
    return newlist[0]['post_id']


def most_disliked(user_id):
    # returned voor bepaalde user_id meest gedislikete post
    post_dislikes = db.execute("SELECT total_dislikes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_dislikes, key=itemgetter('total_dislikes'))
    return newlist[0]['post_id']


def register(user_name, password):
    # check of gebruikersnaam al in gebruik is
    match = db.execute("SELECT * FROM users WHERE username = :username", username=user_name)
    if len(match) != 0:
        return False
    # wachtwoord encrypten
    hash = pwd_context.hash(password)
    db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", username=user_name, password=hash)
    userid = db.execute("SELECT user_id FROM users WHERE username = :username", username=user_name)
    return userid[0]['user_id']

def login(user_name, password):
    # mogelijk user_id vergeten
    session.clear()
    # check of username ingevuld is
    if user_name == None:
        return 0
    # check of wachtwoord ingevuld is
    elif password == None:
        return 1
    account = db.execute("SELECT * FROM users WHERE username = :username", username=user_name)
    # check dat username en wachtwoord goed zijn
    if len(account) != 1 or not pwd_context.verify((password), account[0]["password"]):
        return 2
    # inlogde gebruiker onthouden
    session["user_id"] = account[0]["user_id"]
    return True

def post_like(user_id, post_id):
    rating = already_rated(user_id, post_id)
    if rating == False:
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 1", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1 AND likes_today = likes_today + 1")
        return True
    # als user al dislike heeft gegeven op post
    elif rating == 0:
        db.execute("UPDATE likes_dislikes SET like_dislike = 1 WHERE user_id = :user_id AND post_id = :post_id", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1 AND likes_today = likes_today + 1 AND total_dislikes = total_dislikes - 1 AND dislikes_today = dislikes_today - 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al like heeft gegeven op post
    else:
        return False
def post_dislike(user_id, post_id):
    rating = already_rated(user_id, post_id)
    if rating == False:
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 0", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_dislikes = total_dislikes + 1 AND dislikes_today = dislikes_today + 1")
        return True
    # als user al like heeft gegeven op post
    elif rating == 1:
        db.execute("UPDATE likes_dislikes SET like_dislike = 0 WHERE user_id = :user_id AND post_id = :post_id", user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes - 1 AND likes_today = likes_today - 1 AND total_dislikes = total_dislikes + 1 AND dislikes_today = dislikes_today + 1 WHERE post_id = :post_id", post_id=post_id)
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
    return True

def already_follows(user_id, user_id_follows):
    # check of user persoon al volgt
    check = db.execute("SELECT * FROM followers WHERE user_id = :user_id AND follows = :follows", user_id=user_id, follows=user_id_follows)
    if len(check) != 0:
        return True
    return False