import requests

API_URL = "http://127.0.0.1:8000"


def recognize(image_file):
    files = {
        "file": image_file
    }

    response = requests.post(
        f"{API_URL}/recognize",
        files=files
    )

    return response.json()