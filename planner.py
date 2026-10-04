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
def delete_subject(data, subject_name):
    for index, subject in enumerate(data["subjects"]):

        if subject["name"] == subject_name:
            data["subjects"].pop(index)
            return

    raise ValueError("Subject not found.")


def delete_paper(data, subject_name, paper_name):
    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for index, paper in enumerate(subject["papers"]):

                if paper["name"] == paper_name:
                    subject["papers"].pop(index)
                    return

            raise ValueError("Paper not found.")

    raise ValueError("Subject not found.")


def delete_topic(
    data,
    subject_name,
    paper_name,
    topic_name
):
    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if paper["name"] == paper_name:

                    for index, topic in enumerate(paper["topics"]):

                        if topic["name"] == topic_name:
                            paper["topics"].pop(index)
                            return

                    raise ValueError("Topic not found.")

            raise ValueError("Paper not found.")

    raise ValueError("Subject not found.")

def edit_subject(
    data,
    old_name,
    new_name
):
    new_name = new_name.strip()

    if not new_name:
        raise ValueError(
            "Subject name cannot be empty."
        )

    for subject in data["subjects"]:

        if subject["name"].casefold() == new_name.casefold():

            if subject["name"] != old_name:
                raise ValueError(
                    "Subject already exists."
                )

    for subject in data["subjects"]:

        if subject["name"] == old_name:
            subject["name"] = new_name
            return

    raise ValueError("Subject not found.")


def edit_paper(
    data,
    subject_name,
    old_name,
    new_name,
    new_code,
    new_exam_date
):
    new_name = new_name.strip()
    new_code = new_code.strip()

    if not new_name:
        raise ValueError(
            "Paper name cannot be empty."
        )

    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if (
                    paper["name"].casefold()
                    == new_name.casefold()
                    and paper["name"] != old_name
                ):
                    raise ValueError(
                        "Paper already exists."
                    )

            for paper in subject["papers"]:

                if paper["name"] == old_name:

                    paper["name"] = new_name
                    paper["code"] = new_code
                    paper["exam_date"] = new_exam_date

                    return

            raise ValueError("Paper not found.")

    raise ValueError("Subject not found.")


def edit_topic(
    data,
    subject_name,
    paper_name,
    old_name,
    new_name,
    difficulty,
    importance,
    estimated_hours
):
    new_name = new_name.strip()

    if not new_name:
        raise ValueError(
            "Topic name cannot be empty."
        )

    for subject in data["subjects"]:

        if subject["name"] == subject_name:

            for paper in subject["papers"]:

                if paper["name"] == paper_name:

                    for topic in paper["topics"]:

                        if (
                            topic["name"].casefold()
                            == new_name.casefold()
                            and topic["name"] != old_name
                        ):
                            raise ValueError(
                                "Topic already exists."
                            )

                    for topic in paper["topics"]:

                        if topic["name"] == old_name:

                            topic["name"] = new_name
                            topic["difficulty"] = difficulty
                            topic["importance"] = importance
                            topic["estimated_hours"] = estimated_hours

                            return

                    raise ValueError(
                        "Topic not found."
                    )

            raise ValueError(
                "Paper not found."
            )

    raise ValueError(
        "Subject not found."
    )

def move_topic(
    data,
    subject_name,
    source_paper_name,
    topic_name,
    target_paper_name
):
    source_paper = None
    target_paper = None
    topic_to_move = None

    for subject in data["subjects"]:

        if subject["name"] != subject_name:
            continue

        for paper in subject["papers"]:

            if paper["name"] == source_paper_name:
                source_paper = paper

            if paper["name"] == target_paper_name:
                target_paper = paper

    if source_paper is None:
        raise ValueError(
            "Source paper not found."
        )

    if target_paper is None:
        raise ValueError(
            "Target paper not found."
        )

    if source_paper_name == target_paper_name:
        raise ValueError(
            "Source and target papers must be different."
        )

    for topic in source_paper["topics"]:

        if topic["name"] == topic_name:
            topic_to_move = topic
            break

    if topic_to_move is None:
        raise ValueError(
            "Topic not found."
        )

    for topic in target_paper["topics"]:

        if (
            topic["name"].casefold()
            == topic_name.casefold()
        ):
            raise ValueError(
                "A topic with that name already exists in the target paper."
            )

    source_paper["topics"].remove(topic_to_move)

    target_paper["topics"].append(
        topic_to_move
    )