import json
from pathlib import Path


FILE_PATH = Path(__file__).parent / "data" / "planner.json"


def migrate_data(data):
    """
    Convert the old subject/topic structure into
    the new subject/paper/topic structure.
    """

    changed = False

    if "subjects" not in data or not isinstance(data["subjects"], list):
        data["subjects"] = []
        changed = True

    for subject in data["subjects"]:

        # New structure already exists
        if "papers" in subject:
            continue

        old_topics = subject.get("topics", [])
        old_exam_date = subject.get("exam_date")

        subject["papers"] = [
            {
                "name": "General",
                "code": "",
                "exam_date": old_exam_date,
                "topics": old_topics
            }
        ]

        # Remove old structure
        subject.pop("topics", None)
        subject.pop("exam_date", None)

        changed = True

    return data, changed


def load_data():
    if not FILE_PATH.exists():
        data = {
            "subjects": []
        }

        save_data(data)

        return data

    with FILE_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "planner.json must contain a JSON object."
        )

    data, changed = migrate_data(data)

    if changed:
        save_data(data)

    return data


def save_data(data):
    FILE_PATH.parent.mkdir(exist_ok=True)

    with FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4
        )