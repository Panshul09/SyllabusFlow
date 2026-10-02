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

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        return (
            "AI is not configured yet."
        )


    client = OpenAI(
        api_key=api_key
    )


    planner_summary = []


    for subject in data["subjects"]:

        papers = []


        for paper in subject["papers"]:

            topics = []


            for topic in paper["topics"]:

                topics.append({
                    "name": topic["name"],
                    "difficulty": topic["difficulty"],
                    "importance": topic["importance"],
                    "estimated_hours": topic["estimated_hours"],
                    "completed": topic["completed"]
                })


            papers.append({
                "name": paper["name"],
                "code": paper["code"],
                "exam_date": paper["exam_date"],
                "topics": topics
            })


        planner_summary.append({
            "subject": subject["name"],
            "papers": papers
        })


    prompt = f"""
You are a helpful A-Level study coach.

Analyze the student's study planner.

Identify:
1. Papers that need the most attention.
2. Difficult or important unfinished topics.
3. Papers with significant remaining workload.
4. Practical next steps.

Do not invent information.

Planner data:
{planner_summary}
"""


    try:

        response = client.responses.create(
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-6-luna"
            ),
            instructions=(
                "Give clear, concise and practical "
                "A-Level study advice."
            ),
            input=prompt
        )

        return response.output_text


    except RateLimitError:

        return (
            "The AI service is currently unavailable "
            "because the API account has reached its "
            "usage or credit limit."
        )


    except AuthenticationError:

        return (
            "The AI API key is invalid or unavailable. "
            "Check your API configuration."
        )


    except APIConnectionError:

        return (
            "Could not connect to the AI service. "
            "Check your internet connection."
        )


    except Exception:

        return (
            "Something went wrong while requesting "
            "AI advice. Please try again later."
        )