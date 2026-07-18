import os
from fastapi.testclient import TestClient
from backend.main import app
import pytest
from backend.database import create_user_db,create_watchlist,create_media_cache

TEST_DB = ""

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr("database.DATABASE_URL",TEST_DB)
    create_user_db(TEST_DB)
    create_watchlist(TEST_DB)
    create_media_cache(TEST_DB)

    yield

    os.remove(TEST_DB)

client = TestClient(app)
def register_test_user():
    return client.post("/auth/register", json={
        "username":"testusername",
        "email":"testemail",
        "full_name":"fullname123",
        "password":"test123password"
    })
def register_and_login():
    client.post("/auth/register", json={
        "username":"testusername",
        "email":"testemail",
        "full_name":"fullname123",
        "password":"test123password"
    })
    response = client.post("/auth/login",data = {
        "username":"testusername",
        "password":"test123password"

    })
    token = response.json()["access_token"]
    return token
def test_register_user():
    response = register_test_user()
    assert response.status_code == 200

def test_register_duplicate_user():
    client.post("/auth/register", json ={
    "username": "kacper_dev_88",
    "email": "kacper.nowak.dev@example.pl",
    "full_name": "Kacper Nowak",
    "password": "x9#vL2!pQ7zK4mR"
    })
    response = client.post("/auth/register")
    assert response.status_code != 200

#test rejestracji a potem logowania, test zlego hasla, test dodania tego samego itemu do watchlisty

def test_register_and_login():
    register_test_user()
    response = client.post("/auth/login",
            data = {"username":"testusername",
                    "password":"test123password"})
    assert response.status_code == 200

def test_wrong_password():
    register_test_user()
    response = client.post("auth/login",
                           data = {
                            "username":"testusername",
                            "password":"wrongpassword123"})
    assert response.status_code == 401

def test_user_not_found():
    register_test_user()
    reponse = client.post("auth/login",
                           data = {
                            "username":"user123",
                            "password":"sillypassword123"})
    assert reponse.status_code == 401
def test_add_watchlist_item():
    token = register_and_login()

    response = client.post("/watchlist",json = {
        "tmdb_id":69740,
        "media_type":"tv",
        "status":"want_to_watch"
    },headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200

def test_duplicate_watchlist_item():
    token = register_and_login()
    client.post("/watchlist",json = {
        "tmdb_id":69740,
        "media_type":"tv",
        "status":"want_to_watch"
    },headers={"Authorization":f"Bearer {token}"})
    response = client.post("/watchlist",json = {
        "tmdb_id":69740,
        "media_type":"tv",
        "status":"favourite"
    },headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 409
def test_access_endpoint_without_token():
    response = client.get("/watchlist")
    assert response.status_code == 401

def test_access_endpoint_with_invalid_token():
    response = client.get("/watchlist",headers={"Authorization":"Bearer wrongtoken123"})
    assert response.status_code == 401
def test_add_invalid_rating_to_a_watchlist_item():
    token = register_and_login()
    response = client.post("/watchlist",json={"tmdb_id":1405,
        "media_type":"tv",
        "status":"completed",
        "rating": 15},headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 422

def test_add_invalid_media_type():
    token = register_and_login()
    response = client.post("/watchlist",json={"tmdb_id":1405,
        "media_type":"cartoon",
        "status":"completed",
        "rating": 9},headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 422
def test_delete_non_existent_watchlist_item():
    token = register_and_login()
    params = {"media_type":"tv"}
    response = client.delete("/watchlist/9999999",params=params,headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 404
    assert response.headers.get("Content-Type") == "application/json"
def test_edit_task():
    token = register_and_login()
    params = {"media_type":"tv"}
    client.post("/watchlist",json={"tmdb_id":69740,
        "media_type":"tv",
        "status":"completed",
        "rating":7},headers={"Authorization":f"Bearer {token}"})
    response = client.put("/watchlist/69740",
        json={"tmdb_id":69740,
        "media_type":"tv",
        "status":"favourite",
        "rating":9},params = params,headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
