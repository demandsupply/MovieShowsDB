import asyncio
from flask import Blueprint, render_template, request, redirect, url_for, flash
from helpers.postgreeDbQueries import *
from helpers.utils import tmdb_get, format_runtime
from flask import session
# from app import login_required
import os
from dotenv import load_dotenv

load_dotenv()

movies_bp = Blueprint("movies", __name__)

db = SQL(os.getenv("DATABASE_URL"))



@movies_bp.route("/movie/<id>", methods = ["GET", "POST"])
async def movie(id):
    user_id = session.get("user_id")
    username = get_username(session["user_id"]) if user_id else "guest"

    # Parallelize movie data and images fetch
    movie_task = asyncio.to_thread(tmdb_get, f"movie/{id}")
    images_task = asyncio.to_thread(tmdb_get, f"movie/{id}/images?language=en")

    results = await asyncio.gather(movie_task, images_task)
    movie_datas = results[0]
    imgMovie_datas = results[1]

    if not movie_datas:
        return "Movie not found", 404
    
    print(f"movie id is {id}.\nIts data are {movie_datas}")
    
    movie_datas["runtime_formatted"] = format_runtime(movie_datas.get("runtime"))

    if request.method == ("GET"):
        print("request method is get")

        if user_id:
            status = get_item_status(username, id, "movie")
            button_favorites = "- Favorites" if status["is_favorite"] else "+ Favorites"
            button_watchlist = "- Watchlist" if status["is_in_watchlist"] else "+ Watchlist"

            return render_template ("movie.html", imgMovie_datas = imgMovie_datas,  movie_datas=movie_datas, button_favorites=button_favorites, button_watchlist=button_watchlist)
        else:
            return render_template ("movie.html", imgMovie_datas = imgMovie_datas,  movie_datas=movie_datas)

    else:
        user_id = session.get("user_id")
        if user_id: 
            print("request method is post")

            favorite_action = request.form.get('favorite')
            watchlist_action = request.form.get('watchlist')

            if favorite_action == "+ Favorites":
                add_favorite(username, id, "movie", movie_datas["title"])
            elif favorite_action == "- Favorites":
                remove_favorite(username, id)

            if watchlist_action == "+ Watchlist":
                add_to_watchlist(username, id, "movie", movie_datas["title"])
            elif watchlist_action == "- Watchlist":
                remove_from_watchlist(username, id)


            return redirect(url_for("movies.movie", id=id))
        
