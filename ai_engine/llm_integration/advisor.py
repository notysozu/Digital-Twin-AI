import os
import google.generativeai as genai
from typing import Dict, Any

def get_rule_based_advice(
    user_info: Dict[str, Any],
    baseline: Dict[str, Any],
    sim_results: Dict[str, Any]
) -> str:
    """
    Fallback high-quality rule-based advisor when no Gemini API key is configured.
    """
    sa = sim_results["scenario_a"]
    sb = sim_results["scenario_b"]
    
    advice = "### 🤖 Digital Twin Rule-Based Verdict\n\n"
    advice += "*(Note: Run with a valid LLM_API_KEY to enable full conversational intelligence.)*\n\n"
    
    # Analyze Scenario A
    advice += "#### **Analysis of Scenario A**\n"
    advice += f"- **Lifestyle changes:** Sleep: {sa['details']['sleep']:.1f} hrs, Study: {sa['details']['study_week']:.1f} hrs/week, Monthly Savings: ${sa['details']['monthly_savings']:.2f}.\n"
    advice += f"- **Wellbeing & Performance:** Health Index: {sa['health_index']:.1f}/10, Focus Rating: {sa['focus_index']:.1f}/10.\n"
    advice += f"- **Financial Projection:** Net Worth in 5 years: ${sa['wealth_at_end']:,.2f}. "
    if sa["attained_retirement"]:
        advice += "On track to reach retirement goals! 🎯\n"
    else:
        advice += f"Projected retirement wealth of ${sa['retirement_wealth']:,.2f} falls short of target (${user_info['target_net_worth']:,.2f}).\n"
        
    # Analyze Scenario B
    advice += "\n#### **Analysis of Scenario B**\n"
    advice += f"- **Lifestyle changes:** Sleep: {sb['details']['sleep']:.1f} hrs, Study: {sb['details']['study_week']:.1f} hrs/week, Monthly Savings: ${sb['details']['monthly_savings']:.2f}.\n"
    advice += f"- **Wellbeing & Performance:** Health Index: {sb['health_index']:.1f}/10, Focus Rating: {sb['focus_index']:.1f}/10.\n"
    advice += f"- **Financial Projection:** Net Worth in 5 years: ${sb['wealth_at_end']:,.2f}. "
    if sb["attained_retirement"]:
        advice += "On track to reach retirement goals! 🎯\n"
    else:
        advice += f"Projected retirement wealth of ${sb['retirement_wealth']:,.2f} falls short of target (${user_info['target_net_worth']:,.2f}).\n"
        
    # Compare
    advice += "\n#### **Tradeoff Analysis & Verdict**\n"
    
    # 1. Health Tradeoff
    sleep_diff = sb['details']['sleep'] - sa['details']['sleep']
    if sleep_diff > 0.5:
        advice += f"- **Health:** Scenario B prioritizes sleep by {sleep_diff:.1f} additional hours, yielding a better Health Index of **{sb['health_index']:.1f}/10** compared to Scenario A (**{sa['health_index']:.1f}/10**). Rest is critical for avoiding long-term cognitive burnout.\n"
    elif sleep_diff < -0.5:
        advice += f"- **Health:** Scenario A prioritizes sleep by {abs(sleep_diff):.1f} additional hours, yielding a better Health Index of **{sa['health_index']:.1f}/10** compared to Scenario B (**{sb['health_index']:.1f}/10**). Avoid cutting sleep short to hit financial targets.\n"
    else:
        advice += "- **Health:** Both scenarios maintain similar sleeping patterns.\n"
        
    # 2. Study Tradeoff
    study_diff = sb['details']['study_week'] - sa['details']['study_week']
    if study_diff > 1.0:
        advice += f"- **Studies:** Scenario B increases weekly study by {study_diff:.1f} hours, boosting focus performance to **{sb['focus_index']:.1f}/10**. This represents a strong commitment to learning and career pivoting.\n"
    elif study_diff < -1.0:
        advice += f"- **Studies:** Scenario A increases weekly study by {abs(study_diff):.1f} hours, boosting focus performance to **{sa['focus_index']:.1f}/10**.\n"
        
    # 3. Financial Tradeoff
    sav_diff = sb['details']['monthly_savings'] - sa['details']['monthly_savings']
    if sav_diff > 100:
        advice += f"- **Finances:** Scenario B saves ${sav_diff:,.2f} more monthly, leading to an extra ${sb['wealth_at_end'] - sa['wealth_at_end']:,.2f} in assets over the timeline. This accelerates compounding interest significantly.\n"
    elif sav_diff < -100:
        advice += f"- **Finances:** Scenario A saves ${abs(sav_diff):,.2f} more monthly, leading to an extra ${sa['wealth_at_end'] - sb['wealth_at_end']:,.2f} in assets over the timeline.\n"

    # Verdict
    advice += "\n#### **Digital Twin's Choice**\n"
    if sa['health_index'] < 5.0 and sb['health_index'] >= 5.0:
        advice += "💡 **Recommendation:** **Choose Scenario B.** Scenario A degrades your health index below a sustainable baseline. Short-term financial or study gains do not justify the cognitive toll of sleep deprivation.\n"
    elif sb['health_index'] < 5.0 and sa['health_index'] >= 5.0:
        advice += "💡 **Recommendation:** **Choose Scenario A.** Scenario B degrades your health index below a sustainable baseline due to sleep or habits neglect.\n"
    elif sb['wealth_at_end'] > sa['wealth_at_end'] and sb['health_index'] >= sa['health_index'] - 0.5:
        advice += "💡 **Recommendation:** **Choose Scenario B.** It provides superior financial growth without significantly damaging your lifestyle and health parameters.\n"
    else:
        advice += "💡 **Recommendation:** **Choose Scenario A.** It balances financial safety and performance score with sustainable health metrics.\n"
        
    return advice

def generate_digital_twin_advice(
    user_info: Dict[str, Any],
    baseline: Dict[str, Any],
    sim_results: Dict[str, Any]
) -> str:
    """
    Generate conversational recommendations using Gemini API, or fallback to rule-based logic.
    """
    api_key = os.getenv("LLM_API_KEY")
    
    # Fallback to rule-based advisor if no API key or placeholder
    if not api_key or "your_api_key" in api_key or api_key == "":
        return get_rule_based_advice(user_info, baseline, sim_results)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        sa = sim_results["scenario_a"]
        sb = sim_results["scenario_b"]
        
        prompt = f"""
You are the "Digital Twin Advisor" — an advanced AI assistant representing the digital twin of the user.
Your role is to analyze a comparative "What-If" lifestyle simulation and provide constructive, personalized advice to help the user choose the best path forward.

=== USER PROFILE ===
- Username: {user_info['username']}
- Current Age: {user_info['age']} years
- Target Retirement Age: {user_info['retirement_goal_age']} years
- Target Net Worth at Retirement: ${user_info['target_net_worth']:,.2f}
- Monthly Base Income: ${user_info['monthly_income']:,.2f}

=== PAST 30 DAYS BASELINE (CURRENT LIFESTYLE) ===
- Monthly Savings: ${baseline['monthly_savings']:,.2f}
- Current Net Worth: ${baseline['current_net_worth']:,.2f}
- Sleep: {baseline['sleep_hours']:.1f} hours/night
- Exercise: {baseline['exercise_hours'] * 60:.1f} minutes/day
- Screen Time: {baseline['screen_hours']:.1f} hours/day
- Weekly Study Hours: {baseline['study_hours_week']:.1f} hours/week

=== COMPARATIVE WHAT-IF SCENARIOS (PROJECTED RESULTS) ===

SCENARIO A (MODIFICATIONS):
- Adjustments: Monthly savings change: {sa['details']['monthly_savings'] - baseline['monthly_savings']:+.2f}, Sleep change: {sa['details']['sleep'] - baseline['sleep_hours']:+.1f} hrs, Study change: {sa['details']['study_week'] - baseline['study_hours_week']:+.1f} hrs/week
- Health Index (Well-being): {sa['health_index']:.1f}/10
- Focus Rating (Productivity): {sa['focus_index']:.1f}/10
- Net Worth Projection (Timeline End): ${sa['wealth_at_end']:,.2f}
- Will reach target net worth by retirement age? {"Yes" if sa['attained_retirement'] else "No"} (Projected retirement wealth: ${sa['retirement_wealth']:,.2f})

SCENARIO B (MODIFICATIONS):
- Adjustments: Monthly savings change: {sb['details']['monthly_savings'] - baseline['monthly_savings']:+.2f}, Sleep change: {sb['details']['sleep'] - baseline['sleep_hours']:+.1f} hrs, Study change: {sb['details']['study_week'] - baseline['study_hours_week']:+.1f} hrs/week
- Health Index (Well-being): {sb['health_index']:.1f}/10
- Focus Rating (Productivity): {sb['focus_index']:.1f}/10
- Net Worth Projection (Timeline End): ${sb['wealth_at_end']:,.2f}
- Will reach target net worth by retirement age? {"Yes" if sb['attained_retirement'] else "No"} (Projected retirement wealth: ${sb['retirement_wealth']:,.2f})

=== INSTRUCTIONS ===
Write a comprehensive report comparing Scenario A and Scenario B.
Ensure you address:
1. **Tradeoff Analysis**: Detail the compromises. For example, is one scenario cutting sleep to gain study/savings? Explain the biological or psychological consequence (e.g. sleep deprivation reduces focus rating).
2. **Financial Critique**: Assess their retirement trajectory. Under which scenario are they more financially secure? Is the increased savings rate worth the lifestyle impact?
3. **Recommendation & Verdict**: Pick one scenario as the clear winner and explain why, or suggest a hybrid approach (Scenario C) that would optimize their goals.

Output the analysis in clean, professional markdown with beautiful emojis. Keep it concise, engaging, and directly addressed to the user.
"""
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}. Falling back to rule-based advice.")
        return get_rule_based_advice(user_info, baseline, sim_results)

# import os
# from google import genai
# from google.genai import types

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=GEMINI_API_KEY)


# def build_system_prompt(user_profile: dict, financial_summary: dict,
#                          study_summary: dict, habits: list, goals: list) -> str:
#     """
#     financial_summary, study_summary come from ai_engine/forecasting/financial.py & habits.py
#     goals/habits come from database layer
#     """
#     goals_text = "\n".join(
#         f"- {g['goal_name']}: {g['current_progress']}/{g['target_value']} by {g['target_date']}"
#         for g in goals
#     ) or "No active goals."

#     habits_text = "\n".join(
#         f"- {h['habit_name']}: {h['status']} ({h['completion_rate']}% completion)"
#         for h in habits
#     ) or "No tracked habits."

#     return f"""You are Digital Twin AI, a personal life simulation and decision assistant for {user_profile.get('name', 'the user')}.

# USER PROFILE:
# Age: {user_profile.get('age', 'N/A')}, Occupation: {user_profile.get('occupation', 'N/A')}

# FINANCIAL FORECAST:
# Current Savings: {financial_summary.get('current_savings', 'N/A')}
# Projected (1Y): {financial_summary.get('projected_savings_1y', 'N/A')}
# Monthly Savings Rate: {financial_summary.get('savings_rate', 'N/A')}%

# STUDY FORECAST:
# Avg Weekly Study Hours: {study_summary.get('avg_weekly_hours', 'N/A')}
# Predicted Performance Trend: {study_summary.get('performance_trend', 'N/A')}

# HABITS:
# {habits_text}

# GOALS:
# {goals_text}

# RULES:
# - Answer using ONLY the data above plus reasonable projections (compound savings, trend extrapolation).
# - When asked "will I achieve X", do the math explicitly (projected value vs target).
# - Give concrete, personalized, actionable recommendations — not generic advice.
# - Keep responses concise, structured, and forward-looking.
# - If data is insufficient, say so and ask what's missing.
# """


# class DigitalTwinAdvisor:
#     """
#     LLM-based conversational advisor. Consumes pre-computed forecasts/simulations
#     from other ai_engine modules instead of hitting the DB directly.
#     """

#     def __init__(self, user_id: int, model: str = "gemini-2.0-flash-lite"):
#         self.user_id = user_id
#         self.model = model
#         self.system_prompt = None
#         self.history = []  # [{"role": "user"/"model", "text": str}]

#     def set_context(self, user_profile: dict, financial_summary: dict,
#                      study_summary: dict, habits: list, goals: list):
#         """Call this once per session (or after data refresh) with data
#         gathered from forecasting/simulation modules + database layer."""
#         self.system_prompt = build_system_prompt(
#             user_profile, financial_summary, study_summary, habits, goals
#         )

#     def ask(self, user_message: str) -> str:
#         if self.system_prompt is None:
#             raise ValueError("Call set_context() before ask().")

#         contents = [
#             types.Content(role=t["role"], parts=[types.Part(text=t["text"])])
#             for t in self.history
#         ]
#         contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

#         response = client.models.generate_content(
#             model=self.model,
#             contents=contents,
#             config=types.GenerateContentConfig(
#                 system_instruction=self.system_prompt,
#                 temperature=0.4,
#                 max_output_tokens=800,
#             ),
#         )

#         reply = response.text
#         self.history.append({"role": "user", "text": user_message})
#         self.history.append({"role": "model", "text": reply})
#         return reply

#     def ask_with_simulation(self, user_message: str, scenario_result: dict) -> str:
#         """Use when the user asks about a specific simulated scenario
#         (output of ai_engine/simulation/simulator.py)."""
#         scenario_context = (
#             f"\n\nSIMULATION RESULT FOR THIS QUERY:\n"
#             f"Scenario: {scenario_result.get('scenario_name')}\n"
#             f"Predicted Outcome: {scenario_result.get('predicted_outcome')}\n"
#         )
#         return self.ask(user_message + scenario_context)
# import os
# from openai import OpenAI

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)


# def build_system_prompt(user_profile: dict, financial_summary: dict,
#                          study_summary: dict, habits: list, goals: list) -> str:
#     goals_text = "\n".join(
#         f"- {g['goal_name']}: {g['current_progress']}/{g['target_value']} by {g['target_date']}"
#         for g in goals
#     ) or "No active goals."

#     habits_text = "\n".join(
#         f"- {h['habit_name']}: {h['status']} ({h['completion_rate']}% completion)"
#         for h in habits
#     ) or "No tracked habits."

#     return f"""You are Digital Twin AI, a personal life simulation and decision assistant for {user_profile.get('name', 'the user')}.

# USER PROFILE:
# Age: {user_profile.get('age', 'N/A')}, Occupation: {user_profile.get('occupation', 'N/A')}

# FINANCIAL FORECAST:
# Current Savings: {financial_summary.get('current_savings', 'N/A')}
# Projected (1Y): {financial_summary.get('projected_savings_1y', 'N/A')}
# Monthly Savings Rate: {financial_summary.get('savings_rate', 'N/A')}%

# STUDY FORECAST:
# Avg Weekly Study Hours: {study_summary.get('avg_weekly_hours', 'N/A')}
# Predicted Performance Trend: {study_summary.get('performance_trend', 'N/A')}

# HABITS:
# {habits_text}

# GOALS:
# {goals_text}

# RULES:
# - Answer using ONLY the data above plus reasonable projections (compound savings, trend extrapolation).
# - When asked "will I achieve X", do the math explicitly (projected value vs target).
# - Give concrete, personalized, actionable recommendations — not generic advice.
# - Keep responses concise, structured, and forward-looking.
# - If data is insufficient, say so and ask what's missing.
# """


# class DigitalTwinAdvisor:
#     def __init__(self, user_id: int, model: str = "gpt-4o-mini"):
#         self.user_id = user_id
#         self.model = model
#         self.system_prompt = None
#         self.history = []  # [{"role": "user"/"assistant", "text": str}]

#     def set_context(self, user_profile: dict, financial_summary: dict,
#                      study_summary: dict, habits: list, goals: list):
#         self.system_prompt = build_system_prompt(
#             user_profile, financial_summary, study_summary, habits, goals
#         )

#     def ask(self, user_message: str) -> str:
#         if self.system_prompt is None:
#             raise ValueError("Call set_context() before ask().")

#         messages = [{"role": "system", "content": self.system_prompt}]
#         for t in self.history:
#             messages.append({"role": t["role"], "content": t["text"]})
#         messages.append({"role": "user", "content": user_message})

#         response = client.chat.completions.create(
#             model=self.model,
#             messages=messages,
#             temperature=0.4,
#             max_tokens=800,
#         )

#         reply = response.choices[0].message.content
#         self.history.append({"role": "user", "text": user_message})
#         self.history.append({"role": "assistant", "text": reply})
#         return reply

#     def ask_with_simulation(self, user_message: str, scenario_result: dict) -> str:
#         scenario_context = (
#             f"\n\nSIMULATION RESULT FOR THIS QUERY:\n"
#             f"Scenario: {scenario_result.get('scenario_name')}\n"
#             f"Predicted Outcome: {scenario_result.get('predicted_outcome')}\n"
#         )
#         return self.ask(user_message + scenario_context)

import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")


def build_system_prompt(user_profile: dict, financial_summary: dict,
                         study_summary: dict, habits: list, goals: list) -> str:
    """
    financial_summary, study_summary come from ai_engine/forecasting/financial.py & habits.py
    goals/habits come from database layer
    """
    goals_text = "\n".join(
        f"- {g['goal_name']}: {g['current_progress']}/{g['target_value']} by {g['target_date']}"
        for g in goals
    ) or "No active goals."

    habits_text = "\n".join(
        f"- {h['habit_name']}: {h['status']} ({h['completion_rate']}% completion)"
        for h in habits
    ) or "No tracked habits."

    return f"""You are Digital Twin AI, a personal life simulation and decision assistant for {user_profile.get('name', 'the user')}.

USER PROFILE:
Age: {user_profile.get('age', 'N/A')}, Occupation: {user_profile.get('occupation', 'N/A')}

FINANCIAL FORECAST:
Current Savings: {financial_summary.get('current_savings', 'N/A')}
Projected (1Y): {financial_summary.get('projected_savings_1y', 'N/A')}
Monthly Savings Rate: {financial_summary.get('savings_rate', 'N/A')}%

STUDY FORECAST:
Avg Weekly Study Hours: {study_summary.get('avg_weekly_hours', 'N/A')}
Predicted Performance Trend: {study_summary.get('performance_trend', 'N/A')}

HABITS:
{habits_text}

GOALS:
{goals_text}

RULES:
- Answer using ONLY the data above plus reasonable projections (compound savings, trend extrapolation).
- When asked "will I achieve X", do the math explicitly (projected value vs target).
- Give concrete, personalized, actionable recommendations — not generic advice.
- Keep responses concise, structured, and forward-looking.
- If data is insufficient, say so and ask what's missing.
"""


class DigitalTwinAdvisor:
    """
    LLM-based conversational advisor. Consumes pre-computed forecasts/simulations
    from other ai_engine modules instead of hitting the DB directly.
    Uses Groq's free API (Llama 3.1) - no billing required.
    """

    def __init__(self, user_id: int, model: str = "llama-3.1-8b-instant"):
        self.user_id = user_id
        self.model = model
        self.system_prompt = None
        self.history = []  # [{"role": "user"/"assistant", "text": str}]

    def set_context(self, user_profile: dict, financial_summary: dict,
                     study_summary: dict, habits: list, goals: list):
        """Call this once per session (or after data refresh) with data
        gathered from forecasting/simulation modules + database layer."""
        self.system_prompt = build_system_prompt(
            user_profile, financial_summary, study_summary, habits, goals
        )

    def ask(self, user_message: str) -> str:
        if self.system_prompt is None:
            raise ValueError("Call set_context() before ask().")

        if client is None:
            return "Groq AI Advisor is offline. Please configure a valid GROQ_API_KEY in your environment to enable conversational recommendations."

        messages = [{"role": "system", "content": self.system_prompt}]
        for t in self.history:
            messages.append({"role": t["role"], "content": t["text"]})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.4,
            max_tokens=800,
        )

        reply = response.choices[0].message.content
        self.history.append({"role": "user", "text": user_message})
        self.history.append({"role": "assistant", "text": reply})
        return reply

    def ask_with_simulation(self, user_message: str, scenario_result: dict) -> str:
        """Use when the user asks about a specific simulated scenario
        (output of ai_engine/simulation/simulator.py)."""
        scenario_context = (
            f"\n\nSIMULATION RESULT FOR THIS QUERY:\n"
            f"Scenario: {scenario_result.get('scenario_name')}\n"
            f"Predicted Outcome: {scenario_result.get('predicted_outcome')}\n"
        )
        return self.ask(user_message + scenario_context)