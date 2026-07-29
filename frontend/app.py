import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from components import api_client, charts
import httpx

st.set_page_config(
    page_title="Digital Twin AI",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for rich, premium dark mode aesthetics
st.markdown("""
<style>
    /* Styling cards and blocks */
    .stApp {
        background: #0B0C10;
        color: #F8F9FA;
    }
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        background: linear-gradient(135deg, #0D6EFD 0%, #6F42C1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: rgba(30, 30, 36, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(5px);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #A0A0AB;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8F9FA;
    }
    .advisor-box {
        background: rgba(111, 66, 193, 0.08);
        border-left: 5px solid #6F42C1;
        border-radius: 4px 12px 12px 4px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    /* Buttons styling */
    .stButton>button {
        background: linear-gradient(135deg, #0D6EFD 0%, #6F42C1 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        color: white;
        box-shadow: 0 4px 15px rgba(13, 110, 253, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Application Navigation Header
st.markdown("<h1 class='main-header'>🤖 Digital Twin AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #A0A0AB; font-size: 1.1rem; margin-top: -10px;'>Personal Life Simulation & Decision Advisor</p>", unsafe_allow_html=True)

# Check API health
try:
    user = api_client.get_default_user()
    api_online = True
except Exception as e:
    st.error(f"⚠️ Backend API connection failed. Please ensure the FastAPI server is running. Error: {e}")
    api_online = False

if api_online:
    user_id = user["id"]
    
    # Sidebar
    st.sidebar.markdown(f"### Welcome, **{user['username']}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Select View",
        ["Overview Dashboard", "Financial Planner", "Habits & Studies", "What-If Simulator"]
    )
    
    # Manage Configuration Settings in Sidebar
    with st.sidebar.expander("⚙️ Twin Target Profiles"):
        age = st.number_input("Current Age", value=int(user["age"]), min_value=1, max_value=120)
        ret_age = st.number_input("Retirement Target Age", value=int(user["retirement_goal_age"]), min_value=age, max_value=120)
        target_nw = st.number_input("Target Net Worth ($)", value=float(user["target_net_worth"]), step=10000.0)
        monthly_inc = st.number_input("Monthly Base Income ($)", value=float(user["monthly_income"]), step=100.0)
        sleep_t = st.number_input("Target Sleep (Hrs)", value=float(user["sleep_target_hours"]), step=0.5)
        study_t = st.number_input("Target Study/Wk (Hrs)", value=float(user["study_target_hours_week"]), step=1.0)
        
        if st.button("Update Profile Targets"):
            updates = {
                "age": age,
                "retirement_goal_age": ret_age,
                "target_net_worth": target_nw,
                "monthly_income": monthly_inc,
                "sleep_target_hours": sleep_t,
                "study_target_hours_week": study_t
            }
            api_client.update_user(user_id, updates)
            st.success("Target profile updated! Refreshing...")
            st.rerun()

    # 1. Overview Dashboard
    if menu == "Overview Dashboard":
        # Fetch baseline summaries
        sim_data = api_client.get_baseline_and_correlations(user_id)
        baseline = sim_data["baseline"]
        
        # Display KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Current Net Worth</div>
                <div class='metric-val'>${baseline['current_net_worth']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Avg Sleep Duration</div>
                <div class='metric-val'>{baseline['sleep_hours']:.1f} Hrs</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Avg Study Hours</div>
                <div class='metric-val'>{baseline['study_hours_week']:.1f} Hrs/Wk</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Monthly Savings</div>
                <div class='metric-val'>${baseline['monthly_savings']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("---")
        
        # Projections Section
        col_chart, col_side = st.columns([2, 1])
        
        # Fetch Forecasts
        forecasts = api_client.get_forecasts(user_id)
        
        with col_chart:
            # Monte Carlo Projections
            mc_fig = charts.plot_monte_carlo(forecasts["monte_carlo"], user["target_net_worth"])
            st.plotly_chart(mc_fig, use_container_width=True)
            
        with col_side:
            st.markdown("### 🎯 Retirement Forecast")
            prob = forecasts["probability_of_success"]
            
            # Probability Card
            color_prob = "#198754" if prob > 0.7 else "#FFC107" if prob > 0.4 else "#DC3545"
            st.markdown(f"""
            <div class='metric-card' style='border-top: 4px solid {color_prob};'>
                <div class='metric-label'>Probability of Goal Achievement</div>
                <div class='metric-val' style='color: {color_prob};'>{prob * 100:.1f}%</div>
                <p style='font-size: 0.85rem; color: #A0A0AB; margin-top: 10px;'>
                    Chances of hitting your retirement target of <b>${user['target_net_worth']:,.0f}</b> by age <b>{user['retirement_goal_age']}</b> under current saving rates & market volatility.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Baseline Summary Stats")
            st.write(f"- **Current Age:** {user['age']} years old")
            st.write(f"- **Target Age:** {user['retirement_goal_age']} years old")
            st.write(f"- **Time Horizon:** {user['retirement_goal_age'] - user['age']} years")

        # LLM Advisor feedback for current baseline path
        st.markdown("### 🤖 Digital Twin Advisor Verdict (Current Path)")
        with st.spinner("Analyzing current lifestyle trends..."):
            # Prepare mock comparison of 0 changes to get baseline advice
            dummy_change = {"monthly_investment_change": 0.0, "sleep_hours_change": 0.0, "weekly_study_change": 0.0}
            try:
                base_adv = api_client.compare_scenarios(user_id, dummy_change, dummy_change, years=5)
                st.markdown(f"<div class='advisor-box'>{base_adv['recommendation']}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.info("Unable to fetch Advisor feedback. Ensure backend connection is stable.")

    # 2. Financial Planner
    elif menu == "Financial Planner":
        st.subheader("💳 Financial Tracking & Projections")
        
        col_form, col_pie = st.columns([1, 1])
        
        with col_form:
            st.markdown("### Log Financial Record")
            with st.form("financial_form", clear_on_submit=True):
                category = st.selectbox("Category", ["Income", "Investment", "Fixed Expense", "Discretionary Expense"])
                desc = st.text_input("Description (e.g. Salary, Utilities, Grocery, Mutual Fund)")
                amount = st.number_input("Amount ($)", min_value=0.01, step=10.0)
                record_date = st.date_input("Date", value=datetime.today())
                
                submitted = st.form_submit_button("Submit Financial Record")
                if submitted:
                    new_rec = {
                        "category": category,
                        "description": desc,
                        "amount": amount,
                        "record_date": datetime.combine(record_date, datetime.min.time()).isoformat()
                    }
                    api_client.add_record(user_id, "financial", new_rec)
                    st.success(f"Added {category} record of ${amount:.2f}!")
                    st.rerun()
                    
        with col_pie:
            st.markdown("### Spending Allocation Breakdown")
            records = api_client.get_records(user_id, "financial", limit=100)
            if records:
                pie_fig = charts.plot_financial_pie(records)
                st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.info("No records recorded yet. Start logging above!")
                
        st.write("---")
        
        # List recent logs and display deterministic graph
        col_logs, col_det = st.columns([1, 1.5])
        
        with col_logs:
            st.markdown("### Recent Logged Transactions")
            if records:
                df = pd.DataFrame(records)
                # Select columns and clean names
                df["Date"] = pd.to_datetime(df["record_date"], format="ISO8601", errors="coerce").dt.strftime('%Y-%m-%d')
                df_show = df[["Date", "category", "description", "amount"]].rename(
                    columns={"category": "Category", "description": "Description", "amount": "Amount ($)"}
                )
                st.dataframe(df_show.head(10), use_container_width=True)
            else:
                st.write("No transaction history.")
                
        with col_det:
            # Deterministic Compound growth chart
            forecasts = api_client.get_forecasts(user_id)
            det_data = forecasts["deterministic"]
            
            df_det = pd.DataFrame(det_data)
            fig_det = px.line(
                df_det, x="age", y="net_worth", 
                title="Sustained Savings Growth (8% Annual Real Return)",
                labels={"age": "Age", "net_worth": "Projected Assets ($)"}
            )
            fig_det.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=40, l=40, r=40)
            )
            fig_det.update_xaxes(showgrid=True, gridcolor="#3A3A3C")
            fig_det.update_yaxes(showgrid=True, gridcolor="#3A3A3C")
            st.plotly_chart(fig_det, use_container_width=True)

    # 3. Habits & Studies
    elif menu == "Habits & Studies":
        st.subheader("🏃 Daily Routine & Focus Log")
        
        tab_log, tab_corr = st.tabs(["📝 Add Daily Log", "📊 Correlation Analytics"])
        
        with tab_log:
            col_habit, col_study = st.columns(2)
            
            with col_habit:
                st.markdown("### Log Routine Habits")
                with st.form("habit_form", clear_on_submit=True):
                    h_name = st.selectbox("Habit Name", ["Sleep", "Exercise", "Screen Time", "Socializing"])
                    dur_m = st.number_input("Duration (Minutes)", min_value=1, step=10)
                    impact = st.slider("Subjective Wellbeing / Energy Score", min_value=1, max_value=10, value=5)
                    log_date = st.date_input("Log Date", value=datetime.today())
                    
                    sub = st.form_submit_button("Submit Habit Record")
                    if sub:
                        data = {
                            "habit_name": h_name,
                            "duration_minutes": int(dur_m),
                            "impact_score": int(impact),
                            "created_at": datetime.combine(log_date, datetime.min.time()).isoformat()
                        }
                        api_client.add_record(user_id, "habit", data)
                        st.success(f"Logged {h_name} session!")
                        st.rerun()
                        
            with col_study:
                st.markdown("### Log Study Session")
                with st.form("study_form", clear_on_submit=True):
                    subject = st.text_input("Subject / Skill (e.g. Data Structures, Finance, Spanish)")
                    dur_s = st.number_input("Study Time (Minutes)", min_value=1, step=15)
                    focus = st.slider("Focus & Concentration Rating", min_value=1, max_value=10, value=7)
                    exam_sc = st.number_input("Exam Score (Optional, %)", min_value=0.0, max_value=100.0, value=None)
                    log_date_s = st.date_input("Session Date", value=datetime.today())
                    
                    sub_s = st.form_submit_button("Submit Study Session")
                    if sub_s:
                        data = {
                            "subject": subject,
                            "duration_minutes": int(dur_s),
                            "focus_score": int(focus),
                            "exam_score": exam_sc,
                            "created_at": datetime.combine(log_date_s, datetime.min.time()).isoformat()
                        }
                        api_client.add_record(user_id, "study", data)
                        st.success(f"Logged study session for {subject}!")
                        st.rerun()
                        
            st.write("---")
            
            # Displays logs lists
            col_h_list, col_s_list = st.columns(2)
            
            with col_h_list:
                st.markdown("#### Recent Habit logs")
                h_recs = api_client.get_records(user_id, "habit", limit=20)
                if h_recs:
                    df_h = pd.DataFrame(h_recs)
                    df_h["Date"] = pd.to_datetime(df_h["created_at"], format="ISO8601", errors="coerce").dt.strftime('%m-%d %H:%M')
                    st.dataframe(
                        df_h[["Date", "habit_name", "duration_minutes", "impact_score"]].rename(
                            columns={"habit_name":"Habit", "duration_minutes":"Duration (min)", "impact_score":"Impact Score"}
                        ),
                        use_container_width=True
                    )
                else:
                    st.write("No habit logs recorded.")
                    
            with col_s_list:
                st.markdown("#### Recent Study logs")
                s_recs = api_client.get_records(user_id, "study", limit=20)
                if s_recs:
                    df_s = pd.DataFrame(s_recs)
                    df_s["Date"] = pd.to_datetime(df_s["created_at"], format="ISO8601", errors="coerce").dt.strftime('%m-%d %H:%M')
                    st.dataframe(
                        df_s[["Date", "subject", "duration_minutes", "focus_score"]].rename(
                            columns={"subject":"Subject", "duration_minutes":"Duration (min)", "focus_score":"Focus Rating"}
                        ),
                        use_container_width=True
                    )
                else:
                    st.write("No study logs recorded.")
                    
        with tab_corr:
            st.markdown("### Lifestyle & Academic Performance Correlations")
            sim_data = api_client.get_baseline_and_correlations(user_id)
            corr_matrix = sim_data["correlations"]
            
            if corr_matrix:
                fig_heat = charts.plot_correlation_heatmap(corr_matrix)
                st.plotly_chart(fig_heat, use_container_width=True)
                st.info("""
                💡 **How to interpret this heatmap:** 
                Values close to **+1.0** mean variables rise together (e.g. sleep duration increases focus rating). 
                Values close to **-1.0** mean an inverse relationship (e.g. high screen time decreases sleep duration).
                The AI Twin fits linear regressions on these coordinates to forecast what-if scenarios.
                """)
            else:
                st.info("Gathering data. Log routine metrics for a few days to generate correlations!")

    # 4. What-If Scenario Simulator
    elif menu == "What-If Simulator":
        st.subheader("💡 Multi-Scenario \"What-If\" Simulator")
        
        sim_data = api_client.get_baseline_and_correlations(user_id)
        baseline = sim_data["baseline"]
        
        st.markdown("Compare two lifestyle pathways side-by-side to understand compound financial, health, and focus tradeoffs.")
        
        # Dual Configuration Sliders
        col_scen_a, col_scen_b = st.columns(2)
        
        with col_scen_a:
            st.markdown("### 🔵 Scenario A Configuration")
            savings_a = st.slider("Change Monthly Investment ($)", min_value=-1500.0, max_value=3000.0, value=0.0, step=50.0, key="savings_a")
            sleep_a = st.slider("Change Nightly Sleep (Hours)", min_value=-3.0, max_value=3.0, value=0.0, step=0.5, key="sleep_a")
            study_a = st.slider("Change Weekly Study (Hours)", min_value=-10.0, max_value=20.0, value=0.0, step=1.0, key="study_a")
            
            st.write(f"**Projected Savings:** ${baseline['monthly_savings'] + savings_a:.2f}/mo")
            st.write(f"**Projected Sleep:** {baseline['sleep_hours'] + sleep_a:.1f} hrs/night")
            st.write(f"**Projected Study:** {baseline['study_hours_week'] + study_a:.1f} hrs/wk")
            
        with col_scen_b:
            st.markdown("### 🟣 Scenario B Configuration")
            # Set default values for B that represent a "Career Pivot & Investment Hike" scenario for cool comparison
            savings_b = st.slider("Change Monthly Investment ($)", min_value=-1500.0, max_value=3000.0, value=500.0, step=50.0, key="savings_b")
            sleep_b = st.slider("Change Nightly Sleep (Hours)", min_value=-3.0, max_value=3.0, value=-1.0, step=0.5, key="sleep_b")
            study_b = st.slider("Change Weekly Study (Hours)", min_value=-10.0, max_value=20.0, value=10.0, step=1.0, key="study_b")
            
            st.write(f"**Projected Savings:** ${baseline['monthly_savings'] + savings_b:.2f}/mo")
            st.write(f"**Projected Sleep:** {baseline['sleep_hours'] + sleep_b:.1f} hrs/night")
            st.write(f"**Projected Study:** {baseline['study_hours_week'] + study_b:.1f} hrs/wk")
            
        st.write("---")
        
        sim_years = st.slider("Simulation Timeline (Years)", min_value=1, max_value=15, value=5)
        
        # Trigger Comparison call
        scen_a_payload = {
            "monthly_investment_change": savings_a,
            "sleep_hours_change": sleep_a,
            "weekly_study_change": study_a
        }
        
        scen_b_payload = {
            "monthly_investment_change": savings_b,
            "sleep_hours_change": sleep_b,
            "weekly_study_change": study_b
        }
        
        with st.spinner("Fusing machine learning parameters and compiling projections..."):
            sim_response = api_client.compare_scenarios(user_id, scen_a_payload, scen_b_payload, years=sim_years)
            
        # Display side-by-side results
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            fig_compare_nw = charts.plot_scenario_net_worth_compare(sim_response["scenario_a"], sim_response["scenario_b"])
            st.plotly_chart(fig_compare_nw, use_container_width=True)
            
        with col_res2:
            fig_compare_sc = charts.plot_scenario_scores_compare(sim_response["scenario_a"], sim_response["scenario_b"])
            st.plotly_chart(fig_compare_sc, use_container_width=True)
            
        # Show LLM advisor results
        st.markdown("### 🤖 Digital Twin's Verdict & Analysis")
        st.markdown(f"<div class='advisor-box'>{sim_response['recommendation']}</div>", unsafe_allow_html=True)
