from datetime import date


def calculate_urgency(exam_date, today=None):
    """
    Convert the number of days until an exam into an urgency score from 1-5.
    """

    if today is None:
        today = date.today()

    if not exam_date:
        return 1

    exam = date.fromisoformat(exam_date)
    days_left = (exam - today).days

    if days_left <= 7:
        return 5
    elif days_left <= 14:
        return 4
    elif days_left <= 30:
        return 3
    elif days_left <= 60:
        return 2
    else:
        return 1


def calculate_priority(topic, exam_date, today=None):
    """
    Calculate a priority score for a topic.
    Higher score = higher priority.
    """

    urgency = calculate_urgency(exam_date, today)

    score = (
        topic["difficulty"] * 0.30
        + topic["importance"] * 0.30
        + urgency * 0.40
    )

    return score


def generate_schedule(data, available_hours, today=None):
    """
    Generate a study schedule using the highest-priority incomplete topics.
    """

    if today is None:
        today = date.today()

    topics = []

    for subject in data["subjects"]:

        for topic in subject["topics"]:

            if topic["completed"]:
                continue

            priority = calculate_priority(
                topic,
                subject["exam_date"],
                today
            )

            topics.append({
                "subject": subject["name"],
                "topic": topic["name"],
                "hours": topic["estimated_hours"],
                "priority": priority
            })

    topics.sort(
        key=lambda topic: topic["priority"],
        reverse=True
    )

    schedule = []
    remaining_hours = available_hours

    for topic in topics:

        if remaining_hours <= 0:
            break

        study_hours = min(
            topic["hours"],
            remaining_hours
        )

        schedule.append({
            "subject": topic["subject"],
            "topic": topic["topic"],
            "hours": study_hours,
            "priority": topic["priority"]
        })

        remaining_hours -= study_hours

    return schedule