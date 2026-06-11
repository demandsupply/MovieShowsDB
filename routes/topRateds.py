import asyncio
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from helpers.utils import tmdb_get, format_runtime


top_rateds_bp = Blueprint("toprated", __name__)


@top_rateds_bp.route("/toprated", methods=["GET"])
async def top_rated():
    if request.method == "GET":
        pages = 10

        # old code for reference
        # for page in range(pages):
        #     movie_data = tmdb_get(f"movie/top_rated?language=en-US&page={page}")
        # if movie_data:
        #     response_list.append(movie_data)

        # use async to fetch pages 1 to 10 for top 200 - 20 per page
        tasks = [asyncio.to_thread(tmdb_get, f"movie/top_rated?language=en-US&page={page}") for page in range(1, pages + 1)]
        response_list = await asyncio.gather(*tasks)
        
        # filter out None results from the list
        response_list = [data for data in response_list if data]
        
        print("Top 200 movies: ", response_list)

        return render_template("toprated.html", response_list=response_list)


@top_rateds_bp.route("/topratedshows", methods=["GET"])
async def top_rated_shows():
    if request.method == "GET":
        pages = 5 

        tasks = [asyncio.to_thread(tmdb_get, f"tv/top_rated?language=en-US&page={page}") for page in range(1, pages + 1)]
        response_list = await asyncio.gather(*tasks)
        
        response_list = [data for data in response_list if data]
        
        print("Top 100 shows: ", response_list)

        return render_template("topratedshows.html", response_list=response_list)
