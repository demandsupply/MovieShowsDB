import asyncio
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from helpers.postgreeDbQueries import *
from helpers.utils import tmdb_get, format_runtime
# from helpers.decorators import login_required
from cs50 import SQL
import ast
import os
from dotenv import load_dotenv

load_dotenv()

shows_bp = Blueprint("shows", __name__)

db = SQL(os.getenv("DATABASE_URL"))




@shows_bp.route("/tvshow/<id>", methods = ["GET", "POST"])
async def tvshow_id(id):
    print(f"id is {id}")

    user_id = session.get("user_id")
    username = get_username(session["user_id"]) if user_id else "guest"


    compare = []
    
    # Parallelize initial TMDB calls
    img_task = asyncio.to_thread(tmdb_get, f"tv/{id}/images?language=en")
    details_task = asyncio.to_thread(tmdb_get, f"tv/{id}")
    
    results = await asyncio.gather(img_task, details_task)
    imgShow_datas = results[0]
    show_datas = results[1]

    print("SHOW DATAS", show_datas)
    if not show_datas:
        flash("TV show not found")
        return redirect("/")

    show_title = show_datas["name"]
    number_of_seasons = show_datas["number_of_seasons"]

    status = get_item_status(username, id, "tv-show")
    button_favorites = "remove from favorites" if status["is_favorite"] else "add to favorites"
    button_watchlist = "remove from watchlist" if status["is_in_watchlist"] else "add to watchlist"


    # FUNCTION TO GET ALL EPISODES DATA
    async def load_all_episodes():
        all_episodes = []
        favorite_buttons = []
        season_ratings = []
        counter = 0
        
        # fetch all favorite episode IDs of the user and show in one query
        favorite_episode_ids = set()
        if user_id:
            fav_rows = db.execute(
                "SELECT episode_id FROM usershows WHERE username = %s AND show_id = %s",
                username, id
            )
            favorite_episode_ids = {row["episode_id"] for row in fav_rows}

        # Fetch all seasons in parallel
        tasks = [asyncio.to_thread(tmdb_get, f"tv/{id}/season/{s}") for s in range(1, number_of_seasons + 1)]
        seasons_results = await asyncio.gather(*tasks)

        for season_data in seasons_results:
            if not season_data:
                continue
            
            ratings = []

            for episode in season_data["episodes"]:
                all_episodes.append(episode)
                counter += 1
                ratings.append(episode["vote_average"])
                is_fav = episode["id"] in favorite_episode_ids
                favorite_buttons.append("Unfavorite" if is_fav else "Add Favorite")
            season_ratings.append(ratings)

        return all_episodes, favorite_buttons, season_ratings, counter
    
    # OLD BLOCK TO GET ALL EPISODES DATA (SLOWER)
    # episodes_data = []
    # sort = " | sort(attribute = 'vote_average', reverse=true)"

    # counter = 0

    # for season in range(number_of_seasons + 1):
    #     if season == 0:
    #         continue
    #     else:
    #         season_data = tmdb_get(f"tv/{id}/season/{season}")
    #         print(season_data["name"])     
    #         episode_average_vote = []


    #         for episode in season_data["episodes"]:
    #             counter = counter + 1
    #             episodes_data.append(episode)
    #             episode_average_vote.append(episode['vote_average'])

    #         # print(season_data["episodes"][0]["episode_number"])
    #         print(episode_average_vote)  
    #     seasons_episodes_average_vote.append(episode_average_vote)                      
    #     print(episode_average_vote)
    # session["ratings"] = seasons_episodes_average_vote
    # session["numberEpisodes"] = counter
    # print(f"THEREARE {counter} EPISODES")
    # for episode in episodes_data:
    #     print(f"season: {episode['season_number']}, ", end="")
    #     print(f"episode: {episode['episode_number']}, ", end="")
    #     print(f"vote average: {episode['vote_average']}")
    #     # print(episode)


    # OLD GET METHOD (SLOWER)
    # if request.method == ("GET"):
    #     print("request method is get")

    #     episodes_data = []
    #     sort = " | sort(attribute = 'vote_average', reverse=true)"

    #     counter = 0

    #     for season in range(number_of_seasons + 1):
    #         if season == 0:
    #             continue
    #         else:
    #             url_season_data = f"https://api.themoviedb.org/3/tv/{id}/season/{season}"
    #             response_season_data = requests.get(url_season_data, headers=headers)
    #             season_data = json.loads(response_season_data.text)
    #             print(season_data["name"])     


    #             for episode in season_data["episodes"]:
    #                 counter = counter + 1
    #                 print(episode["id"])
    #                 episodes_data.append(episode)
    #                 favorite_episodes = db.execute("SELECT episode_id, username FROM usershows WHERE episode_id = %s AND username = %s", episode["id"], username) 

    #                 if favorite_episodes:
    #                     print("episode exist")
    #                     button_favorite_episodes.append("Unfavorite")
    #                     print(button_favorite_episodes)
    #                 else:
    #                     print("episode does not exist")
    #                     button_favorite_episodes.append("Add Favorite")
    #                     print(button_favorite_episodes)
    #                 # print(f"episode number {episode_number}")
    #             # print(season_data["episodes"][0]["episode_number"])
            

    #     return render_template ("tvshow.html", button_favorite_episodes=button_favorite_episodes, button_favorites=button_favorites, button_watchlist=button_watchlist, number_of_seasons=number_of_seasons, show_datas=show_datas, episodes_data=episodes_data, imgShow_datas=imgShow_datas)

    if request.method == "GET":
        eps, favorite_buttons, ratings, total = await load_all_episodes()
        session["ratings"] = ratings
        session["numberEpisodes"] = total

        return render_template(
            "tvshow.html",
            show_datas=show_datas,
            imgShow_datas=imgShow_datas,
            number_of_seasons=number_of_seasons,
            episodes_data=eps,
            button_favorite_episodes=favorite_buttons,
            button_favorites=button_favorites,
            button_watchlist=button_watchlist
        )
    
    else:
        if user_id: 
            favorite_action = request.form.get("favorite")
            
            if favorite_action == "add to favorites":
                add_favorite(username, id, "tv-show", show_datas["name"])
            elif favorite_action == "remove from favorites":
                remove_favorite(username, id)

            watchlist_action = request.form.get("watchlist")
            if watchlist_action == "add to watchlist":
                add_to_watchlist(username, id, "tv-show", show_datas["name"])
            elif watchlist_action == "remove from watchlist":
                remove_from_watchlist(username, id)
                            
            if request.form.get('favorite_episodes'): 
                episode_data_str = request.form.get('favorite_episodes') 
                print(f"EPISODE STRING DATAS ARE: {episode_data_str}")
                episode_to_db = ast.literal_eval(episode_data_str)
                print(f"IIIIIIIDDDDDD IS ONE {episode_to_db['id']}") 
                
                check_episode_on_db_list = db.execute("SELECT episode_id FROM usershows where episode_id = %s AND username = %s", episode_to_db["id"], username)
                if check_episode_on_db_list:
                    print("episode saved on favorite episodes, I'll remove it")
                    remove_favorite_episode(username, episode_to_db["id"])
                else:
                    print("episode is not saved on favorite episodes, I'll add it")
                    add_favorite_episode(
                        username, show_title, id,
                        episode_to_db["season_number"], episode_to_db["episode_number"],
                        episode_to_db["name"], episode_to_db["id"]
                    )
            
            if request.form.get('compare'):
                # only 'ratings' values are needed
                _, _, ratings, _ = await load_all_episodes()
                list_to_string = str(ratings)
                check_compare = db.execute("SELECT id FROM compareshows WHERE username = %s AND show_title = %s", username, show_title)
                
                if not check_compare:
                    db.execute("INSERT INTO compareshows (username, show_title, episodes_ratings) VALUES (%s, %s, %s)", username, show_title, list_to_string)
                return redirect(url_for("compare.ajaxshows"))

            return redirect(url_for("shows.tvshow_id", id=id))
        return redirect(url_for("auth.login"))

@shows_bp.route("/tvshow/tv/<id>/season/<season>/episode/<seasonEpisode>", methods = ["GET", "POST"])
async def episode(id, season, seasonEpisode):
    print(f"id {id}, season{season}, seasonEpisode{seasonEpisode}")

    user_id = session.get("user_id")
    username = get_username(session["user_id"]) if user_id else "guest"


    show_datas = tmdb_get(f"tv/{id}")   
    
    if not show_datas:
        flash("TV show not found")
        return redirect("/")

    show_title = show_datas["name"]
    # print(f"THIS IS SHOW DATAS {show_datas['name']}")
    number_of_seasons = show_datas["number_of_seasons"]
    print(f"There are {number_of_seasons} seasons")  

    episode_data = tmdb_get(f"tv/{id}/season/{season}/episode/{seasonEpisode}")

    if not episode_data:
        flash("Episode data not found")
        return redirect("/")

    print(episode_data)
    episode_id = episode_data["id"] 

    is_favorite = is_favorite_episode(username, episode_id)

    button_favorites = "remove from favorite episodes" if is_favorite else "add to favorite episodes"


    if request.method == "GET":  
        return render_template("episode.html", episode_data=episode_data, button_favorites=button_favorites)
    
    else:
        action = request.form.get("favorite")

        if action == "remove from favorite episodes":
            remove_favorite_episode(username, episode_id)
            
        elif action == "add to favorite episodes":
            add_favorite_episode(username, show_title, id, episode_data["season_number"], episode_data["episode_number"], episode_data["name"], episode_data["id"])

        return redirect(url_for("shows.episode", id=id, season=season, seasonEpisode=seasonEpisode))
