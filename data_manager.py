import json

FILE_PATH = "data/planner.json"


def load_data():
    with open(FILE_PATH, "r") as file:
        return json.load(file)


def save_data(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)