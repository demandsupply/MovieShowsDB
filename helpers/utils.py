from datetime import date

import requests, json
import os
from dotenv import load_dotenv


load_dotenv()
AUTH_CODE = os.getenv("API_KEY")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {AUTH_CODE}"}

def tmdb_get(endpoint):
    url = f"https://api.themoviedb.org/3/{endpoint}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()


def format_runtime(minutes):
    if minutes is None:
        return "N/A"
    h = minutes // 60
    m = minutes % 60
    return f"{h}h {m:02d}m"


def getCurrentYEar():
    current_date = date.today()
    current_year = current_date.year

    return current_year