from pydantic import BaseModel
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
def get_details_tv(tmdb_id : int):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"

    }  
    url2 = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    data2 = requests.get(url2,headers=headers) 
    response2 = data2.json()

    url3 = f"https://api.themoviedb.org/3/tv/{tmdb_id}/credits"
    data3 = requests.get(url3,headers=headers)
    cast = data3.json()
    poster_path = response2['poster_path']
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    people = []
    for x in cast['cast']:
        people.append({
            "name":x['name'],
            "popularity": x['popularity'],
            "character": x['character']
        })
    actors = sorted(people,key = lambda x: x['popularity'],reverse=True)
    sorted_actors = actors[:5]
    
    return {"tmdb_id":tmdb_id,
            "name": (response2['name']),
            "release_date":(response2['first_air_date']),
            "overview":(response2['overview']),
            "genre": response2['genres'][0:2],
            "rating": response2['vote_average'],
            "most_popular_cast_members": sorted_actors,
            "poster": poster_url 
            }
    
def get_details_movie(tmdb_id : int):
    headers = {
        "accept" : "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    url2 = f"https://api.themoviedb.org/3/movie/{tmdb_id}"    
    data2 = requests.get(url2,headers=headers)
    response2 = data2.json()
    url3 = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
    data3 = requests.get(url3,headers=headers)
    cast = data3.json()
    people = []
    for x in cast['cast']:
        people.append({
            "name":x['name'],
            "popularity": x['popularity'],
            "character": x['character']
        })
    actors = sorted(people,key = lambda x: x['popularity'],reverse=True)
    sorted_actors = actors[:5]
    poster_path = response2['poster_path']
    
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return {"tmdb_id": tmdb_id,
            "name": (response2['title']),
            "release_date":(response2['release_date']),
            "overview":(response2['overview']),
            "genre": response2['genres'][0:2],
            "rating": response2['vote_average'],
            "most_popular_cast_members": sorted_actors,
            "poster": poster_url 
            }
def search_movie(query : str):
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false"
    headers = {
        "accept" : "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    response = data.json()
    results = []
    
    poster_url = f"https://image.tmdb.org/t/p/w500"
    for movie in response['results']:
        results.append({
            "tmdb_id":movie['id'],
            "name":movie['title'],
            "release_date":movie['release_date'],
            "overview":movie['overview'],
            "poster":f"{poster_url}{movie['poster_path']}",
            "rating":f"{movie['vote_average']:.2f}"
        })
    return results
def search_tv(query : str):
    url = f"https://api.themoviedb.org/3/search/tv?query={query}&include_adult=false"
    headers = {
        "accept" : "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    response = data.json()
    results = []
    
    
    poster_url = f"https://image.tmdb.org/t/p/w500"

    for tv in response['results']:
        results.append({
            "tmdb_id":tv['id'],
            "name":tv['name'],
            "release_date":tv['first_air_date'],
            "overview":tv['overview'],
            "poster":f"{poster_url}{tv['poster_path']}",
            "rating":f"{tv['vote_average']:.2f}"
        })
    return results
        



