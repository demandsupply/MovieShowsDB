import asyncio
import os
from flask import Flask, redirect, render_template, request, jsonify, session, flash, url_for, abort
from cs50 import SQL
from flask_session import Session
import requests
import json
import random
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import ast
from helpers.utils import headers, tmdb_get, format_runtime
from helpers.postgreeDbQueries import (
    db,
    is_favorite, add_favorite, remove_favorite,
    get_username,
    is_in_watchlist, add_to_watchlist, remove_from_watchlist,
    is_favorite_episode, add_favorite_episode, remove_favorite_episode
)
from urllib.parse import urlencode

from routes.movies import movies_bp
from routes.shows import shows_bp
from routes.auth import auth_bp, login_required
from routes.topRateds import top_rateds_bp
from routes.user import user_bp
from routes.compare import compare_bp

from app_config import DevelopmentConfig, ProductionConfig
from dotenv import load_dotenv
from helpers.utils import getCurrentYEar

load_dotenv()



# Configure application
app = Flask(__name__)

env = os.getenv("FLASK_ENV", "development")

if env == "production":
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


app.register_blueprint(movies_bp)
app.register_blueprint(shows_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(top_rateds_bp)
app.register_blueprint(user_bp)
app.register_blueprint(compare_bp)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        errors = {}
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm", "")

        # Check if username is blank
        if not username:
            errors["username"] = "Username is required"
        else:
            # Check if the chosen username is already used
            temporary = db.execute("SELECT username FROM users WHERE username = %s LIMIT 1", username)
            if temporary:
                errors["usernamexists"] = "Username already exists"
                
        # Password validation
        if not password:
            errors["password"] = "Password is required"
        elif len(password) < 8:
            errors["passwordlength"] = "Password must be at least 8 chars"
        elif password.isalpha() or password.isdigit():
            errors["passwordchars"] = "Password must contain at least one character and one number"

        # Check if password matches
        if not confirmation:
             errors["passwordwrong"] = "Please confirm your password"
        elif password != confirmation:
            errors["passwordwrong"] = "Password is not the same!"

        if errors:
            return render_template("register.html", errors=errors, username=username)

        # Insert the new user into users and store a hash of its password
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users(username, hash) VALUES(%s, %s)", username, hash)

        return redirect("/?registered=true")
    
    return render_template("register.html", errors={}, username="")
    
    






#############################   INDEX    ############################

@app.route("/", methods=["GET", "POST"])
async def index():
    if request.method == "GET":
        # fetch data using function from helpers -> more efficient
        # use asyncio to parallelize popular movies and shows fetch
        movies_task = asyncio.to_thread(tmdb_get, "movie/popular")
        shows_task = asyncio.to_thread(tmdb_get, "tv/popular")


        # get random movies using "discover/movie?" endpoint -> lighter and more efficient way
        def get_random_movie():
            starting_release_year = 1950
            random_year = random.randint(starting_release_year, getCurrentYEar())

            params = {
                "adult": "false",
                "primary_release_year": random_year
            }

            data = tmdb_get("discover/movie?" + urlencode(params))

            # print(f"current yeart: {getCurrentYEar()}")
            # print(f"random_year: {random_year}")
            # print(f"movie data: {data}")


            if not data or "results" not in data:
                return None
            
            return random.choice(data["results"])
        
        def get_random_show():
            starting_release_year = 1980
            random_year = random.randint(starting_release_year, getCurrentYEar())

            params = {
                "adult": "false",
                "first_air_date_year": random_year
            }

            data = tmdb_get("discover/tv?" + urlencode(params))
            
            # print(f"current yeart: {getCurrentYEar()}")
            # print(f"random_year: {random_year}")
            # print(f"show data: {data}")


            if not data or "results" not in data:
                return None
            
            return random.choice(data["results"])

        # original code to get random shows 
        # while True:
        #     random_show_id = random.randint(1, 400000)
        #     url_random_show = f"https://api.themoviedb.org/3/tv/{random_show_id}"
        #     response_random_show = requests.get(url_random_show, headers=headers)
        #     if response_random_show:
        #         random_show_data = json.loads(response_random_show.text)
        #         if random_show_data["adult"] != True:
        #             break
        #         else:
        #             print(f"Adult content, load another show")
        #     else:
        #         print(f"Show does not exist, load another ID")   

        results = await asyncio.gather(movies_task, shows_task)
        
        popular_movies = results[0]
        popular_shows = results[1]

        popular_movie_list = popular_movies["results"] if popular_movies else []
        popular_show_list = popular_shows["results"] if popular_shows else []

        # print(f"popular_show_list: {popular_show_list}")   
        
        return render_template("index.html", popular_movie_list=popular_movie_list, popular_show_list=popular_show_list, random_movie=get_random_movie(), random_show=get_random_show())
    else:
        q = request.form.get("q")
        if q:
            url = f"https://api.themoviedb.org/3/search/multi?query={q}&page=1"

            print(url)
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                shows = json.loads(response.text)
                print(shows)
                return jsonify(shows)




@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get("query")
        if not query:
            flash("Insert a search")
            return redirect("/search")

        params = urlencode({"query": query})
        data = tmdb_get("search/multi?" + params)

        results = data.get("results", []) if data else []

        return render_template("search.html", results=results, query=query)

    return render_template("search.html", results=None)







@app.route("/showratings", methods=["GET", "POST"])
def show_ratings():
    if request.method == "POST":
        print("request method is post")
        compare = []
        seasons_episodes_average_vote = []
        id = request.form.get("q")
        url = f"https://api.themoviedb.org/3/tv/{id}"
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            show_datas = json.loads(response.text)
            # print(movie_datas)
        show_title = show_datas["name"]


        # print(f"THIS IS SHOW DATAS {show_datas['name']}")
        number_of_seasons = show_datas["number_of_seasons"]
        print(f"There are {number_of_seasons} seasons")


        episodes_data = []

        counter = 0

        for season in range(number_of_seasons + 1):
            if season == 0:
                continue
            else:
                url_season_data = f"https://api.themoviedb.org/3/tv/{id}/season/{season}"
                response_season_data = requests.get(url_season_data, headers=headers)
                season_data = json.loads(response_season_data.text)
                print(season_data["name"])     
                episode_average_vote = []


                for episode in season_data["episodes"]:
                    counter = counter + 1
                    episodes_data.append(episode)
                    episode_average_vote.append(episode['vote_average'])

                # print(season_data["episodes"][0]["episode_number"])
                print(episode_average_vote)  
            seasons_episodes_average_vote.append(episode_average_vote)                      
            print(episode_average_vote)
            print(f"ALL VOTES FOR {show_title} ARE {seasons_episodes_average_vote}")
        return seasons_episodes_average_vote




@app.route("/test", methods=["GET"])
def test():
    if request.method == "GET":
        # response_list = []
        # url = f"https://api.themoviedb.org/3/discover/movie"

        # response = requests.get(url, headers=headers)
        # movie_data = json.loads(response.text)
        # response_list.append(movie_data)
        # print(response_list)
        
        while True:
            random_movie_id = random.randint(1, 1200000)
            url_random_movie = f"https://api.themoviedb.org/3/movie/{random_movie_id}"
            response_random_movie = requests.get(url_random_movie, headers=headers)
            if response_random_movie:
                random_movie_data = json.loads(response_random_movie.text)
                if random_movie_data["adult"] != True:
                    print(f"ADULT CONTENT = {random_movie_data["adult"]}")
                    break
                else:
                    print(f"ADULT CONTENT = {random_movie_data}")
            else:
                print(f"URL NOT existent = {url_random_movie}")
            
        print(f"URL EXIT = {response_random_movie}")

        return render_template("test.html", movie=random_movie_data)
