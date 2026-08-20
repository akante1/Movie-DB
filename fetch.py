import requests
import time
import pandas as pd
from config import API_KEY

url = "https://api.themoviedb.org/3/movie/popular"

all_movies = []
PAGES = 100   # 100 pages x 20 movies = 2,000 movies

for page in range(1, PAGES + 1):
    params = {"api_key": API_KEY, "page": page}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Page {page} failed with status {response.status_code}, skipping")
        continue

    all_movies.extend(response.json()["results"])

    if page % 10 == 0:                       # progress note every 10 pages
        print(f"Fetched {page} pages ({len(all_movies)} movies so far)")

    time.sleep(0.3)                          # be polite: brief pause between requests

df = pd.DataFrame(all_movies)

# keep only the columns we care about
df = df[["id", "title", "release_date", "vote_average", "vote_count", "popularity"]]

df.to_csv("movies_raw.csv", index=False)
print(f"\nSaved {len(df)} movies to movies_raw.csv")