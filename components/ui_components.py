# components/ui_components.py
# Reusable Streamlit UI components

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_score_gauge(score: float, title: str = "ATS Score") -> None:
    """Render an animated gauge chart for ATS score."""
    color = "#22c55e" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#e2e8f0', 'family': 'Georgia'}},
        delta={'reference': 75, 'increasing': {'color': "#22c55e"}, 'decreasing': {'color': "#ef4444"}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#475569",
                'tickfont': {'color': '#94a3b8', 'size': 10},
            },
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': "#1e293b",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#2d1b1b'},
                {'range': [40, 65], 'color': '#2d2910'},
                {'range': [65, 100], 'color': '#1a2e1a'},
            ],
            'threshold': {
                'line': {'color': "#f8fafc", 'width': 2},
                'thickness': 0.8,
                'value': 75
            }
        },
        number={'font': {'size': 48, 'color': color, 'family': 'Georgia'}, 'suffix': '/100'}
    ))

    fig.update_layout(
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10),
        font={'color': '#e2e8f0'}
    )
    st.plotly_chart(fig, use_container_width=True)


def render_section_bar_chart(section_scores: dict, max_scores: dict) -> None:
    """Render horizontal bar chart for section-wise scores."""
    sections = list(section_scores.keys())
    scores = list(section_scores.values())
    maxes = [max_scores.get(s.lower().replace(" ", "_"), 10) for s in sections]
    percentages = [round((s / m) * 100, 1) if m > 0 else 0 for s, m in zip(scores, maxes)]

    colors = ["#22c55e" if p >= 75 else "#eab308" if p >= 50 else "#ef4444" for p in percentages]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sections,
        x=scores,
        orientation='h',
        marker_color=colors,
        marker_line_width=0,
        text=[f"{s}/{m} ({p}%)" for s, m, p in zip(scores, maxes, percentages)],
        textposition='outside',
        textfont={'color': '#cbd5e1', 'size': 11},
        hovertemplate='<b>%{y}</b><br>Score: %{x}<br><extra></extra>'
    ))

    # Add max as background
    fig.add_trace(go.Bar(
        y=sections,
        x=maxes,
        orientation='h',
        marker_color='rgba(100,116,139,0.15)',
        marker_line_width=0,
        hovertemplate='Max: %{x}<extra></extra>',
        showlegend=False,
    ))

    fig.update_layout(
        barmode='overlay',
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={
            'gridcolor': '#1e293b',
            'tickfont': {'color': '#94a3b8'},
            'title': {'text': 'Score', 'font': {'color': '#94a3b8'}},
        },
        yaxis={
            'tickfont': {'color': '#e2e8f0', 'size': 12},
            'categoryorder': 'total ascending',
        },
        margin=dict(l=10, r=80, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_radar(resume_skills: dict) -> None:
    """Render radar chart showing skill category coverage."""
    categories = list(resume_skills.keys()) if resume_skills else ["No Skills Found"]
    counts = [len(v) for v in resume_skills.values()] if resume_skills else [0]

    # Normalize to 0-10 scale for display
    max_count = max(counts) if counts else 1
    normalized = [min(c / max_count * 10, 10) for c in counts]

    # Close the polygon
    cats = categories + [categories[0]]
    vals = normalized + [normalized[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=cats,
        fill='toself',
        fillcolor='rgba(99,102,241,0.25)',
        line={'color': '#818cf8', 'width': 2},
        marker={'color': '#818cf8', 'size': 6},
        hovertemplate='<b>%{theta}</b>: %{customdata} skills<extra></extra>',
        customdata=counts + [counts[0]]
    ))

    fig.update_layout(
        polar={
            'bgcolor': 'rgba(0,0,0,0)',
            'radialaxis': {
                'visible': True,
                'range': [0, 10],
                'tickfont': {'color': '#64748b', 'size': 9},
                'gridcolor': '#1e293b',
                'linecolor': '#334155',
            },
            'angularaxis': {
                'tickfont': {'color': '#cbd5e1', 'size': 11},
                'gridcolor': '#1e293b',
                'linecolor': '#334155',
            }
        },
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_bubbles(resume_skills: dict) -> None:
    """Render bubble/treemap chart for skill categories."""
    if not resume_skills:
        st.info("No skills detected.")
        return

    labels, parents, values, colors = [], [], [], []
    palette = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7', '#f97316']

    labels.append("All Skills")
    parents.append("")
    values.append(0)
    colors.append('#0f172a')

    for i, (cat, skills) in enumerate(resume_skills.items()):
        labels.append(cat)
        parents.append("All Skills")
        values.append(len(skills))
        colors.append(palette[i % len(palette)])
        for skill in skills:
            labels.append(skill)
            parents.append(cat)
            values.append(1)
            colors.append(palette[i % len(palette)] + "88")

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker={'colors': colors, 'line': {'width': 1.5, 'color': '#0f172a'}},
        textfont={'color': '#f1f5f9', 'size': 12},
        hovertemplate='<b>%{label}</b><br>%{value} skills<extra></extra>',
        pathbar={'visible': False}
    ))

    fig.update_layout(
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=5, t=5, b=5),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_job_match_chart(job_results: list) -> None:
    """Render bar chart comparing match scores across job roles."""
    if not job_results:
        return

    roles = [r["role"] for r in job_results]
    scores = [r["match_score"] for r in job_results]
    colors = ["#22c55e" if s >= 70 else "#eab308" if s >= 40 else "#ef4444" for s in scores]

    fig = go.Figure(go.Bar(
        x=roles,
        y=scores,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{s}%" for s in scores],
        textposition='outside',
        textfont={'color': '#e2e8f0', 'size': 13, 'family': 'Georgia'},
        hovertemplate='<b>%{x}</b><br>Match: %{y}%<extra></extra>'
    ))

    fig.add_hline(y=70, line_dash="dot", line_color="#22c55e", annotation_text="Target (70%)",
                  annotation_font_color="#22c55e")

    fig.update_layout(
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'tickfont': {'color': '#cbd5e1', 'size': 11}, 'gridcolor': '#1e293b'},
        yaxis={'tickfont': {'color': '#94a3b8'}, 'gridcolor': '#1e293b', 'range': [0, 110]},
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def score_badge(score: float) -> str:
    """Return HTML badge HTML for a score."""
    if score >= 80:
        return f'<span style="background:#166534;color:#86efac;padding:3px 10px;border-radius:20px;font-weight:700">🏆 Excellent {score}%</span>'
    elif score >= 65:
        return f'<span style="background:#14532d;color:#4ade80;padding:3px 10px;border-radius:20px;font-weight:700">✅ Good {score}%</span>'
    elif score >= 50:
        return f'<span style="background:#713f12;color:#fbbf24;padding:3px 10px;border-radius:20px;font-weight:700">⚡ Average {score}%</span>'
    else:
        return f'<span style="background:#7f1d1d;color:#fca5a5;padding:3px 10px;border-radius:20px;font-weight:700">❌ Needs Work {score}%</span>'


def keyword_pills(keywords: list, color: str = "#1e3a5f") -> str:
    """Render keyword pills as HTML."""
    pills = "".join(
        f'<span style="display:inline-block;background:{color};color:#93c5fd;'
        f'border:1px solid #3b82f6;padding:3px 10px;border-radius:20px;'
        f'font-size:12px;margin:3px 2px;font-weight:500">{k}</span>'
        for k in keywords
    )
    return f'<div style="line-height:2.2">{pills}</div>'


def missing_keyword_pills(keywords: list) -> str:
    """Render missing keywords as red pills."""
    pills = "".join(
        f'<span style="display:inline-block;background:#3b0a0a;color:#fca5a5;'
        f'border:1px solid #ef4444;padding:3px 10px;border-radius:20px;'
        f'font-size:12px;margin:3px 2px;font-weight:500">+ {k}</span>'
        for k in keywords
    )
    return f'<div style="line-height:2.2">{pills}</div>'
