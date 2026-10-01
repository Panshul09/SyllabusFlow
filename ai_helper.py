import os

from dotenv import load_dotenv
from openai import (
    OpenAI,
    RateLimitError,
    AuthenticationError,
    APIConnectionError
)


load_dotenv()


def get_ai_study_advice(data):
    """
    Send the student's current planner data to the AI
    and return personalized study advice.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "AI is not configured yet. Add your OPENAI_API_KEY."

    client = OpenAI(api_key=api_key)

    planner_summary = []

    for subject in data["subjects"]:

        topics = []

        for topic in subject["topics"]:

            topics.append({
                "name": topic["name"],
                "difficulty": topic["difficulty"],
                "importance": topic["importance"],
                "estimated_hours": topic["estimated_hours"],
                "completed": topic["completed"]
            })

        planner_summary.append({
            "subject": subject["name"],
            "exam_date": subject["exam_date"],
            "topics": topics
        })

    prompt = f"""
You are a helpful A-Level study coach.

Analyze the student's study planner below.

Give:
1. The most important areas they should focus on.
2. Which subjects appear to need more attention.
3. Practical advice for using their available study time.
4. Two or three specific actions they can take next.

Do not invent information that isn't present in the planner.

Planner data:
{planner_summary}
"""

    try:

        response = client.responses.create(
            model="...",
            instructions=(
                "Give clear, concise, practical study advice "
                "for an A-Level student."
            ),
            input=prompt
        )

        return response.output_text

    except RateLimitError:

        return (
            "The AI service is currently unavailable "
            "because the API account has reached its usage "
            "or credit limit."
        )

    except AuthenticationError:

        return (
            "The AI API key is invalid or unavailable. "
            "Check your API key configuration."
        )

    except APIConnectionError:

        return (
            "Could not connect to the AI service. "
            "Check your internet connection and try again."
        )

    except Exception:

        return (
            "Something went wrong while requesting AI advice. "
            "Please try again later."
        )