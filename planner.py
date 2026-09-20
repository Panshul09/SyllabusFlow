def add_subject(data, name, exam_date=None):
    name = name.strip()

    if not name:
        raise ValueError("Subject name cannot be empty.")

    for subject in data["subjects"]:
        if subject["name"].casefold() == name.casefold():
            raise ValueError("Subject already exists.")

    data["subjects"].append({
        "name": name,
        "exam_date": exam_date,
        "topics": []
    })


def add_topic(data, subject_name, topic_name, difficulty, importance, estimated_hours):
    topic_name = topic_name.strip()

    if not topic_name:
        raise ValueError("Topic name cannot be empty.")

    for subject in data["subjects"]:
        if subject["name"] == subject_name:

            for topic in subject["topics"]:
                if topic["name"].casefold() == topic_name.casefold():
                    raise ValueError("Topic already exists.")

            subject["topics"].append({
                "name": topic_name,
                "difficulty": difficulty,
                "importance": importance,
                "estimated_hours": estimated_hours,
                "completed": False
            })

            return

    raise ValueError("Subject not found.")
def set_topic_completed(data, subject_name, topic_name, completed):
    """
    Change the completion status of a topic.
    """

    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for topic in subject["topics"]:

                if topic["name"] == topic_name:
                    topic["completed"] = completed
                    return

    raise ValueError("Topic not found.")
def calculate_progress(subject):
    """
    Return the percentage of completed topics in a subject.
    """

    topics = subject["topics"]

    if not topics:
        return 0

    completed_topics = sum(
        topic["completed"]
        for topic in topics
    )

    return completed_topics / len(topics)