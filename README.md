# MovieShowsDB

A personally designed Flask web app that allows users to search, compare, and save movies and shows using real-time data from The Movie Database. 

Check it on https://movieshowsdb.onrender.com.


# Features
- search bar to find movies/shows with detailed infos
- a section with the latest most popular releases
- discover - randomly - a new movie or show
- an updated list of the top 200 movies and top 100 shows
- compare the TMDB ratings of different movies/shows
- user authentication (login/register, NO mail required)
- save your favorites movies/shows into your account.. Or in a watchlist 


# Tech stack
- Python (flask)
- Jinja 2
- HTML & custom CSS
- Javascript
- PostgreeSQL
- Chart.js
- TMDB API (The Movie Database API)


# Project web structure and description 
- Main page: 
    - search movies/shows 
    - link for compare them
    - carousel with popular movies/shows
    - box which generates a random movies/shows each time the page is loaded
    - link for the top movies/shows
- Compare Movies: page where the user can look and compare up to 10 movies. Hovering a bar will show the movie details
- Compare Shows: page where the user can look and compare up to 5 shows. Hovering a dot on the chart will display some details
- Top 200 movies: page where are displayed the top 200 rated movies on The Movie Database
- Top 200 shows: page where are displayed the top 100 rated shows on The Movie Database
- My Area (user must be logged in): personal dashboard with favorite movies, shows, shows episodes and watchlist


# Installation Setup
In case you want to run the web app from your pc:
1. Clone the repo:
    git clone <repo-link> new-folder-name
    cd new-folder-name
    
2. Create the virtual environment:
    python3 -m venv venv
    source venv/bin/activate
    
3. Install dependencies:
    pip install -r requirements.txt
    
4. Set the env variables
   export DATABASE_URL=<your_db_connection_string>
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export API_KEY=<your_key> * 
   
5. Run the app:
    flask run
    go to http://localhost:5000 in your browser
    
* you must get a personal api key to run the webapp by yourself. You can (register and ) get it here: https://developer.themoviedb.org/docs/getting-started


# Credits

Movie and show data provided by "The Movie Database (TMDB)" - https://www.themoviedb.org/.
*This product uses the TMDB API but is not endorsed or certified by TMDB.*
