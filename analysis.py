"""
Airbnb Market Analysis: Columbus vs New York City

My analysis answering the 5 research questions from my project README, using
real Inside Airbnb data (Columbus snapshot 2025-09-26, NYC snapshot 2026-06-14 --
I originally planned to use the Dec 4 2025 NYC snapshot, but it had no price
data at all, so I switched to a more recent NYC snapshot with real pricing).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 120)

DATA_DIR = "C:/Users/redre/AppData/Local/Temp/claude/airbnb_analysis/data"
OUT_DIR = "C:/Users/redre/AppData/Local/Temp/claude/airbnb_analysis/output"
import os
os.makedirs(OUT_DIR, exist_ok=True)

def load_and_clean(path, city_label):
    df = pd.read_csv(path, low_memory=False)
    # price comes in as "$123.00" strings
    df["price_clean"] = (
        df["price"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
    )
    # drop rows with no price or absurd outliers (top/bottom 0.5% and $0 listings)
    df = df[df["price_clean"] > 0]
    lo, hi = df["price_clean"].quantile([0.005, 0.995])
    df = df[(df["price_clean"] >= lo) & (df["price_clean"] <= hi)]
    df["city"] = city_label
    return df

col = load_and_clean(f"{DATA_DIR}/columbus_listings.csv", "Columbus")
nyc = load_and_clean(f"{DATA_DIR}/nyc_listings.csv", "New York City")

raw_col_n = len(pd.read_csv(f"{DATA_DIR}/columbus_listings.csv", low_memory=False))
raw_nyc_n = len(pd.read_csv(f"{DATA_DIR}/nyc_listings.csv", low_memory=False))

print(f"RAW_COUNT_COLUMBUS={raw_col_n}")
print(f"RAW_COUNT_NYC={raw_nyc_n}")
print(f"CLEAN_COUNT_COLUMBUS={len(col)}")
print(f"CLEAN_COUNT_NYC={len(nyc)}")

# ---------- Q1: avg nightly price by neighborhood ----------
col_price_by_neigh = col.groupby("neighbourhood_cleansed")["price_clean"].mean().sort_values(ascending=False)
nyc_price_by_neigh = nyc.groupby("neighbourhood_cleansed")["price_clean"].mean().sort_values(ascending=False)

print("\n=== Q1: Avg price by neighborhood (top 5) ===")
print("Columbus top 5:\n", col_price_by_neigh.head(5))
print("Columbus overall avg: ${:.2f}".format(col["price_clean"].mean()))
print("NYC top 5:\n", nyc_price_by_neigh.head(5))
print("NYC overall avg: ${:.2f}".format(nyc["price_clean"].mean()))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
col_price_by_neigh.head(10).plot(kind="barh", ax=axes[0], color="#2b6cb0")
axes[0].set_title("Columbus: Avg Price by Neighborhood (Top 10)")
axes[0].set_xlabel("Avg nightly price ($)")
axes[0].invert_yaxis()
nyc_price_by_neigh.head(10).plot(kind="barh", ax=axes[1], color="#c05621")
axes[1].set_title("NYC: Avg Price by Neighborhood (Top 10)")
axes[1].set_xlabel("Avg nightly price ($)")
axes[1].invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/01_price_by_neighborhood.png", dpi=120)
plt.close()

# ---------- Q2: availability vs price by neighborhood ----------
col_avail = col.groupby("neighbourhood_cleansed").agg(
    avg_price=("price_clean", "mean"), avg_availability=("availability_365", "mean"), n=("id", "count")
)
col_avail = col_avail[col_avail["n"] >= 5]
col_avail["avail_per_dollar"] = col_avail["avg_availability"] / col_avail["avg_price"]
col_avail = col_avail.sort_values("avail_per_dollar", ascending=False)

nyc_avail = nyc.groupby("neighbourhood_cleansed").agg(
    avg_price=("price_clean", "mean"), avg_availability=("availability_365", "mean"), n=("id", "count")
)
nyc_avail = nyc_avail[nyc_avail["n"] >= 5]
nyc_avail["avail_per_dollar"] = nyc_avail["avg_availability"] / nyc_avail["avg_price"]
nyc_avail = nyc_avail.sort_values("avail_per_dollar", ascending=False)

print("\n=== Q2: Best availability-per-dollar neighborhoods (top 5) ===")
print("Columbus:\n", col_avail.head(5)[["avg_price", "avg_availability", "avail_per_dollar"]])
print("NYC:\n", nyc_avail.head(5)[["avg_price", "avg_availability", "avail_per_dollar"]])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(col["price_clean"], col["availability_365"], alpha=0.15, s=8, label="Columbus", color="#2b6cb0")
ax.scatter(nyc["price_clean"], nyc["availability_365"], alpha=0.08, s=8, label="New York City", color="#c05621")
ax.set_xlim(0, 600)
ax.set_xlabel("Nightly price ($)")
ax.set_ylabel("Availability (days/365)")
ax.set_title("Price vs Availability")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/02_price_vs_availability.png", dpi=120)
plt.close()

# ---------- Q3: host concentration ----------
def host_concentration(df, city):
    # I found host_total_listings_count is entirely redacted for NYC in Inside
    # Airbnb's published data (a known effect of NYC Local Law 18 reporting
    # restrictions), so for any city where that field is unusable I fall back
    # to counting how many listings each host_id actually appears with IN THIS
    # DATASET as the concentration proxy instead. This is real, computed data
    # either way - just two different (clearly labeled) methodologies depending
    # on what the source data makes available for that city.
    if df["host_total_listings_count"].notna().sum() > 0:
        method = "host_total_listings_count field"
        hosts = df.drop_duplicates("host_id")[["host_id", "host_total_listings_count"]].copy()
        hosts["host_total_listings_count"] = hosts["host_total_listings_count"].fillna(1)
        single = (hosts["host_total_listings_count"] <= 1).sum()
        multi = (hosts["host_total_listings_count"] > 1).sum()
        multi_host_ids = hosts[hosts["host_total_listings_count"] > 1]["host_id"]
    else:
        method = "listings observed per host_id in this dataset"
        counts = df["host_id"].value_counts()
        single = (counts == 1).sum()
        multi = (counts > 1).sum()
        multi_host_ids = counts[counts > 1].index
    total = single + multi
    listings_by_multi = df[df["host_id"].isin(multi_host_ids)].shape[0]
    pct_listings_multi = listings_by_multi / len(df) * 100
    print(f"{city} [method: {method}]: {total} unique hosts | single-listing hosts: {single} ({single/total*100:.1f}%) | "
          f"multi-listing hosts: {multi} ({multi/total*100:.1f}%) | "
          f"% of ALL listings owned by multi-listing hosts: {pct_listings_multi:.1f}%")
    return single, multi, pct_listings_multi

print("\n=== Q3: Host ownership concentration ===")
col_single, col_multi, col_pct = host_concentration(col, "Columbus")
nyc_single, nyc_multi, nyc_pct = host_concentration(nyc, "NYC")

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].pie([col_single, col_multi], labels=["Single-listing hosts", "Multi-listing hosts"],
            autopct="%1.0f%%", colors=["#2b6cb0", "#90cdf4"])
axes[0].set_title("Columbus Host Concentration")
axes[1].pie([nyc_single, nyc_multi], labels=["Single-listing hosts", "Multi-listing hosts"],
            autopct="%1.0f%%", colors=["#c05621", "#fbd38d"])
axes[1].set_title("NYC Host Concentration")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_host_concentration.png", dpi=120)
plt.close()

# ---------- Q4: drivers of higher prices ----------
def price_drivers(df, city):
    features = ["accommodates", "bedrooms", "bathrooms", "number_of_reviews", "review_scores_rating"]
    avail = [f for f in features if f in df.columns]
    corr = df[avail + ["price_clean"]].corr(numeric_only=True)["price_clean"].drop("price_clean").sort_values(ascending=False)
    print(f"{city} correlation with price:\n{corr}")
    room_type_price = df.groupby("room_type")["price_clean"].mean().sort_values(ascending=False)
    print(f"{city} avg price by room type:\n{room_type_price}\n")
    return corr, room_type_price

print("\n=== Q4: Drivers of higher prices ===")
col_corr, col_rt_price = price_drivers(col, "Columbus")
nyc_corr, nyc_rt_price = price_drivers(nyc, "NYC")

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(col_rt_price.index.union(nyc_rt_price.index)))
labels = sorted(set(col_rt_price.index) | set(nyc_rt_price.index))
col_vals = [col_rt_price.get(l, 0) for l in labels]
nyc_vals = [nyc_rt_price.get(l, 0) for l in labels]
width = 0.35
xpos = np.arange(len(labels))
ax.bar(xpos - width/2, col_vals, width, label="Columbus", color="#2b6cb0")
ax.bar(xpos + width/2, nyc_vals, width, label="NYC", color="#c05621")
ax.set_xticks(xpos)
ax.set_xticklabels(labels, rotation=20, ha="right")
ax.set_ylabel("Avg nightly price ($)")
ax.set_title("Avg Price by Room Type")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/04_price_by_room_type.png", dpi=120)
plt.close()

# ---------- Q5: room type distribution ----------
col_rt_dist = col["room_type"].value_counts(normalize=True) * 100
nyc_rt_dist = nyc["room_type"].value_counts(normalize=True) * 100
print("\n=== Q5: Room type distribution (%) ===")
print("Columbus:\n", col_rt_dist)
print("NYC:\n", nyc_rt_dist)

fig, ax = plt.subplots(figsize=(8, 6))
labels5 = sorted(set(col_rt_dist.index) | set(nyc_rt_dist.index))
col_vals5 = [col_rt_dist.get(l, 0) for l in labels5]
nyc_vals5 = [nyc_rt_dist.get(l, 0) for l in labels5]
xpos5 = np.arange(len(labels5))
ax.bar(xpos5 - 0.2, col_vals5, 0.4, label="Columbus", color="#2b6cb0")
ax.bar(xpos5 + 0.2, nyc_vals5, 0.4, label="NYC", color="#c05621")
ax.set_xticks(xpos5)
ax.set_xticklabels(labels5, rotation=20, ha="right")
ax.set_ylabel("% of listings")
ax.set_title("Room Type Distribution: Columbus vs NYC")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_room_type_distribution.png", dpi=120)
plt.close()

print("\nDONE - all 5 PNGs written to", OUT_DIR)
