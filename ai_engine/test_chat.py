# from dotenv import load_dotenv
# load_dotenv()

# from ai_engine.llm_integration import DigitalTwinAdvisor

# advisor = DigitalTwinAdvisor(user_id=1)

# advisor.set_context(
#     user_profile={"name": "Alex", "age": 25, "occupation": "Student"},
#     financial_summary={
#         "current_savings": 15420,
#         "projected_savings_1y": 24800,
#         "savings_rate": 20
#     },
#     study_summary={
#         "avg_weekly_hours": 12,
#         "performance_trend": "improving"
#     },
#     habits=[
#         {"habit_name": "Exercise", "status": "active", "completion_rate": 85}
#     ],
#     goals=[
#         {"goal_name": "Emergency Fund", "current_progress": 15000,
#          "target_value": 20000, "target_date": "2026-12-31"}
#     ]
# )

# # Interactive loop so you can test multiple questions
# print("Digital Twin AI ready. Type 'exit' to quit.\n")
# while True:
#     user_input = input("You: ")
#     if user_input.lower() == "exit":
#         break
#     reply = advisor.ask(user_input)
#     print(f"\nDigital Twin AI: {reply}\n")

from dotenv import load_dotenv
load_dotenv()

from ai_engine.llm_integration import DigitalTwinAdvisor
from ai_engine.forecasting.financial import get_financial_summary
from ai_engine.forecasting.habits import get_study_summary

advisor = DigitalTwinAdvisor(user_id=1)

advisor.set_context(
    user_profile={"name": "Alex", "age": 25, "occupation": "Student"},
    financial_summary=get_financial_summary(1),
    study_summary=get_study_summary(1),
    habits=[{"habit_name": "Exercise", "status": "active", "completion_rate": 85}],
    goals=[{"goal_name": "Emergency Fund", "current_progress": 15000,
            "target_value": 20000, "target_date": "2026-12-31"}]
)

print("Digital Twin AI ready. Type 'exit' to quit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    reply = advisor.ask(user_input)
    print(f"\nDigital Twin AI: {reply}\n")