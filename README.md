# Movies & Series Tracker

Personal watchlist for movies and TV shows. Browse TMDB catalogues, save titles, track progress, rate what you’ve watched, and keep favourites — all behind cookie-based JWT auth.

## Screenshots

### Home page
<p align="center">
  <img src="https://github.com/user-attachments/assets/8dd797dc-9b90-4b7c-9698-4baa132ae8ef" width="900" alt="Home page">
</p>

### Search results
<p align="center">
  <img src="https://github.com/user-attachments/assets/4cc6ea76-f45f-42a8-9ae1-cd3e9af54dc5" width="900" alt="Search results">
</p>

### Details page
<p align="center">
  <img src="https://github.com/user-attachments/assets/edbe4a09-ed3e-4e10-a0b6-2a9c975d2663" width="900" alt="Details page">
</p>

### Watchlist
<p align="center">
  <img src="https://github.com/user-attachments/assets/7e4a1201-cf10-40ac-b721-3b4adbae0e28" width="900" alt="Watchlist">
</p>

## Features

- Register / login / logout with JWT stored in **httpOnly cookies**
- Password hashing (Argon2) and password strength validation
- Search movies and TV shows via **TMDB**
- Trending & popular carousels on the home page
- Detail pages: overview, cast, runtime, trailer, recommendations
- Watchlist: add / edit status / rate (1–10) / favourite / remove
- Statuses: Want to watch · Watching · Completed · Dropped
- PostgreSQL **media cache** so watchlist posters/titles don’t hit TMDB every time
- Custom **token-bucket rate limiter** (429 + Retry-After headers)
- Docker Compose: API, nginx frontend, Postgres, pgAdmin

## Tech stack

| Layer     | Stack                                      |
|-----------|--------------------------------------------|
| Backend   | Python, FastAPI, Pydantic, PyJWT, pwdlib   |
| Database  | PostgreSQL, psycopg2 connection pool       |
| Frontend  | HTML, CSS, vanilla JS, Bootstrap 5         |
| External  | TMDB API                                   |
| Infra     | Docker, Docker Compose, nginx              |

