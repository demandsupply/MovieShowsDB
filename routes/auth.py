from flask import Blueprint, render_template, request, redirect, session, flash
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()


from helpers.postgreeDbQueries import db

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username were submitted
        if not username:
            flash("Must provide username")
            return redirect("/")

        # Ensure password was submitted
        if not password:
            flash("Must provide password")
            return redirect("/")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = %s", username)
        print(rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("invalid username and/or password")
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")
        # return render_template("search.html", name=rows[0]["username"])


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")   


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function