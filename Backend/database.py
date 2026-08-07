from pathlib import Path
from typing import Dict, List

import pandas as pd

# ==========================================================
# LOAD STUDENT DATABASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR.parent / "data" / "students.csv"

students = pd.read_csv(CSV_PATH)

# ==========================================================
# COLUMN MAP
# ==========================================================

COLUMN_MAP = {
    "roll": "Roll No.",
    "name": "Student Name",
    "course": "Course",
    "semester": "Semester",
    "stream": "Stream",
    "section": "Section",
}

# ==========================================================
# SEARCH WEIGHTS
# ==========================================================

SEARCH_WEIGHTS = {
    "roll": 100,
    "name": 50,
    "course": 20,
    "semester": 15,
    "stream": 15,
    "section": 10,
}

# ==========================================================
# RETURN STUDENT BY INDEX
# ==========================================================

def get_student(index: int) -> Dict:

    row = students.iloc[index]

    return {
        "name": row["Student Name"],
        "roll": row["Roll No."],
        "course": row["Course"],
        "semester": row["Semester"],
        "stream": row["Stream"],
        "section": row["Section"],
        "photo": row["Photo"],
    }


# ==========================================================
# CLEAN VALUE
# ==========================================================

def normalize(value):

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


# ==========================================================
# SCORE A SINGLE FIELD
# ==========================================================

def score_field(
    query: str,
    candidate: str,
    weight: int,
    exact_only: bool = False,
):

    query = normalize(query)
    candidate = normalize(candidate)

    if query == "":
        return 0

    if exact_only:

        if query == candidate:
            return weight

        return 0

    # Exact match

    if query == candidate:
        return weight

    # Starts with

    if candidate.startswith(query):
        return int(weight * 0.90)

    # Partial match

    if query in candidate:
        return int(weight * 0.75)

    return 0


# ==========================================================
# SCORE STUDENT
# ==========================================================

def score_student(
    row,
    filters: Dict,
):

    score = 0

    score += score_field(
        filters.get("roll", ""),
        row["Roll No."],
        SEARCH_WEIGHTS["roll"],
        exact_only=True,
    )

    score += score_field(
        filters.get("name", ""),
        row["Student Name"],
        SEARCH_WEIGHTS["name"],
    )

    score += score_field(
        filters.get("course", ""),
        row["Course"],
        SEARCH_WEIGHTS["course"],
    )

    score += score_field(
        filters.get("semester", ""),
        row["Semester"],
        SEARCH_WEIGHTS["semester"],
        exact_only=True,
    )

    score += score_field(
        filters.get("stream", ""),
        row["Stream"],
        SEARCH_WEIGHTS["stream"],
    )

    score += score_field(
        filters.get("section", ""),
        row["Section"],
        SEARCH_WEIGHTS["section"],
        exact_only=True,
    )

    return score



# ==========================================================
# SEARCH BEST MATCHES
# ==========================================================

def search_best_matches(
    filters: Dict,
    limit: int = 20,
) -> List[Dict]:

    results = []

    # Normalize filters once
    cleaned_filters = {
        key: normalize(value)
        for key, value in filters.items()
    }

    for _, row in students.iterrows():

        score = score_student(
            row,
            cleaned_filters,
        )

        if score == 0:
            continue

        results.append(
            {
                "score": score,
                "name": row["Student Name"],
                "roll": row["Roll No."],
                "course": row["Course"],
                "semester": row["Semester"],
                "stream": row["Stream"],
                "section": row["Section"],
                "photo": row["Photo"],
            }
        )

    results.sort(
        key=lambda x: (
            x["score"],
            x["name"]
        ),
        reverse=True,
    )

    return results[:limit]


# ==========================================================
# SEARCH STATISTICS (OPTIONAL)
# ==========================================================

def total_students():

    return len(students)


def total_matches(filters: Dict):

    return len(
        search_best_matches(
            filters,
            limit=len(students),
        )
    )


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    filters = {
        "roll": "",
        "name": "rahul",
        "course": "",
        "semester": "",
        "stream": "",
        "section": "",
    }

    matches = search_best_matches(filters)

    print(f"\nFound {len(matches)} students\n")

    for student in matches:

        print(
            f"{student['score']:>3} | "
            f"{student['name']} | "
            f"{student['roll']}"
        )

