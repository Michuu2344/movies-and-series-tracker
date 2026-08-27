from pydantic import BaseModel
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_trailer_key(tmdb_id : int,media_type: str ="movie")-> str| None:

    if media_type not in("movie","tv"):
            raise ValueError("media_type value must be 'movie' or 'tv'")
    headers = {
            "accept" : "application/json",
            "Authorization" : f"Bearer {API_KEY}"
        }
    
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos"
    try:
        response = requests.get(url,headers=headers,timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    results = data.get("results",[])

    for video in results:
        if video.get("site") == "YouTube" and video.get("type") =="Trailer" and video.get("official"):
            return video.get("key")

    for video in results:
        if video.get("site") == "YouTube" and video.get("type") =="Trailer":
            return video.get("key")

    return None








def get_details_tv(tmdb_id : int):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"

    }  
    url2 = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    data2 = requests.get(url2,headers=headers) 
    tv = data2.json()

    url3 = f"https://api.themoviedb.org/3/tv/{tmdb_id}/credits"
    data3 = requests.get(url3,headers=headers)
    cast = data3.json()




    poster_path = tv['poster_path']
    backdrop_path = tv['backdrop_path']
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    backdrop_url = f"https://image.tmdb.org/t/p/w500{backdrop_path}"
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
            "name": (tv['name']),
            "original_name" : tv['original_name'],
            "release_date":(tv['first_air_date']),
            "overview":(tv['overview']),
            "genre": tv['genres'][0:2],
            "rating": tv['vote_average'],
            "most_popular_cast_members": sorted_actors,
            "poster": poster_url ,
            "vote_count" : tv['vote_count'],
            "number_of_seasons" : tv['number_of_seasons'],
            "number_of_episodes" : tv['number_of_episodes'],
            "episode_run_time" : tv['episode_run_time'],
            "backdrop" : backdrop_url,
            "original_language" :tv['original_language'],
            "first_air_date" : tv['first_air_date'],
            "last_air_date" : tv['last_air_date'],
            "created_by" : tv['created_by'],
            "origin_country" : tv["origin_country"][0],
            "trailer_key":get_trailer_key(tmdb_id,"tv")
            }
    
def get_details_movie(tmdb_id : int):
    headers = {
        "accept" : "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    url2 = f"https://api.themoviedb.org/3/movie/{tmdb_id}"    
    data2 = requests.get(url2,headers=headers)
    movie = data2.json()
    url3 = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
    data3 = requests.get(url3,headers=headers)
    response3 = data3.json()
    people = []
    for x in response3['cast']:
        people.append({
            "name":x['name'],
            "popularity": x['popularity'],
            "character": x['character']
        })
    actors = sorted(people,key = lambda x: x['popularity'],reverse=True)
    sorted_actors = actors[:5]
    
    poster_path = movie['poster_path']
    crew_members = []
    for x in response3['crew']:
            crew_members.append({
                "name":x['name'],
                "popularity": x['popularity'],
                "profile_path": x['profile_path']
            })
    crew_members_sorted = sorted(crew_members,key = lambda x: x['popularity'],reverse=True)
    five_crew_members = crew_members_sorted[:5]

    backdrop_path = movie['backdrop_path']
    backdrop_url = f"https://image.tmdb.org/t/p/w500{backdrop_path}"
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return {"tmdb_id": tmdb_id,
            "name": (movie['title']),
            "original_name" : movie['original_title'],
            "release_date":(movie['release_date']),
            "overview":(movie['overview']),
            "genre": movie['genres'][0:2],
            "rating": movie['vote_average'],
            "most_popular_cast_members": sorted_actors,
            "poster": poster_url ,
            "vote_count" : movie['vote_count'],
            "backdrop" : backdrop_url,
            "revenue" : movie['revenue'],
            "runtime" : movie['runtime'],
            "origin_country" : movie['origin_country'][0],
            "original_language" : movie['original_language'],
            "crew" : five_crew_members,
            "trailer_key" : get_trailer_key(tmdb_id,"movie")

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
            "rating":f"{movie['vote_average']:.2f}",
            "vote_count" : movie['vote_count'],
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
def get_trending_movies():
    url = "https://api.themoviedb.org/3/trending/movie/day?language=en-US"
    headers = {
        "accept" : "application/json",
        "Authorization" : f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    results = []
    response = data.json()
    poster_url = f"https://image.tmdb.org/t/p/w500"
    for item in response['results']:
        results.append({
            "tmdb_id" : item['id'],
            "media_type" : item['media_type'],
            "poster" : f"{poster_url}{item['poster_path']}"
            
        })
    return results
def get_popular_movies():
    url ="https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    headers = {
            "accept" : "application/json",
            "Authorization" : f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    results = []
    response = data.json()
    poster_url = f"https://image.tmdb.org/t/p/w500"
    for item in response['results']:
        results.append({
            "tmdb_id" : item['id'],
            "media_type" : "movie",
            "poster" : f"{poster_url}{item['poster_path']}"
    
                
        })
    return results
def get_trending_tv_shows():
    url ="https://api.themoviedb.org/3/trending/tv/day?language=en-US"
    headers = {
            "accept" : "application/json",
            "Authorization" : f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    results = []
    response = data.json()
    poster_url = f"https://image.tmdb.org/t/p/w500"
    for item in response['results']:
        results.append({
            "tmdb_id" : item['id'],
            "media_type" : item['media_type'],
            "poster" : f"{poster_url}{item['poster_path']}"
    
                
        })
    return results

def get_popular_tv_shows():
    url ="https://api.themoviedb.org/3/tv/popular?language=en-US&page=1"
    headers = {
            "accept" : "application/json",
            "Authorization" : f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    results = []
    response = data.json()
    poster_url = f"https://image.tmdb.org/t/p/w500"
    for item in response['results']:
        results.append({
            "tmdb_id" : item['id'],
            "media_type" : "tv",
            "poster" : f"{poster_url}{item['poster_path']}"
    
                
        })
    return results


