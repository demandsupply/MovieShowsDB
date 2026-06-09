import psycopg2
import os
from dotenv import load_dotenv
from cs50 import SQL


load_dotenv()

# db = SQL(
#     f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
#     f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# )

db = SQL(os.getenv("DATABASE_URL"))


def get_username(user_id):
    result = db.execute("SELECT username FROM users WHERE id = %s", user_id)
    return result[0]["username"] if result else None


# Favorites functions
def get_item_status(user, item_id, item_type):
    rows = db.execute(
        "SELECT category FROM favoriteswatchlist " \
        "WHERE username = %s AND " \
        "item_id = %s AND " \
        "type = %s",
        user, item_id, item_type
    )
    categories = [row["category"] for row in rows]
    return {
        "is_favorite": "favorite" in categories,
        "is_in_watchlist": "watchlist" in categories
    }


def is_favorite(user, item_id, type):
    rows = db.execute(
        "SELECT * FROM favoriteswatchlist " \
        "WHERE username = %s AND " \
        "item_id = %s AND " \
        "type = %s AND " \
        "category = 'favorite'", 
        user, item_id, type
    )
    return len(rows) == 1


def add_favorite(user, item_id, type, title):
    db.execute(
        "INSERT INTO favoriteswatchlist (username, type, title, item_id, category) " \
        "VALUES(%s, %s, %s, %s, 'favorite')",
        user, type, title, item_id
    )


def remove_favorite(user, item_id):
    db.execute(
        "DELETE FROM favoriteswatchlist WHERE username=%s AND " \
        "item_id=%s AND " \
        "category='favorite'",
        user, item_id
    )


# Watchlist functions

def is_in_watchlist(user, item_id, type):
    rows = db.execute(
        "SELECT * FROM favoriteswatchlist " \
        "WHERE username=%s " \
        "AND item_id=%s " \
        "AND type=%s " \
        "AND category='watchlist'", 
        user, item_id, type
    )
    return len(rows) == 1

def add_to_watchlist(user, item_id, type, title):
    db.execute(
        "INSERT INTO favoriteswatchlist (username, type, title, item_id, category) " \
        "VALUES(%s, %s, %s, %s, 'watchlist')",
        user, type, title, item_id
    )

def remove_from_watchlist(user, item_id):
    db.execute(
        "DELETE FROM favoriteswatchlist WHERE username=%s " \
        "AND item_id=%s " \
        "AND category='watchlist'",
        user, item_id
    )


# Episodes functions
def is_favorite_episode(user, episode_id):
    rows = db.execute(
        "SELECT * FROM usershows WHERE username=%s AND episode_id=%s",
        user, episode_id
    )
    return len(rows) == 1

def add_favorite_episode(user, show_title, show_id, season_number, episode_number, episode_title, episode_id):
    db.execute(
        "INSERT INTO usershows (username, show_title, show_id, season_number, episode_number, episode_title, episode_id) " \
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        user, show_title, show_id, season_number, episode_number, episode_title, episode_id
    )

def remove_favorite_episode(user, episode_id):
    db.execute(
        "DELETE FROM usershows WHERE username=%s AND episode_id=%s",
        user, episode_id
    )