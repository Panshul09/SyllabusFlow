def add_subject(data, name):
    name = name.strip()

    if not name:
        raise ValueError("Subject name cannot be empty.")

    for subject in data["subjects"]:
        if subject["name"].casefold() == name.casefold():
            raise ValueError("Subject already exists.")

    data["subjects"].append({
        "name": name,
        "exam_date": None,
        "topics": []
    })


def add_topic(data, subject_name, topic_name):
    topic_name = topic_name.strip()

    if not topic_name:
        raise ValueError("Topic name cannot be empty.")

    for subject in data["subjects"]:
        if subject["name"] == subject_name:
            subject["topics"].append({
                "name": topic_name,
                "difficulty": 3,
                "importance": 3,
                "estimated_hours": 1,
                "completed": False
            })
            return

    raise ValueError("Subject not found.")