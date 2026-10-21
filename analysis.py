"""Columbus and New York listings from Inside Airbnb.

Columbus file: 22 September 2026.
New York file: 14 September 2026.
Source: https://insideairbnb.com/get-the-data/
License: Creative Commons Attribution 4.0.

The files are not stored in the repo. A run downloads them into data/.
"""

import json
import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT
MIN_N = 30

FILES = {
    "Columbus": (
        "columbus.csv.gz",
        "https://data.insideairbnb.com/united-states/oh/columbus/2026-09-22/data/listings.csv.gz",
        "2026-09-22",
    ),
    "New York": (
        "nyc.csv.gz",
        "https://data.insideairbnb.com/united-states/ny/new-york-city/2026-09-14/data/listings.csv.gz",
        "2026-09-14",
    ),
}

BATH_RE = re.compile(r"(\d+(?:\.\d+)?)")


def ensure_files():
    DATA.mkdir(exist_ok=True)
    for _city, (name, url, _date) in FILES.items():
        path = DATA / name
        if path.exists() and path.stat().st_size > 0:
            continue
        import urllib.request

        urllib.request.urlretrieve(url, path)


def bath_count(value):
    if pd.isna(value):
        return np.nan
    match = BATH_RE.search(str(value))
    if not match:
        return np.nan
    return float(match.group(1))


def load_raw(path):
    df = pd.read_csv(path, low_memory=False)
    df["price_clean"] = (
        df["price"].astype(str).str.replace(r"[\$,]", "", regex=True).replace("nan", np.nan)
    )
    df["price_clean"] = pd.to_numeric(df["price_clean"], errors="coerce")
    df["bath_n"] = df["bathrooms_text"].map(bath_count)
    return df


def clean_prices(df):
    priced = df[df["price_clean"] > 0].copy()
    lo, hi = priced["price_clean"].quantile([0.005, 0.995])
    kept = priced[(priced["price_clean"] >= lo) & (priced["price_clean"] <= hi)].copy()
    return kept, float(lo), float(hi)


def host_split(df):
    field = "calculated_host_listings_count"
    usable = df[field].notna().mean() if field in df.columns else 0
    hosts = df.drop_duplicates("host_id")
    if usable > 0.5:
        method = "calculated_host_listings_count"
        single = int((hosts[field] <= 1).sum())
        multi = int((hosts[field] > 1).sum())
        multi_ids = set(hosts.loc[hosts[field] > 1, "host_id"])
    else:
        method = "host_id counted inside this file"
        counts = df["host_id"].value_counts()
        single = int((counts == 1).sum())
        multi = int((counts > 1).sum())
        multi_ids = set(counts[counts > 1].index)
    share = float(df["host_id"].isin(multi_ids).mean() * 100)
    anywhere = None
    if "host_total_listings_count" in df.columns and df["host_total_listings_count"].notna().mean() > 0.5:
        anywhere_hosts = hosts.dropna(subset=["host_total_listings_count"])
        anywhere = {
            "single_host_pct": round(float((anywhere_hosts["host_total_listings_count"] <= 1).mean() * 100), 1),
            "listings_held_by_multi_pct": round(
                float(df["host_id"].isin(
                    set(anywhere_hosts.loc[anywhere_hosts["host_total_listings_count"] > 1, "host_id"])
                ).mean() * 100),
                1,
            ),
        }
    total = single + multi
    return {
        "method": method,
        "hosts": total,
        "single_host_pct": round(single / total * 100, 1),
        "multi_host_pct": round(multi / total * 100, 1),
        "listings_held_by_multi_pct": round(share, 1),
        "anywhere": anywhere,
        "single": single,
        "multi": multi,
    }


def neighborhood_table(df):
    table = df.groupby("neighbourhood_cleansed").agg(
        n=("id", "count"),
        median_price=("price_clean", "median"),
        mean_price=("price_clean", "mean"),
        median_open=("availability_365", "median"),
    )
    return table[table["n"] >= MIN_N].sort_values("median_price", ascending=False)


def price_drivers(df):
    cols = ["accommodates", "bedrooms", "bath_n", "number_of_reviews", "review_scores_rating", "price_clean"]
    corr = df[cols].corr(numeric_only=True)["price_clean"].drop("price_clean").sort_values(ascending=False)
    by_room = df.groupby("room_type")["price_clean"].agg(["median", "mean", "count"]).sort_values("median", ascending=False)
    return corr, by_room


def room_mix(df):
    return (df["room_type"].value_counts(normalize=True) * 100).round(1)


def main():
    ensure_files()
    os.makedirs(OUT, exist_ok=True)
    summary = {}
    frames = {}
    cleaned = {}
    for city, (name, _url, date) in FILES.items():
        raw = load_raw(DATA / name)
        kept, lo, hi = clean_prices(raw)
        frames[city] = raw
        cleaned[city] = kept
        summary[city] = {
            "date": date,
            "rows": int(len(raw)),
            "priced_rows": int((raw["price_clean"] > 0).sum()),
            "clean_rows": int(len(kept)),
            "price_floor": round(lo, 2),
            "price_cap": round(hi, 2),
            "mean_price": round(float(kept["price_clean"].mean()), 2),
            "median_price": round(float(kept["price_clean"].median()), 2),
            "host_total_null_pct": round(float(raw["host_total_listings_count"].isna().mean() * 100), 1),
            "calculated_null_pct": round(float(raw["calculated_host_listings_count"].isna().mean() * 100), 1),
            "bathrooms_null_pct": round(float(raw["bathrooms"].isna().mean() * 100), 1),
            "hosts": host_split(raw),
            "room_mix_pct": room_mix(raw).to_dict(),
        }
        top_median = neighborhood_table(kept).head(5)
        open_cal = neighborhood_table(kept).sort_values("median_open", ascending=False).head(5)
        corr, by_room = price_drivers(kept)
        summary[city]["top_median_price"] = [
            {"neighbourhood": idx, "n": int(row.n), "median": round(float(row.median_price), 2), "mean": round(float(row.mean_price), 2)}
            for idx, row in top_median.iterrows()
        ]
        summary[city]["most_open"] = [
            {"neighbourhood": idx, "n": int(row.n), "median_open": round(float(row.median_open), 1), "median_price": round(float(row.median_price), 2)}
            for idx, row in open_cal.iterrows()
        ]
        summary[city]["corr"] = {k: round(float(v), 3) for k, v in corr.items()}
        summary[city]["price_by_room"] = [
            {"room_type": idx, "median": round(float(row["median"]), 2), "mean": round(float(row["mean"]), 2), "n": int(row["count"])}
            for idx, row in by_room.iterrows()
        ]

    colors = {"Columbus": "#2b6cb0", "New York": "#c05621"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, city in zip(axes, ["Columbus", "New York"]):
        table = neighborhood_table(cleaned[city]).head(10).sort_values("median_price")
        ax.barh(table.index, table["median_price"], color=colors[city])
        ax.set_title(f"{city}: median night, {MIN_N}+ listings")
        ax.set_xlabel("Median nightly price ($)")
    fig.tight_layout()
    fig.savefig(OUT / "01_price_by_neighborhood.png", dpi=120)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, city in zip(axes, ["Columbus", "New York"]):
        table = neighborhood_table(cleaned[city]).sort_values("median_open").tail(10)
        ax.barh(table.index, table["median_open"], color=colors[city])
        ax.set_title(f"{city}: most open calendars, {MIN_N}+ listings")
        ax.set_xlabel("Median open nights in the next 365")
    fig.tight_layout()
    fig.savefig(OUT / "02_price_vs_availability.png", dpi=120)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax, city in zip(axes, ["Columbus", "New York"]):
        hosts = summary[city]["hosts"]
        ax.pie(
            [hosts["single"], hosts["multi"]],
            labels=["One listing in this city", "More than one"],
            autopct="%1.0f%%",
            colors=[colors[city], "#cbd5e0"],
        )
        ax.set_title(f"{city} hosts")
    fig.tight_layout()
    fig.savefig(OUT / "03_host_concentration.png", dpi=120)
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    labels = sorted(set(cleaned["Columbus"]["room_type"]) | set(cleaned["New York"]["room_type"]))
    xpos = np.arange(len(labels))
    width = 0.35
    for offset, city in ((-width / 2, "Columbus"), (width / 2, "New York")):
        medians = cleaned[city].groupby("room_type")["price_clean"].median()
        ax.bar(xpos + offset, [medians.get(label, 0) for label in labels], width, label=city, color=colors[city])
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Median nightly price ($)")
    ax.set_title("Median price by room type")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "04_price_by_room_type.png", dpi=120)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 6))
    labels = sorted(set(frames["Columbus"]["room_type"]) | set(frames["New York"]["room_type"]))
    xpos = np.arange(len(labels))
    for offset, city in ((-0.2, "Columbus"), (0.2, "New York")):
        mix = frames[city]["room_type"].value_counts(normalize=True) * 100
        ax.bar(xpos + offset, [mix.get(label, 0) for label in labels], 0.4, label=city, color=colors[city])
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("% of listings")
    ax.set_title("Room type")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "05_room_type_distribution.png", dpi=120)
    plt.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
