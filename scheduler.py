from datetime import date


def get_days_until_exam(exam_date, today=None):

    if today is None:
        today = date.today()

    if not exam_date:
        return None

    exam = date.fromisoformat(exam_date)

    return (exam - today).days


def calculate_urgency(exam_date, today=None):

    days_left = get_days_until_exam(
        exam_date,
        today
    )

    if days_left is None:
        return 1

    if days_left <= 0:
        return 5

    days_left = min(days_left, 60)

    return 5 - (days_left / 15)


def calculate_workload_pressure(
    paper,
    today=None
):

    days_left = get_days_until_exam(
        paper["exam_date"],
        today
    )

    if days_left is None:
        return 1

    remaining_hours = sum(
        topic["estimated_hours"]
        for topic in paper["topics"]
        if not topic["completed"]
    )

    if remaining_hours == 0:
        return 1

    effective_days = max(days_left, 1)

    hours_per_day = remaining_hours / effective_days

    pressure = 1 + hours_per_day

    return min(5, pressure)


def calculate_priority(
    topic,
    paper,
    today=None
):

    urgency = calculate_urgency(
        paper["exam_date"],
        today
    )

    workload_pressure = calculate_workload_pressure(
        paper,
        today
    )

    score = (
        topic["difficulty"] * 0.25
        + topic["importance"] * 0.25
        + urgency * 0.30
        + workload_pressure * 0.20
    )

    return score


def generate_schedule(
    data,
    available_hours,
    today=None
):

    if today is None:
        today = date.today()

    topics = []

    for subject in data["subjects"]:

            for paper in subject["papers"]:
                days_left = get_days_until_exam(
                    paper["exam_date"],
                    today
                )

                if days_left is not None and days_left < 0:
                    continue
            for topic in paper["topics"]:

                if topic["completed"]:
                    continue

                priority = calculate_priority(
                    topic,
                    paper,
                    today
                )

                topics.append({
                    "subject": subject["name"],
                    "paper": paper["name"],
                    "topic": topic["name"],
                    "hours": topic["estimated_hours"],
                    "priority": priority,
                    "days_left": get_days_until_exam(
                        paper["exam_date"],
                        today
                    )
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
            "paper": topic["paper"],
            "topic": topic["topic"],
            "hours": study_hours,
            "priority": topic["priority"],
            "days_left": topic["days_left"]
        })

        remaining_hours -= study_hours

    return schedule