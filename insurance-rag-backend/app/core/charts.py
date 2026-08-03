# src/charts.py
import plotly.graph_objects as go

def create_premium_chart(age, monthly_premium, yearly_premium):
    """Create premium comparison chart"""
    fig = go.Figure(data=[
        go.Bar(
            name='Monthly',
            x=['Premium'],
            y=[monthly_premium],
            marker_color='#2d6a4f',
            text=[f'${monthly_premium:,.2f}'],
            textposition='auto',
        ),
        go.Bar(
            name='Yearly',
            x=['Premium'],
            y=[yearly_premium],
            marker_color='#1e4a6e',
            text=[f'${yearly_premium:,.2f}'],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="💰 Premium Comparison",
        yaxis_title="Amount ($)",
        showlegend=True,
        height=350,
        template="plotly_white"
    )
    
    return fig

def create_deductible_chart():
    """Create deductible comparison bar chart"""
    deductibles = {
        'Auto Collision': 1000,
        'Auto Comprehensive': 500,
        'Auto Glass': 0,
        'Renters Standard': 500,
        'Renters Water': 1000,
        'Renters Theft': 500,
        'Health Annual': 1500
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(deductibles.keys()),
            y=list(deductibles.values()),
            marker_color=['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'],
            text=[f'${v}' for v in deductibles.values()],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="📋 Policy Deductibles Comparison",
        xaxis_title="Policy Type",
        yaxis_title="Deductible Amount ($)",
        height=450,
        template="plotly_white"
    )
    
    return fig

def create_age_premium_chart(current_age=28):
    """Show how premium changes with age"""
    ages = list(range(18, 71))
    base_premium = 500
    premiums = []
    
    for age in ages:
        if age < 25:
            factor = 1.2
        elif age < 60:
            factor = 0.8
        else:
            factor = 1.3
        premiums.append(base_premium * factor)
    
    fig = go.Figure(data=[
        go.Scatter(
            x=ages,
            y=premiums,
            mode='lines+markers',
            line=dict(color='#2d6a4f', width=3),
            marker=dict(size=6, color='#ffd700'),
            name='Premium Trend'
        ),
        go.Scatter(
            x=[current_age],
            y=[premiums[ages.index(current_age)]],
            mode='markers',
            marker=dict(size=15, color='#ef4444', symbol='star'),
            name=f'Your Age: {current_age}'
        )
    ])
    
    fig.update_layout(
        title="📈 Premium Trend by Age",
        xaxis_title="Age",
        yaxis_title="Estimated Premium ($)",
        height=350,
        template="plotly_white"
    )
    
    return fig

def create_coverage_chart():
    """Create coverage limits horizontal bar chart"""
    coverages = {
        'Auto Liability': 250000,
        'Auto Uninsured': 250000,
        'Renters Property': 20000,
        'Renters Liability': 100000,
        'Renters Loss of Use': 5000,
        'Health OOP Max': 5000
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(coverages.values()),
            y=list(coverages.keys()),
            orientation='h',
            marker_color='#1e4a6e',
            text=[f'${v:,.0f}' for v in coverages.values()],
            textposition='outside',
        )
    ])
    
    fig.update_layout(
        title="📊 Coverage Limits Comparison",
        xaxis_title="Coverage Amount ($)",
        yaxis_title="Coverage Type",
        height=400,
        template="plotly_white"
    )
    
    return fig
