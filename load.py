import sqlite3
import pandas as pd

df = pd.read_csv("movies_clean.csv")

conn = sqlite3.connect("movies.db")
cur = conn.cursor()

# --- build the three drawers ---
cur.executescript("""
DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS movies;

CREATE TABLE movies (
    movie_id     INTEGER PRIMARY KEY,
    title        TEXT,
    release_date TEXT,
    release_year INTEGER,
    decade       INTEGER,
    budget       INTEGER,
    revenue      INTEGER,
    roi          REAL,
    runtime      REAL,
    vote_average REAL,
    vote_count   INTEGER,
    has_financials INTEGER
);

CREATE TABLE genres (
    genre_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT UNIQUE
);

CREATE TABLE movie_genres (
    movie_id INTEGER REFERENCES movies(movie_id),
    genre_id INTEGER REFERENCES genres(genre_id),
    PRIMARY KEY (movie_id, genre_id)
);
""")

# --- load movies ---
movie_cols = ["id", "title", "release_date", "release_year", "decade",
              "budget", "revenue", "roi", "runtime",
              "vote_average", "vote_count", "has_financials"]
movies_out = df[movie_cols].rename(columns={"id": "movie_id"})
movies_out.to_sql("movies", conn, if_exists="append", index=False)

# --- EXPLODE the genre strings into the bridge table ---
# "Action|Adventure" becomes two rows linking this movie to two genres
all_genres = set()
links = []
for _, row in df.iterrows():
    if pd.isna(row["genres"]) or row["genres"] == "":
        continue
    for g in row["genres"].split("|"):
        all_genres.add(g)
        links.append((row["id"], g))

# insert unique genres, let the DB hand out their ids
for g in sorted(all_genres):
    cur.execute("INSERT OR IGNORE INTO genres (genre_name) VALUES (?)", (g,))

# look up each genre's id, then load the bridge
genre_ids = {name: gid for gid, name in
             cur.execute("SELECT genre_id, genre_name FROM genres")}
cur.executemany(
    "INSERT OR IGNORE INTO movie_genres (movie_id, genre_id) VALUES (?, ?)",
    [(mid, genre_ids[g]) for mid, g in links]
)

conn.commit()

# --- proof it worked: first JOIN of the project ---
check = pd.read_sql("""
    SELECT g.genre_name, COUNT(*) AS movie_count
    FROM movie_genres mg
    JOIN genres g ON g.genre_id = mg.genre_id
    GROUP BY g.genre_name
    ORDER BY movie_count DESC
""", conn)
print(check)

counts = pd.read_sql("""
    SELECT
        (SELECT COUNT(*) FROM movies)       AS movies,
        (SELECT COUNT(*) FROM genres)       AS genres,
        (SELECT COUNT(*) FROM movie_genres) AS links
""", conn)
print("\n", counts)
conn.close()