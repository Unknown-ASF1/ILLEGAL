import pickle
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EMBEDDINGS_PATH = BASE_DIR / "embeddings" / "embeddings.pkl"

with open(EMBEDDINGS_PATH, "rb") as f:
    EMBEDDINGS = pickle.load(f)


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def recognize(face_embedding):

    best_score = -1
    best_index = None

    for item in EMBEDDINGS:

        score = cosine_similarity(
            face_embedding,
            item["embedding"]
        )

        if score > best_score:

            best_score = score
            best_index = item["index"]

    THRESHOLD = 0.55

    if best_score < THRESHOLD:
        return None, float(best_score)

    return best_index, float(best_score)