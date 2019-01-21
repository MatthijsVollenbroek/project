from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp


from helpers import *

# configure application
app = Flask(__name__)

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
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        check = login_user(request.form.get("username"), request.form.get("password"))
        # check dat username is ingevuld
        if check == -1:
            return apology("must provide username")

        # check dat wachtwoord is ingevuld
        elif check == -2:
            return redirect(url_for('login'))

        elif check == -3:
            return apology("wachtwoord en username komen niet overeen")
        elif check == True:
            return redirect(url_for('homepage'))
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username to register")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password to register")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide matching passwords")

        check = register_user(request.form.get("username"), request.form.get("password"))
        if check == False:
            return apology("gebruikersnaam al in gebruik")
        else:
            session["user_id"] = check
            return redirect(url_for('homepage'))

    else:
        return render_template("register.html")


@app.route("homepage_recent", methods=["GET", "POST"])
def homepage_recent():
    return render_template("homepage_recent.html")

@app.route("homepage_shame", methods=["GET", "POST"])
def homepage_shame():
    return render_template("homepage_shame.html")

@app.route("homepage_trending", methods=["GET", "POST"])
def homepage_trending():
    return render_template("homepage_trending.html")

@app.route("search", methods=["GET", "POST"])
def search():
    return render_template("search.html")