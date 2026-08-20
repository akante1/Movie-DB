import sqlite3
import pandas as pd

conn = sqlite3.connect("movies.db")
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", None)

# --- Q1: Revenue by genre (the three-table JOIN) ---
q1 = """
SELECT
    g.genre_name,
    COUNT(*)                          AS n_movies,
    ROUND(AVG(m.revenue) / 1e6, 1)    AS avg_revenue_millions,
    ROUND(AVG(m.roi), 2)              AS avg_roi
FROM movies m
JOIN movie_genres mg ON mg.movie_id = m.movie_id
JOIN genres g        ON g.genre_id  = mg.genre_id
WHERE m.has_financials = 1
GROUP BY g.genre_name
HAVING COUNT(*) >= 30
ORDER BY avg_roi DESC
"""
print("=== ROI and revenue by genre (min 30 movies) ===")
print(pd.read_sql(q1, conn))

# --- Q2: Does money buy quality? Budget tiers vs ratings ---
q2 = """
SELECT
    CASE
        WHEN budget < 10e6  THEN '1. under $10M'
        WHEN budget < 50e6  THEN '2. $10-50M'
        WHEN budget < 150e6 THEN '3. $50-150M'
        ELSE                     '4. $150M+'
    END                              AS budget_tier,
    COUNT(*)                         AS n_movies,
    ROUND(AVG(vote_average), 2)      AS avg_rating,
    ROUND(AVG(roi), 2)               AS avg_roi
FROM movies
WHERE has_financials = 1
GROUP BY budget_tier
ORDER BY budget_tier
"""
print("\n=== Budget tiers: rating and ROI ===")
print(pd.read_sql(q2, conn))

# --- Q3: Top earner per genre (RANK - the new window function) ---
q3 = """
WITH ranked AS (
    SELECT
        g.genre_name,
        m.title,
        m.revenue,
        RANK() OVER (
            PARTITION BY g.genre_name
            ORDER BY m.revenue DESC
        ) AS rev_rank
    FROM movies m
    JOIN movie_genres mg ON mg.movie_id = m.movie_id
    JOIN genres g        ON g.genre_id  = mg.genre_id
    WHERE m.has_financials = 1
)
SELECT genre_name, title, ROUND(revenue / 1e6, 0) AS revenue_millions
FROM ranked
WHERE rev_rank = 1
ORDER BY revenue_millions DESC
"""
print("\n=== Highest-grossing movie in each genre ===")
print(pd.read_sql(q3, conn))

# --- Q4: Ratings by decade (date-derived analysis) ---
q4 = """
SELECT
    decade,
    COUNT(*)                    AS n_movies,
    ROUND(AVG(vote_average), 2) AS avg_rating,
    ROUND(AVG(runtime), 0)      AS avg_runtime_min
FROM movies
WHERE decade >= 1970
GROUP BY decade
ORDER BY decade
"""
print("\n=== By decade: ratings and runtimes ===")
print(pd.read_sql(q4, conn))

conn.close()