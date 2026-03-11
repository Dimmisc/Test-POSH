import requests
from pprint import pprint

url = "https://olimp.miet.ru/ppo_it/api"

def get_data():
    res = requests.get(url)
    if res and "message" in res.json() and "data" in res.json()["message"]:
        return res.json()["message"]["data"]
    return None
