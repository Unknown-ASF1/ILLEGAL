import requests

API_URL = "https://florence-leasing-correspondence-mental.trycloudflare.com"


def recognize(image_bytes: bytes):
    files = {
        "file": ("photo.jpg", image_bytes, "image/jpeg")
    }
    response = requests.post(
        f"{API_URL}/recognize",
        files=files,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def search_students(filters: dict):
    response = requests.post(
        f"{API_URL}/search",
        json=filters,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def get_total_students():
    try:
        response = requests.get(f"{API_URL}/total", timeout=10)
        response.raise_for_status()
        return response.json().get("total", 0)
    except Exception:
        return 0