def add_subject(data, name):
    name = name.strip()

    if not name:
        raise ValueError("Subject name cannot be empty.")

    for subject in data["subjects"]:
        if subject["name"].casefold() == name.casefold():
            raise ValueError("Subject already exists.")

    data["subjects"].append({
        "name": name,
        "papers": []
    })


def add_paper(
    data,
    subject_name,
    paper_name,
    exam_date=None,
    code=""
):
    paper_name = paper_name.strip()
    code = code.strip()

    if not paper_name:
        raise ValueError("Paper name cannot be empty.")

    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if paper["name"].casefold() == paper_name.casefold():
                    raise ValueError("Paper already exists.")

            subject["papers"].append({
                "name": paper_name,
                "code": code,
                "exam_date": exam_date,
                "topics": []
            })

            return

    raise ValueError("Subject not found.")


def add_topic(
    data,
    subject_name,
    paper_name,
    topic_name,
    difficulty,
    importance,
    estimated_hours
):
    topic_name = topic_name.strip()

    if not topic_name:
        raise ValueError("Topic name cannot be empty.")

    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if paper["name"] == paper_name:

                    for topic in paper["topics"]:

                        if topic["name"].casefold() == topic_name.casefold():
                            raise ValueError(
                                "Topic already exists."
                            )

                    paper["topics"].append({
                        "name": topic_name,
                        "difficulty": difficulty,
                        "importance": importance,
                        "estimated_hours": estimated_hours,
                        "completed": False
                    })

                    return

    raise ValueError("Paper not found.")


def set_topic_completed(
    data,
    subject_name,
    paper_name,
    topic_name,
    completed
):
    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if paper["name"] == paper_name:

                    for topic in paper["topics"]:

                        if topic["name"] == topic_name:

                            topic["completed"] = completed
                            return

    raise ValueError("Topic not found.")


def calculate_progress(paper):
    topics = paper["topics"]

    if not topics:
        return 0

    completed_topics = sum(
        topic["completed"]
        for topic in topics
    )

    return completed_topics / len(topics)