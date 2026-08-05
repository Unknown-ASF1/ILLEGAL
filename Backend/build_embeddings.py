import requests
import cv2
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from Backend.face_engine import get_faces

# =====================================================
# SETTINGS
# =====================================================

# Change this to None when you want to process ALL students
LIMIT = None

SAVE_EVERY = 100

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR.parent / "data" / "students.csv"

EMBEDDINGS_DIR = BASE_DIR / "embeddings"
EMBEDDINGS_DIR.mkdir(exist_ok=True)

EMBEDDINGS_PATH = EMBEDDINGS_DIR / "embeddings.pkl"

# =====================================================
# LOAD CSV
# =====================================================

students = pd.read_csv(CSV_PATH)

if LIMIT is not None:
    students = students.head(LIMIT)

print(f"\nLoaded {len(students)} students.\n")

embeddings = []
skipped = []

# =====================================================
# PROCESS
# =====================================================

for i, row in tqdm(students.iterrows(), total=len(students)):

    try:

        # ----------------------------
        # Check Photo URL
        # ----------------------------

        photo = row.get("Photo")

        if pd.isna(photo):
            skipped.append((i, "Missing Photo"))
            continue

        photo = str(photo).strip()

        if photo == "":
            skipped.append((i, "Empty Photo URL"))
            continue

        # ----------------------------
        # Download Image
        # ----------------------------

        response = requests.get(photo, timeout=10)

        if response.status_code != 200:
            skipped.append((i, f"HTTP {response.status_code}"))
            continue

        arr = np.frombuffer(response.content, np.uint8)

        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if img is None:
            skipped.append((i, "Image Decode Failed"))
            continue

        # ----------------------------
        # Detect Face
        # ----------------------------

        faces = get_faces(img)

        if len(faces) == 0:
            skipped.append((i, "No Face Found"))
            continue

        # ----------------------------
        # Save Embedding
        # ----------------------------

        embeddings.append(
            {
                "index": i,
                "embedding": faces[0].embedding
            }
        )

        # ----------------------------
        # Save Progress Every 100 Students
        # ----------------------------

        if len(embeddings) % SAVE_EVERY == 0:

            with open(EMBEDDINGS_PATH, "wb") as f:
                pickle.dump(embeddings, f)

    except Exception as e:

        skipped.append((i, str(e)))

# =====================================================
# FINAL SAVE
# =====================================================

with open(EMBEDDINGS_PATH, "wb") as f:
    pickle.dump(embeddings, f)

print("\n===================================")
print("Embedding Generation Complete")
print("===================================")

print(f"Students Processed : {len(students)}")
print(f"Embeddings Created : {len(embeddings)}")
print(f"Skipped            : {len(skipped)}")

if skipped:

    print("\nFirst 20 skipped rows:\n")

    for item in skipped[:20]:
        print(item)