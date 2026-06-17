import asyncio
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, abort
from helpers.utils import tmdb_get, format_runtime
from helpers.postgreeDbQueries import *
import requests
import json
from helpers.utils import headers
import os
from dotenv import load_dotenv

load_dotenv()


user_bp = Blueprint("user", __name__)


environment = os.getenv("FLASK_ENV", "development")



@user_bp.route("/myarea", methods=["GET", "POST"])
async def myarea():
    if request.method == "POST":
        print("request method is post")

        usernameToFix = db.execute("SELECT username FROM users WHERE id = %s", session["user_id"])
        username = usernameToFix[0]["username"]

        id_favorite = request.form.get("movie_id_favorite")
        if id_favorite:
            db.execute("DELETE FROM favoriteswatchlist WHERE item_id = %s AND category = 'favorite' AND username = %s", id_favorite, username) 

        id_watchlist = request.form.get("movie_id_watchlist")
        if id_watchlist:
            db.execute("DELETE FROM favoriteswatchlist WHERE item_id = %s AND category = 'watchlist' AND username = %s", id_watchlist, username) 

        id_favorite_episode = request.form.get("episode_id_favorite")
        if id_favorite_episode:
            db.execute("DELETE FROM usershows WHERE episode_id = %s AND username = %s", id_favorite_episode, username) 

        return redirect (url_for("user.myarea"))
    else:
        usernameToFix = db.execute("SELECT username FROM users WHERE id = %s", session["user_id"])
        if not usernameToFix:
            return redirect(url_for("auth.login"))
            
        username = usernameToFix[0]["username"]       
        item_list = db.execute("SElECT * FROM favoriteswatchlist WHERE username = %s", username)
        episode_list = db.execute("SElECT * FROM usershows WHERE username = %s", username)
        episodes_ratings_list = db.execute("SElECT * FROM compareshows WHERE username = %s", username)
        print(f"favorites are {item_list}")
        print(f"favorite episodes are {episode_list}")

        # old code to get my area data
        # for item in item_list:
        #     q = item["item_id"]
        #     if (item["type"] == "movie"):
        #         url = f"https://api.themoviedb.org/3/movie/{q}"
        #         response = requests.get(url, headers=headers)
        #         movie_data = json.loads(response.text)

        #         if(item["category"] == "favorite"):
        #             favorites_list.append(movie_data)
        #         else:
        #             watchlist_list.append(movie_data)

        #     elif(item["type"] == "tv-show"):
        #         url = f"https://api.themoviedb.org/3/tv/{q}"
        #         response = requests.get(url, headers=headers)
        #         movie_data = json.loads(response.text)

        #         if(item["category"] == "favorite"):
        #             favorites_list.append(movie_data)
        #         else:
        #             watchlist_list.append(movie_data)

                
        # zip_list_favorites = zip(item_list, favorites_list) 
        # zip_list_watchlist = zip(item_list, watchlist_list) 

        # for episode in episode_list:
        #     series_id = episode["show_id"]
        #     season_number = episode["season_number"]
        #     episode_number = episode["episode_number"]
        #     url = f"https://api.themoviedb.org/3/tv/{series_id}/season/{season_number}/episode/{episode_number}"
        #     response = requests.get(url, headers=headers)
        #     episode_data = json.loads(response.text)
        #     print(episode_data)
        #     favorite_episodes_list.append(episode_data)
            
        # zip_list_episodes = zip(episode_list, favorite_episodes_list)
        # if item_list:
        #     print("movie exist")
        #     button_favorites = "remove from favorites"
        # else:
        #     print("movie does not exist")
        #     button_favorites = "add to favorites"


        # return render_template("myarea.html", button_favorites=button_favorites, users=username, favorites=item_list, favorites_list=favorites_list, watchlist_list=watchlist_list, zip_list_favorites=zip_list_favorites, zip_list_watchlist=zip_list_watchlist, favorite_episodes_list=favorite_episodes_list, zip_list_episodes=zip_list_episodes, episodes_ratings_list=episodes_ratings_list, environment=environment)
    

        # parallelize fetching details for all items and episodes
        item_tasks = []
        for item in item_list:
            endpoint = f"movie/{item['item_id']}" if item["type"] == "movie" else f"tv/{item['item_id']}"
            item_tasks.append(asyncio.to_thread(tmdb_get, endpoint))
        
        episode_tasks = []
        for ep in episode_list:
            endpoint = f"tv/{ep['show_id']}/season/{ep['season_number']}/episode/{ep['episode_number']}"
            episode_tasks.append(asyncio.to_thread(tmdb_get, endpoint))
        
        # wait for all TMDB data
        all_results = await asyncio.gather(*(item_tasks + episode_tasks))
        
        # Split obtained results to items_data and episodes_data
        items_data = all_results[:len(item_tasks)]
        episodes_data = all_results[len(item_tasks):]

        favorites_list = []
        watchlist_list = []
        
        # Sort items into favorites and watchlist
        for i, item in enumerate(item_list):
            data = items_data[i]
            if not data: continue
            if item["category"] == "favorite":
                favorites_list.append(data)
            else:
                watchlist_list.append(data)

        # Filter out failed episode fetches
        favorite_episodes_list = [ep for ep in episodes_data if ep]
            
        zip_list_favorites = zip([i for i in item_list if i["category"] == "favorite"], favorites_list) 
        zip_list_watchlist = zip([i for i in item_list if i["category"] == "watchlist"], watchlist_list) 
        zip_list_episodes = zip(episode_list, favorite_episodes_list)

        button_favorites = "- Favorites" if item_list else "+ Favorites"

        return render_template("myarea.html", button_favorites=button_favorites, users=username, favorites=item_list, favorites_list=favorites_list, watchlist_list=watchlist_list, zip_list_favorites=zip_list_favorites, zip_list_watchlist=zip_list_watchlist, favorite_episodes_list=favorite_episodes_list, zip_list_episodes=zip_list_episodes, episodes_ratings_list=episodes_ratings_list, environment=environment)
    

@user_bp.route("/data", methods=["GET", "POST"])
def data():

    if not current_app.config.get("SHOW_DATA_PAGE"):
        abort(404)

    if request.method == "GET":
        favorites_list = []
        favorite_episodes_list = []

        users = db.execute("SElECT * FROM users")
        item_list = db.execute("SElECT * FROM favoriteswatchlist")
        episode_list = db.execute("SElECT * FROM usershows")
        episodes_ratings_list = db.execute("SElECT * FROM compareshows")
        print(f"favorites are {item_list}")
        print(f"favorite episodes are {episode_list}")

        for item in item_list:
            q = item["item_id"]
            if (item["type"] == "movie"):
                movie_data = tmdb_get(f"movie/{q}")
                favorites_list.append(movie_data)

            elif(item["type"] == "tv-show"):
                movie_data = tmdb_get(f"tv/{q}")
                favorites_list.append(movie_data)

        zip_list = zip(item_list, favorites_list) 

        for episode in episode_list:
            series_id = episode["show_id"]
            season_number = episode["season_number"]
            episode_number = episode["episode_number"]

            episode_data = tmdb_get(f"tv/{series_id}/season/{season_number}/episode/{episode_number}")
            favorite_episodes_list.append(episode_data)
            
        zip_list_episodes = zip(episode_list, favorite_episodes_list)

        return render_template ("data.html", 
                                users=users, 
                                favorites=item_list, 
                                favorites_list=favorites_list, 
                                zip_list=zip_list, 
                                favorite_episodes_list=favorite_episodes_list, 
                                zip_list_episodes=zip_list_episodes, 
                                episodes_ratings_list=episodes_ratings_list
                                )
    
    else:
        remove_id = request.form.get("id")
        db.execute("DELETE FROM users WHERE id = %s", remove_id)
        return redirect ("/data")

    


