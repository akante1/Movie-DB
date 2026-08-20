import pandas as pd

df = pd.read_csv("movies_detailed.csv")
start_count = len(df)
print(f"Starting with {start_count} movies\n")

# --- MEASURE the mess before touching anything ---
print("=== Damage report ===")
print(f"Zero budget:        {(df['budget'] == 0).sum()}")
print(f"Zero revenue:       {(df['revenue'] == 0).sum()}")
print(f"Missing release date: {df['release_date'].isna().sum()}")
print(f"Zero/missing runtime: {((df['runtime'].fillna(0)) == 0).sum()}")
print(f"No genres listed:   {df['genres'].isna().sum() + (df['genres'] == '').sum()}")
print(f"Duplicate ids:      {df.duplicated(subset='id').sum()}")

# --- CLEAN, one decision at a time, counting each ---

# 1. exact duplicates (same movie fetched twice across pages)
df = df.drop_duplicates(subset="id")
after_dupes = len(df)

# 2. missing dates are useless for decade analysis
df = df.dropna(subset=["release_date"])
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df = df.dropna(subset=["release_date"])   # drops any dates that failed to parse
after_dates = len(df)

# 3. the big decision: money analysis needs real money numbers.
#    zero budget/revenue = unreported, not free. keep a FLAG, don't delete -
#    ratings analysis can still use these rows!
df["has_financials"] = (df["budget"] > 0) & (df["revenue"] > 0)

# 4. derived columns while we're here
df["release_year"] = df["release_date"].dt.year
df["decade"] = (df["release_year"] // 10) * 10
df["roi"] = df.apply(
    lambda r: r["revenue"] / r["budget"] if r["has_financials"] else None, axis=1
)

df.to_csv("movies_clean.csv", index=False)

# --- the receipts ---
print(f"\n=== Cleaning receipts ===")
print(f"Removed {start_count - after_dupes} duplicates")
print(f"Removed {after_dupes - after_dates} rows with missing/bad dates")
print(f"Kept {len(df)} movies total")
print(f"  of which {df['has_financials'].sum()} have usable financials "
      f"({df['has_financials'].mean() * 100:.0f}%)")