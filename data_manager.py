import json
from pathlib import Path

FILE_PATH = Path(__file__).parent / "data" / "planner.json"


def load_data():
    if not FILE_PATH.exists():
        data = {"subjects": []}
        save_data(data)
        return data

    with FILE_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("planner.json must contain a JSON object.")

    if "subjects" not in data or not isinstance(data["subjects"], list):
        data["subjects"] = []
        save_data(data)

    return data


def save_data(data):
    FILE_PATH.parent.mkdir(exist_ok=True)

    with FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)