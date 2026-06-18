from flask import Blueprint, render_template, request
from helpers.postgreeDbQueries import *
from helpers.utils import tmdb_get
import os
from dotenv import load_dotenv

load_dotenv()


compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/comparemovies", methods=["GET", "POST"])
def ajaxmovies():
    if request.method == "GET":
        return render_template("comparemovies.html")
    else:
        q = request.form.get("q")
        print("request form is", q)
        if q:
            compare_movie_data = tmdb_get(f"search/movie?query={q}&page=1")
            # print("compare data: ", compare_data)

            return compare_movie_data
    # return jsonify({"error": "Invalid request"})



@compare_bp.route("/comparetvshows", methods=["GET", "POST"])
def ajaxshows():

    # username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])       

    if request.method == "GET":
        # compare = db.execute("SELECT* FROM compareshows WHERE username = ?", username[0]["username"]) 
        # print(compare)
        return render_template("comparetvshows.html")
    
    else:
        print("request method is post")
        q = request.form.get("q")
        if q:
            compare_show_data = tmdb_get(f"search/tv?query={q}&page=1")

            return compare_show_data
