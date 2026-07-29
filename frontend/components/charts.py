import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# Custom color palette for premium design
PRIMARY_COLOR = "#0D6EFD"
SECONDARY_COLOR = "#6F42C1"
ACCENT_GREEN = "#198754"
ACCENT_RED = "#DC3545"
ACCENT_AMBER = "#FFC107"
BG_DARK = "#1E1E24"
TEXT_COLOR = "#F8F9FA"

def plot_financial_pie(records: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate a pie chart breakdown of financial categories.
    """
    if not records:
        # Empty placeholder figure
        fig = go.Figure()
        fig.update_layout(title="No records to display")
        return fig
        
    df = pd.DataFrame(records)
    # Sum by category
    summary = df.groupby("category")["amount"].sum().reset_index()
    
    fig = px.pie(
        summary,
        values="amount",
        names="category",
        color="category",
        color_discrete_map={
            "Income": "#2ECC71",
            "Fixed Expense": "#E74C3C",
            "Discretionary Expense": "#F39C12",
            "Investment": "#3498DB"
        },
        hole=0.4
    )
    
    fig.update_layout(
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR)
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def plot_monte_carlo(mc_data: Dict[str, Any], target_net_worth: float) -> go.Figure:
    """
    Generate a Monte Carlo simulation line chart with shaded confidence intervals (p10 to p90).
    """
    fig = go.Figure()
    
    ages = mc_data["ages"]
    median = mc_data["median"]
    p10 = mc_data["p10"]
    p90 = mc_data["p90"]
    
    # Shading the 10th-90th percentile bounds
    fig.add_trace(go.Scatter(
        x=ages + ages[::-1],
        y=p90 + p10[::-1],
        fill='toself',
        fillcolor='rgba(13, 110, 253, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='10th - 90th Percentile Range',
        showlegend=True
    ))
    
    # Median line
    fig.add_trace(go.Scatter(
        x=ages,
        y=median,
        line=dict(color=PRIMARY_COLOR, width=3),
        mode='lines',
        name='Median Projection (50th %)'
    ))
    
    # Pessimistic line
    fig.add_trace(go.Scatter(
        x=ages,
        y=p10,
        line=dict(color=ACCENT_RED, width=1.5, dash='dot'),
        mode='lines',
        name='Pessimistic Projection (10th %)'
    ))
    
    # Optimistic line
    fig.add_trace(go.Scatter(
        x=ages,
        y=p90,
        line=dict(color=ACCENT_GREEN, width=1.5, dash='dash'),
        mode='lines',
        name='Optimistic Projection (90th %)'
    ))
    
    # Target Line
    fig.add_trace(go.Scatter(
        x=ages,
        y=[target_net_worth] * len(ages),
        line=dict(color='rgba(255, 193, 7, 0.7)', width=2, dash='longdash'),
        mode='lines',
        name=f'Target Net Worth (${target_net_worth:,.0f})'
    ))
    
    fig.update_layout(
        title="Monte Carlo Net Worth Projections (Retirement Path)",
        xaxis_title="Age",
        yaxis_title="Net Worth ($)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        margin=dict(t=50, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#3A3A3C")
    fig.update_yaxes(showgrid=True, gridcolor="#3A3A3C")
    
    return fig

def plot_correlation_heatmap(corr_dict: Dict[str, Dict[str, float]]) -> go.Figure:
    """
    Generate correlation matrix heatmap.
    """
    if not corr_dict:
        fig = go.Figure()
        fig.update_layout(title="Not enough data to calculate correlations")
        return fig
        
    df = pd.DataFrame(corr_dict)
    
    # Rename index and columns for user friendliness
    rename_map = {
        "Sleep": "Sleep Hours",
        "Exercise": "Exercise Hours",
        "Screen Time": "Screen Time",
        "Socializing": "Social Hours",
        "study_duration": "Study Hours",
        "focus_score": "Focus Rating",
        "daily_impact": "Wellbeing Index"
    }
    df = df.rename(columns=rename_map, index=rename_map)
    
    fig = px.imshow(
        df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1.0,
        zmax=1.0,
        labels=dict(color="Correlation Coefficient")
    )
    
    fig.update_layout(
        title="Habits & Study Correlation Matrix",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        margin=dict(t=50, b=40, l=40, r=40)
    )
    
    return fig

def plot_scenario_net_worth_compare(scen_a: Dict[str, Any], scen_b: Dict[str, Any]) -> go.Figure:
    """
    Plot net worth trajectory comparison for Scenario A vs Scenario B.
    """
    fig = go.Figure()
    
    years = [dp["year"] for dp in scen_a["datapoints"]]
    nw_a = [dp["net_worth"] for dp in scen_a["datapoints"]]
    nw_b = [dp["net_worth"] for dp in scen_b["datapoints"]]
    
    fig.add_trace(go.Scatter(
        x=years,
        y=nw_a,
        line=dict(color=PRIMARY_COLOR, width=3),
        mode='lines+markers',
        name='Scenario A'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=nw_b,
        line=dict(color=SECONDARY_COLOR, width=3),
        mode='lines+markers',
        name='Scenario B'
    ))
    
    fig.update_layout(
        title="Wealth Growth Projection Comparison",
        xaxis_title="Years",
        yaxis_title="Projected Net Worth ($)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        margin=dict(t=50, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#3A3A3C")
    fig.update_yaxes(showgrid=True, gridcolor="#3A3A3C")
    
    return fig

def plot_scenario_scores_compare(scen_a: Dict[str, Any], scen_b: Dict[str, Any]) -> go.Figure:
    """
    Compare average predicted health and study focus indexes for A vs B.
    """
    fig = go.Figure()
    
    categories = ['Wellbeing (Health Index)', 'Focus & Study Index']
    
    def get_avg_score(scen: Dict[str, Any], key: str) -> float:
        if key in scen:
            return float(scen[key])
        datapoints = scen.get("datapoints", [])
        if not datapoints:
            return 0.0
        return sum(float(dp.get(key, 0.0)) for dp in datapoints) / len(datapoints)
    
    scores_a = [get_avg_score(scen_a, "health_index"), get_avg_score(scen_a, "focus_index")]
    scores_b = [get_avg_score(scen_b, "health_index"), get_avg_score(scen_b, "focus_index")]

    
    fig.add_trace(go.Bar(
        name='Scenario A',
        x=categories,
        y=scores_a,
        marker_color=PRIMARY_COLOR,
        text=[f"{s:.2f}/10" for s in scores_a],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Scenario B',
        x=categories,
        y=scores_b,
        marker_color=SECONDARY_COLOR,
        text=[f"{s:.2f}/10" for s in scores_b],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Sustained Well-being & Performance Comparison",
        yaxis_title="Index Score (1-10)",
        yaxis=dict(range=[0, 11]),
        template="plotly_dark",
        barmode='group',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        margin=dict(t=50, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    fig.update_yaxes(showgrid=True, gridcolor="#3A3A3C")
    
    return fig
