#!/usr/bin/env python3
"""
Generate report cards for each GBA ward based on citizen-submitted grievance ratings.

Scoring:
  - Each category is a subject worth 100 marks.
  - Marks for a ward-category = (mean_rating - 1) * 25
    (Rating 1 = 0 marks, ..., Rating 5 = 100 marks)
  - Overall percentage = total_marks / max_possible_marks * 100
    where max_possible_marks counts only categories that have rated complaints.
  - Ward rank is determined by overall percentage (ties broken alphabetically).

Grades:
  A+ 90-100 | A 75-89 | B 60-74 | C 45-59 | D 30-44 | F <30
"""

import json
import pandas as pd
from pathlib import Path
from urllib.request import urlretrieve

AREA_MAPPING_PATH = Path("data/ward-areas.json")
WARD_ALIAS_PATH = Path("data/ward-name-aliases.json")


PARQUET_PATH = Path("data.parquet")
PARQUET_DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/Vonter/bbmp-citizen-grievances/main/"
    "data/citizen-grievances.parquet"
)


def ensure_parquet_file() -> Path:
    """Ensure data.parquet exists locally, downloading it if needed."""
    if not PARQUET_PATH.exists():
        print(f"{PARQUET_PATH} not found. Downloading...")
        urlretrieve(PARQUET_DOWNLOAD_URL, PARQUET_PATH)
        print(f"Downloaded {PARQUET_PATH}")
    return PARQUET_PATH


GRADE_BANDS = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (40, "D"),
    (0,  "F"),
]

# Minimum number of rated complaints across the entire dataset for a category
# to be included in scoring.
MIN_RATED_THRESHOLD = 1000

# Maximum number of categories to score (top N by rated complaint count).
MAX_SCORABLE_CATEGORIES = 6


def grade(score: float) -> str:
    for threshold, letter in GRADE_BANDS:
        if score >= threshold:
            return letter
    return "E"


def _key(prefix: tuple, *parts) -> tuple | str:
    """Build a lookup key; unwrap to a plain value when the result is length-1."""
    full = prefix + parts
    return full[0] if len(full) == 1 else full


def build_subjects(
    scorable_categories: list[str],
    rated_agg,
    sub_rated_agg,
    sub_rated_order,
    key_prefix: tuple,          # (ward,) or () for city-level
    total_counts,
    sub_total_counts,
    sub_rating_dist: dict,
) -> list[dict]:
    """Build the subjects list for one card (ward or city)."""
    subjects = []
    for cat in scorable_categories:
        cat_key = _key(key_prefix, cat)
        total = int(total_counts.get(cat_key, 0))

        if cat_key in rated_agg.index:
            row = rated_agg.loc[cat_key]
            rated_count = int(row["rated_count"])
            avg_rating = round(float(row["avg_rating"]), 2)
            marks = round((avg_rating - 1) * 25, 1)
            cat_grade = grade(marks)
        else:
            rated_count = 0
            avg_rating = None
            marks = None
            cat_grade = None

        cat_subs_order = (
            sub_rated_order[sub_rated_order["category"] == cat]
            .sort_values("n", ascending=False)["sub_category"]
            .tolist()
        )
        subcategories = []
        for sub in cat_subs_order:
            sub_key = _key(key_prefix, cat, sub)
            sub_total = int(sub_total_counts.get(sub_key, 0))
            if sub_key in sub_rated_agg.index:
                sub_row = sub_rated_agg.loc[sub_key]
                sub_rated = int(sub_row["rated_count"])
                sub_avg = round(float(sub_row["avg_rating"]), 2)
                sub_marks = round((sub_avg - 1) * 25, 1)
                sub_grade = grade(sub_marks)
            else:
                sub_rated = 0
                sub_avg = None
                sub_marks = None
                sub_grade = None
            dist_key = _key(key_prefix, cat, sub)
            rating_dist = sub_rating_dist.get(dist_key, {})
            subcategories.append({
                "sub_category": sub,
                "complaint_count": sub_total,
                "rated_count": sub_rated,
                "avg_rating": sub_avg,
                "marks": sub_marks,
                "grade": sub_grade,
                "rating_distribution": {str(k): v for k, v in sorted(rating_dist.items())},
            })

        subjects.append({
            "category": cat,
            "complaint_count": total,
            "rated_count": rated_count,
            "avg_rating": avg_rating,
            "marks": marks,
            "max_marks": 100,
            "grade": cat_grade,
            "subcategories": subcategories,
        })

    return subjects


def score_subjects(subjects: list[dict]) -> tuple[float, int, float, str | None]:
    scored = [s for s in subjects if s["marks"] is not None]
    total_marks = round(sum(s["marks"] for s in scored), 1)
    max_possible = len(scored) * 100
    percentage = round(total_marks / max_possible * 100, 2) if max_possible else 0.0
    overall_grade = grade(percentage) if max_possible else None
    return total_marks, max_possible, percentage, overall_grade


def load_area_mapping() -> dict[str, list[str]]:
    with open(AREA_MAPPING_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_ward_aliases() -> dict[str, str]:
    """data ward_name → canonical GeoJSON/KML ward name (only differing names)."""
    with open(WARD_ALIAS_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_report_cards(parquet_path: str) -> tuple[list[dict], dict, list[dict], list[str]]:
    df = pd.read_parquet(parquet_path)
    df = df[df["ward_name"] != "NON Ward"]

    # Work only with complaints that have ratings
    rated = df[df["rating"].notna()].copy()
    rated = rated.assign(rating=rated["rating"].astype(float))

    # Scorable categories: top MAX_SCORABLE_CATEGORIES by rated complaint count,
    # requiring at least MIN_RATED_THRESHOLD rated complaints each.
    rated_per_category = rated.groupby("category").size()
    eligible = sorted(
        (c for c in df["category"].dropna().unique()
         if rated_per_category.get(c, 0) >= MIN_RATED_THRESHOLD),
        key=lambda c: -rated_per_category[c],
    )
    scorable_categories = sorted(eligible[:MAX_SCORABLE_CATEGORIES])

    # Subcategories per category (ordered by dataset-wide rated count, descending)
    sub_rated_order = (
        rated.groupby(["category", "sub_category"])
        .size()
        .reset_index(name="n")
    )

    # --- Ward-level aggregations (keyed by (ward, category) etc.) ---
    ward_complaint_counts = rated.groupby("ward_name").size()
    ward_rated_agg = (
        rated.groupby(["ward_name", "category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )
    ward_total_counts = df.groupby(["ward_name", "category"]).size().rename("total")
    ward_sub_total_counts = (
        df.groupby(["ward_name", "category", "sub_category"]).size().rename("total")
    )
    ward_sub_rated_agg = (
        rated.groupby(["ward_name", "category", "sub_category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )

    # --- Area mapping ---
    area_mapping = load_area_mapping()
    aliases = load_ward_aliases()
    ward_to_area = {ward: area for area, wards in area_mapping.items() for ward in wards}
    # data ward names differ in spelling from the area mapping (GeoJSON names);
    # canonicalise via the alias table before resolving the area.
    data_ward_to_area = {
        ward: ward_to_area.get(aliases.get(ward, ward))
        for ward in df["ward_name"].dropna().unique()
    }
    df_area = df.assign(area_name=df["ward_name"].map(data_ward_to_area))
    rated_area = rated.assign(area_name=rated["ward_name"].map(data_ward_to_area))

    # --- Rating distribution per subcategory ---
    rated_int = rated.assign(rating_int=rated["rating"].astype(int))
    rated_int_area = rated_area.assign(rating_int=rated_area["rating"].astype(int))
    city_sub_rd: dict = {}
    for (cat, sub, r), cnt in (
        rated_int.groupby(["category", "sub_category", "rating_int"]).size().items()
    ):
        city_sub_rd.setdefault((cat, sub), {})[r] = int(cnt)
    ward_sub_rd: dict = {}
    for (ward, cat, sub, r), cnt in (
        rated_int.groupby(["ward_name", "category", "sub_category", "rating_int"]).size().items()
    ):
        ward_sub_rd.setdefault((ward, cat, sub), {})[r] = int(cnt)
    area_sub_rd: dict = {}
    for (area, cat, sub, r), cnt in (
        rated_int_area.dropna(subset=["area_name"])
        .groupby(["area_name", "category", "sub_category", "rating_int"])
        .size()
        .items()
    ):
        area_sub_rd.setdefault((area, cat, sub), {})[r] = int(cnt)

    # --- Area-level aggregations (keyed by (area, category) etc.) ---
    area_complaint_counts = rated_area.dropna(subset=["area_name"]).groupby("area_name").size()
    area_rated_agg = (
        rated_area.dropna(subset=["area_name"])
        .groupby(["area_name", "category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )
    area_total_counts = (
        df_area.dropna(subset=["area_name"])
        .groupby(["area_name", "category"]).size().rename("total")
    )
    area_sub_total_counts = (
        df_area.dropna(subset=["area_name"])
        .groupby(["area_name", "category", "sub_category"]).size().rename("total")
    )
    area_sub_rated_agg = (
        rated_area.dropna(subset=["area_name"])
        .groupby(["area_name", "category", "sub_category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )

    # --- City-level aggregations (keyed by (category,) etc.) ---
    city_rated_agg = (
        rated.groupby(["category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )
    city_total_counts = df.groupby(["category"]).size().rename("total")
    city_sub_total_counts = (
        df.groupby(["category", "sub_category"]).size().rename("total")
    )
    city_sub_rated_agg = (
        rated.groupby(["category", "sub_category"])["rating"]
        .agg(rated_count="count", avg_rating="mean")
    )

    # Build city card
    city_subjects = build_subjects(
        scorable_categories, city_rated_agg, city_sub_rated_agg,
        sub_rated_order, (), city_total_counts, city_sub_total_counts, city_sub_rd,
    )
    city_total_marks, city_max_possible, city_percentage, city_grade = score_subjects(city_subjects)
    city_card = {
        "complaint_count": int(len(rated)),
        "rank": None,
        "total_marks": city_total_marks,
        "max_possible_marks": city_max_possible,
        "categories_scored": sum(1 for s in city_subjects if s["marks"] is not None),
        "categories_total": len(scorable_categories),
        "percentage": city_percentage,
        "grade": city_grade,
        "subjects": city_subjects,
    }

    # Build ward cards
    report_cards = []
    for ward in sorted(df["ward_name"].dropna().unique()):
        subjects = build_subjects(
            scorable_categories, ward_rated_agg, ward_sub_rated_agg,
            sub_rated_order, (ward,), ward_total_counts, ward_sub_total_counts, ward_sub_rd,
        )
        total_marks, max_possible, percentage, overall_grade = score_subjects(subjects)
        report_cards.append({
            "ward_name": ward,
            "complaint_count": int(ward_complaint_counts.get(ward, 0)),
            "rank": None,
            "total_marks": total_marks,
            "max_possible_marks": max_possible,
            "categories_scored": sum(1 for s in subjects if s["marks"] is not None),
            "categories_total": len(scorable_categories),
            "percentage": percentage,
            "grade": overall_grade,
            "subjects": subjects,
        })

    # Rank wards: higher percentage = better rank; ties broken alphabetically
    report_cards.sort(key=lambda r: (-r["percentage"], r["ward_name"]))
    for i, card in enumerate(report_cards, start=1):
        card["rank"] = i

    # Restore alphabetical order for the final file (rank is embedded in each card)
    report_cards.sort(key=lambda r: r["ward_name"])

    # Build area cards
    area_cards = []
    for area_name, ward_names in sorted(area_mapping.items()):
        subjects = build_subjects(
            scorable_categories, area_rated_agg, area_sub_rated_agg,
            sub_rated_order, (area_name,), area_total_counts, area_sub_total_counts, area_sub_rd,
        )
        total_marks, max_possible, percentage, overall_grade = score_subjects(subjects)
        area_cards.append({
            "area_name": area_name,
            "ward_names": ward_names,
            "complaint_count": int(area_complaint_counts.get(area_name, 0)),
            "rank": None,
            "total_marks": total_marks,
            "max_possible_marks": max_possible,
            "categories_scored": sum(1 for s in subjects if s["marks"] is not None),
            "categories_total": len(scorable_categories),
            "percentage": percentage,
            "grade": overall_grade,
            "subjects": subjects,
        })

    # Rank areas: higher percentage = better rank; ties broken alphabetically
    area_cards.sort(key=lambda r: (-r["percentage"], r["area_name"]))
    for i, card in enumerate(area_cards, start=1):
        card["rank"] = i

    # Restore alphabetical order
    area_cards.sort(key=lambda r: r["area_name"])

    return report_cards, city_card, area_cards, scorable_categories


def main():
    parquet_path = ensure_parquet_file()
    output_path = Path("static/results.json")

    print("Loading data...")
    report_cards, city_card, area_cards, scorable_categories = build_report_cards(parquet_path)

    output = {
        "metadata": {
            "total_wards": len(report_cards),
            "total_areas": len(area_cards),
        },
        "city": city_card,
        "wards": report_cards,
        "areas": area_cards,
    }

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()
