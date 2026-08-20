import os
import requests
import time
import pandas as pd
from config import API_KEY

movies = pd.read_csv("movies_raw.csv")

# --- RESUME: if a previous run saved progress, skip what's already done ---
if os.path.exists("movies_detailed.csv"):
    done = pd.read_csv("movies_detailed.csv")
    done_ids = set(done["id"])
    details = done.to_dict("records")
    print(f"Resuming: {len(done_ids)} movies already fetched")
else:
    done_ids = set()
    details = []

def fetch_with_retry(url, params, tries=3):
    """Try up to 3 times, waiting longer each time. Returns None if all fail."""
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
            print(f"  status {r.status_code}, attempt {attempt}")
        except requests.exceptions.RequestException as e:
            print(f"  network error attempt {attempt}: {type(e).__name__}")
        time.sleep(2 * attempt)   # wait 2s, then 4s, then 6s
    return None

total = len(movies)
for i, movie_id in enumerate(movies["id"], start=1):
    if movie_id in done_ids:
        continue                                  # already have it, skip

    d = fetch_with_retry(f"https://api.themoviedb.org/3/movie/{movie_id}",
                         {"api_key": API_KEY})
    if d is None:
        print(f"Movie {movie_id}: gave up after 3 tries, skipping")
        continue

    details.append({
        "id": d["id"],
        "title": d["title"],
        "release_date": d.get("release_date"),
        "budget": d.get("budget"),
        "revenue": d.get("revenue"),
        "runtime": d.get("runtime"),
        "vote_average": d.get("vote_average"),
        "vote_count": d.get("vote_count"),
        "genres": "|".join(g["name"] for g in d.get("genres", [])),
    })

    # --- CHECKPOINT: save every 100 movies so a crash loses at most 100 ---
    if len(details) % 100 == 0:
        pd.DataFrame(details).to_csv("movies_detailed.csv", index=False)
        print(f"{len(details)}/{total} enriched (checkpoint saved)")

    time.sleep(0.25)

pd.DataFrame(details).to_csv("movies_detailed.csv", index=False)
print(f"\nDone: {len(details)} detailed records saved")