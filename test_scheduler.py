from data_manager import load_data
from scheduler import generate_schedule


data = load_data()

schedule = generate_schedule(
    data,
    available_hours=4
)

print("\nToday's Study Schedule:\n")

for item in schedule:
    print(
        f"{item['subject']} - "
        f"{item['topic']} - "
        f"{item['hours']}h - "
        f"Priority: {item['priority']:.2f}"
    )