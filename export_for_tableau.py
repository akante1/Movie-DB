import sqlite3
import pandas as pd

conn = sqlite3.connect("movies.db")

q = """
SELECT
    m.movie_id,
    m.title,
    m.release_date,
    m.release_year,
    m.decade,
    m.budget,
    m.revenue,
    m.roi,
    m.runtime,
    m.vote_average,
    m.vote_count,
    m.has_financials,
    g.genre_name
FROM movies m
JOIN movie_genres mg ON mg.movie_id = m.movie_id
JOIN genres g        ON g.genre_id  = mg.genre_id
    
"""
df = pd.read_sql(q, conn)
conn.close()

df.to_csv("tableau_data.csv", index=False)
print(f"Exported {len(df)} rows to tableau_data.csv")