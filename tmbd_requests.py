from pydantic import BaseModel
import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ODBlYzRmOTdjY2IwNGFlNzVmYTE1N2FiOWZkZjFkNCIsIm5iZiI6MTc4MjA1ODQzNC4xNDYsInN1YiI6IjZhMzgwZGMyMDQyMjU3ZTAzNjM0NzMwNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.dZOhvjo3fdL8dTs_1H-xRa5Y0DOgd11xdqpAs8JYeXM"
def search_tv(query : str):
    url = f"https://api.themoviedb.org/3/search/tv?query={query}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"

    }  
    data = requests.get(url, headers=headers)
    response = data.json()
    return (response["results"][0]["overview"])
def search_movie(query : str):
    url = f"https://api.themoviedb.org/3/search/movie?query={query}"
    headers = {
        "accept" : "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = requests.get(url,headers=headers)
    response = data.json()
    result = response['results'][0]['title']
    return result



