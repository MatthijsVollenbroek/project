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
#  CS50 Library configureren om SQLite database te gebruiken
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


def most_liked_disliked(post_id):
    # na liken of disliken wordt most_liked en most_disliked van poster geupdate
    user_id = db.execute("SELECT user_id FROM posts WHERE post_id = :post_id", post_id=post_id)[0]['user_id']
    post_likes = db.execute("SELECT total_likes from posts WHERE user_id = :user_id", user_id=user_id)
    # most gelikete post pakken
    list_likes = sorted(post_likes, key=itemgetter('total_likes'), reverse=True)[:1]
    post_dislikes = db.execute("SELECT total_dislikes from posts WHERE user_id = :user_id", user_id=user_id)
    # meest gedislikete post pakken
    list_dislikes = sorted(post_dislikes, key=itemgetter('total_dislikes'), reverse=True)[:1]
    if len(list_likes) != 0:
        db.execute("UPDATE users SET most_likes = :most_likes WHERE user_id=:user_id",
                   most_likes=list_likes[0]['total_likes'], user_id=user_id)
    if len(list_dislikes) != 0:
        db.execute("UPDATE users SET most_dislikes = :most_dislikes WHERE user_id=:user_id",
                   most_dislikes=list_dislikes[0]['total_dislikes'], user_id=user_id)
    return True


def register_user(user_name, password):
    # check of gebruikersnaam al in gebruik is
    match = db.execute("SELECT * FROM users WHERE username = :username", username=user_name)
    if len(match) != 0:
        return False
    # wachtwoord encrypten
    password_encrypt = pwd_context.hash(password)
    db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", username=user_name, password=password_encrypt)
    # userid meegeven om user na registreren automatisch in te loggen
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
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 2)",
                   user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al dislike heeft gegeven op post
    elif rating == 3:
        db.execute("UPDATE likes_dislikes SET like_dislike = 2 WHERE user_id = :user_id AND post_id = :post_id",
                   user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes + 1, total_dislikes = total_dislikes - 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al like heeft gegeven op post
    else:
        return False


def post_dislike(user_id, post_id):
    rating = already_rated(user_id, post_id)
    # als user nog geen like of dislike heeft gegeven
    if rating == False:
        db.execute("INSERT INTO likes_dislikes (user_id, post_id, like_dislike) VALUES(:user_id, :post_id, 3)",
                   user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_dislikes = total_dislikes + 1 WHERE post_id =:post_id", post_id=post_id)
        return True
    # als user al like heeft gegeven op post
    elif rating == 2:
        db.execute("UPDATE likes_dislikes SET like_dislike = 3 WHERE user_id = :user_id AND post_id = :post_id",
                   user_id=user_id, post_id=post_id)
        db.execute("UPDATE posts SET total_likes = total_likes - 1, total_dislikes = total_dislikes + 1 WHERE post_id = :post_id", post_id=post_id)
        return True
    # als user al dislike heeft gegeven op post
    else:
        return False


def already_rated(user_id, post_id):
    # check of user al deze post gelikete of gedislikete heeft
    rate = db.execute("SELECT like_dislike FROM likes_dislikes WHERE user_id = :user_id AND post_id = :post_id",
                      user_id=user_id, post_id=post_id)
    if len(rate) == 0:
        return False
    return rate[0]["like_dislike"]


def follow(user_id, user_id_follows):
    # als user persoon al volgt, ontvolgen
    if already_follows(user_id, user_id_follows) == True:
        db.execute("DELETE FROM followers WHERE user_id = :user_id AND follows = :follows", user_id=user_id, follows=user_id_follows)
        db.execute("UPDATE users SET followers = followers - 1 WHERE user_id = :user_id_follows", user_id_follows=user_id_follows)
        return False
    # zo niet dan volgen
    db.execute("INSERT INTO followers (user_id, follows) VALUES(:user_id, :follows)", user_id=user_id, follows=user_id_follows)
    db.execute("UPDATE users SET followers = followers + 1 WHERE user_id = :user_id_follows", user_id_follows=user_id_follows)
    return True


def already_follows(user_id, user_id_follows):
    # check of user persoon al volgt
    check = db.execute("SELECT * FROM followers WHERE user_id = :user_id AND follows = :follows",
                       user_id=user_id, follows=user_id_follows)
    if len(check) != 0:
        return True
    return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def post_made(user_id, filename, description):
    # upload bestand_url met user_id naar database
    username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]['username']
    if description == None:
        description = " "
        db.execute("INSERT INTO posts (username, user_id, file, description) VALUES(:username, :user_id, :file, :description)",
                   user_id=user_id, file=filename, username=username, description=description)


def table_list():
    # maak lijst met alle gebruikers om in tabel weer te geven
    gebruikers = db.execute("SELECT * FROM users")
    return gebruikers


def recent_posts():
    posts = db.execute("SELECT * from posts")
    posts_recent = sorted(posts, key=itemgetter("post_date"), reverse=True)
    # de twintig meest recente posts inladen
    posts = posts_recent[:20]
    return posts


def trending_shame(versie):
    posts = db.execute("SELECT * from posts")
    posts_likes = sorted(posts, key=itemgetter('total_likes'), reverse=True)
    posts_dislikes = sorted(posts, key=itemgetter('total_dislikes'), reverse=True)
    # de tien meest gelikete en meest gedislikete posts
    posts_likes = posts_likes[:10]
    posts_dislikes = posts_dislikes[:10]
    # kandidaatlijsten opstellen
    likes_temp = []
    dislikes_temp = []
    for post in posts_likes:
        # als post in zowel meest gelikete als meest gedislikete zit, aantal likes en dislikes vergelijken
        if post in posts_dislikes:
            # meer likes dan dislikes betekent dat hij kandidaat is voor hall of fame
            if post['total_likes'] >= post['total_dislikes']:
                likes_temp.append(post)
            # meer dislikes maakt post kandidaat voor wall of shame
            else:
                dislikes_temp.append(post)
        else:
            likes_temp.append(post)
    for post in posts_dislikes:
        if post not in posts_likes:
            dislikes_temp.append(post)
    # kandidaten op juiste volgorde zetten van meer likes/dislikes naar minder likes/dislikes
    likes_temp = sorted(likes_temp, key=itemgetter('total_likes'), reverse=True)
    dislikes_temp = sorted(dislikes_temp, key=itemgetter('total_dislikes'), reverse=True)
    # als functie aangeroepen werd voor hall of fame dan top 5 van like kandidaten returnen
    if versie == 'trending':
        return likes_temp[:5]
    # anders meest gedislikete voor wall of shame
    else:
        return dislikes_temp[:5]


def preview_GIF(query):
    # zoekterm spaties omzetten in bruikbare query voor giphy
    zoekterm = query.replace(" ", "+")
    link = "http://api.giphy.com/v1/gifs/search?q=" + zoekterm + "&api_key=az08ZN1d9Ek2JlYs2IVW8f1kvy7dtEDI&limit=5"
    # json bestand laden
    data = json.loads(urllib.request.urlopen(link).read())
    return data


def userIDtoName(user_id):
    # userid omzettetten naar username
    username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=user_id)[0]['username']
    return username


def recent_following(user_id):
    following = db.execute("SELECT follows FROM followers WHERE user_id = :user_id", user_id=user_id)
    follows = []
    for follow in range(len(following)):
        follows.append(following[follow]['follows'])
    posts = []
    # voor de volgers de laatste posts inladen
    for follow in follows:
        follow_post = db.execute("SELECT * FROM posts WHERE user_id = :user_id", user_id=follow)
        posts.append(follow_post)
    # all posts in één grote lijst plaatsen in plaats van lijsten in lijsten
    all_posts = []
    for uploader in posts:
        for post in uploader:
            all_posts.append(post)
    # posts op volgorde van upload datum en tijd zetten
    all_posts_sorted = sorted(all_posts, key=itemgetter("post_date"), reverse=True)
    # de 20 meest recente posts van de mensen die de user volgt worden gereturned
    return all_posts_sorted[:20]


def profile_info(user_id):
    user_data = {}
    # dictionary opdelen in informatie over degene met die userid en informatie over zijn of haar posts
    user_data['user_info'] = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=user_id)[0]
    user_data['user_posts'] = db.execute("SELECT * FROM posts WHERE user_id = :user_id", user_id=user_id)
    return user_data


def followers(user_id):
    # userids ophalen van mensen die de user volgt
    follow_dict = db.execute("SELECT follows FROM followers WHERE user_id = :user_id", user_id=user_id)
    # lijst met enkel de userids
    follow_list = []
    for follow in range(len(follow_dict)):
        follow_list.append(follow_dict[follow]['follows'])
    # lijst met alle benodigde info over deze mensen
    follow_list_usable = []
    for follow in follow_list:
        userinfo = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=follow)
        follow_list_usable.append(userinfo)
    return follow_list_usable


def editbio(user_id, bio):
    # bio editen door user
    db.execute("UPDATE users SET description = :description WHERE user_id = :user_id", description=bio, user_id=user_id)
    return True


def liked_disliked_profile(profileID):
    # de posts met de meeste likes en meeste dislikes ophalen (kan dezelfde post zijn)
    post_likes = db.execute("SELECT * from posts WHERE user_id = :user_id", user_id=profileID)
    list_likes = sorted(post_likes, key=itemgetter('total_likes'), reverse=True)[:1]
    post_dislikes = db.execute("SELECT * from posts WHERE user_id = :user_id", user_id=profileID)
    list_dislikes = sorted(post_dislikes, key=itemgetter('total_dislikes'), reverse=True)[:1]
    posts = []
    # indien gebruiker minimaal 1 post heeft word de volgende code uitgevoerd
    if len(post_likes) != 0:
        posts.append(list_likes[0])
        posts.append(list_dislikes[0])
    # als de gebruiker geen posts heeft een lege lijst returnen om errors te voorkomen met jinja
    return posts


def postid(userid, filename):
    # post_id ophalen bij userid en filename
    post_id = db.execute("SELECT post_id FROM posts WHERE user_id =:user_id AND file = :file", user_id=userid, file=filename)
    return post_id


def postnameUpdate(postid, filename):
    # filename in database updaten met correct path naam
    db.execute("UPDATE posts SET file = :file WHERE post_id=:post_id", file=filename, post_id=postid)