# Movies & Series Tracker

Personal watchlist for movies and TV shows. Browse TMDB catalogues, save titles, track progress, rate what you’ve watched, and keep favourites — all behind cookie-based JWT auth.

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

