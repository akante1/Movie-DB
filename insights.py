import sqlite3
import pandas as pd

pd.set_option("display.width", 130)
pd.set_option("display.max_columns", None)

conn = sqlite3.connect("movies.db")

# pull the joined data once, analyze in pandas
df = pd.read_sql("""
    SELECT m.movie_id, m.title, m.budget, m.revenue, m.roi,
           m.vote_average, m.release_year, g.genre_name
    FROM movies m
    JOIN movie_genres mg ON mg.movie_id = m.movie_id
    JOIN genres g        ON g.genre_id  = mg.genre_id
    WHERE m.has_financials = 1
""", conn)
conn.close()

# --- 1. Mean vs median ROI by genre: outlier detector ---
roi_check = (df.groupby("genre_name")["roi"]
               .agg(n="count", mean_roi="mean", median_roi="median")
               .query("n >= 30")
               .sort_values("mean_roi", ascending=False)
               .round(2))
print("=== Mean vs median ROI (big gap = outliers at work) ===")
print(roi_check)

# --- 2. Who ARE the outliers? ---
top_roi = df.drop_duplicates("movie_id").nlargest(10, "roi")
print("\n=== Top 10 ROI movies (the average-wreckers) ===")
print(top_roi[["title", "budget", "revenue", "roi", "release_year"]].round(1))

# --- 3. Does budget correlate with revenue? With quality? ---
uniq = df.drop_duplicates("movie_id")
print("\n=== Correlations ===")
print(f"budget vs revenue:      {uniq['budget'].corr(uniq['revenue']):.2f}")
print(f"budget vs rating:       {uniq['budget'].corr(uniq['vote_average']):.2f}")
print(f"rating vs revenue:      {uniq['vote_average'].corr(uniq['revenue']):.2f}")