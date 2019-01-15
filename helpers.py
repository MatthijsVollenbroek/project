import csv
import urllib.request
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
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
    # check voor bepaalde user_id meest gelikete post
    post_likes = db.execute("SELECT total_likes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_likes, key=itemgetter('total_likes'))
    return newlist[0]['post_id']


def most_disliked(user_id):
    # check voor bepaalde user_id meest gedislikete post
    post_dislikes = db.execute("SELECT total_dislikes from posts WHERE user_id = :user_id", user_id=user_id)
    newlist = sorted(post_dislikes, key=itemgetter('total_dislikes'))
    return newlist[0]['post_id']