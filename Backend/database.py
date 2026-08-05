from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR.parent / "data" / "students.csv"

students = pd.read_csv(CSV_PATH)


def get_student(index):

    row = students.iloc[index]

    return {
        "name": row["Student Name"],
        "roll": row["Roll No."],
        "course": row["Course"],
        "semester": row["Semester"],
        "stream": row["Stream"],
        "section": row["Section"],
        "photo": row["Photo"]
    }