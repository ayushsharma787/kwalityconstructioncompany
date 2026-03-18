"""
charts.py — Reusable Plotly chart builder functions.
All charts share consistent styling from utils.PLOTLY_LAYOUT.
"""
import plotly.graph_objects as go
import plotly.express as px
import math
from utils import PLOTLY_LAYOUT, COLORS, CAT_COLORS, fmt

def _layout(height: int = 400, **kwargs) -> dict:
    base = {**PLOTLY_LAYOUT, "height": height}
    base.update(kwargs)
    return base

# ─── WATERFALL ──────────────────────────────────────────────────
def waterfall(labels: list, values: list, measures: list, height: int = 400) -> go.Figure:
    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        connector_line=dict(color="#94a3b8", width=1),
        increasing_marker_color=COLORS["green"],
        decreasing_marker_color=COLORS["red"],
        totals_marker_color=COLORS["blue"],
        text=[fmt(v) for v in values],
        textposition="outside",
        textfont=dict(size=12, family="JetBrains Mono"),
    ))
    fig.update_layout(**_layout(height,
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"], zeroline=True, zerolinecolor="#475569")))
    return fig

# ─── DONUT ──────────────────────────────────────────────────────
def donut(labels: list, values: list, colors: list = None, center_text: str = "", height: int = 400) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors) if colors else {},
        textinfo="label+percent", textposition="outside", textfont_size=10,
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    annot = [dict(text=center_text, x=0.5, y=0.5, font_size=13, showarrow=False, font_family="JetBrains Mono")] if center_text else []
    fig.update_layout(**_layout(height, showlegend=False, annotations=annot))
    return fig

# ─── HORIZONTAL BAR ─────────────────────────────────────────────
def hbar(names: list, values: list, colors=None, height: int = 400, text_fmt=None) -> go.Figure:
    if text_fmt is None:
        text_fmt = [fmt(v) for v in values]
    color = colors if colors else COLORS["blue"]
    fig = go.Figure(go.Bar(
        y=names, x=values, orientation="h",
        marker_color=color, marker_opacity=0.85,
        text=text_fmt, textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout(height,
        xaxis=dict(showgrid=True, gridcolor=COLORS["grid"]),
        yaxis=dict(autorange="reversed", tickfont_size=10)))
    return fig

# ─── GROUPED BAR (INFLOW vs OUTFLOW) ────────────────────────────
def grouped_bar(months: list, series: dict, height: int = 430) -> go.Figure:
    fig = go.Figure()
    color_map = {"Inflows": COLORS["green"], "Outflows": COLORS["red"], "Credits": COLORS["green"], "Debits": COLORS["red"]}
    for name, vals in series.items():
        fig.add_trace(go.Bar(
            name=name, x=months, y=vals,
            marker_color=color_map.get(name, COLORS["blue"]), marker_opacity=0.85,
            text=[fmt(v) for v in vals], textposition="outside",
            textfont=dict(size=8, family="JetBrains Mono"),
        ))
    fig.update_layout(**_layout(height, barmode="group",
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"])))
    return fig

# ─── NET SURPLUS/DEFICIT BAR ─────────────────────────────────────
def net_bar(months: list, values: list, height: int = 320) -> go.Figure:
    colors = [COLORS["green"] if v >= 0 else COLORS["red"] for v in values]
    fig = go.Figure(go.Bar(
        x=months, y=values, marker_color=colors,
        text=[fmt(v) for v in values], textposition="outside",
        textfont=dict(size=9, family="JetBrains Mono"),
    ))
    fig.update_layout(**_layout(height,
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"],
                   zeroline=True, zerolinecolor="#475569", zerolinewidth=1.5)))
    return fig

# ─── LINE CHART ──────────────────────────────────────────────────
def line_chart(x: list, y: list, color: str = None, height: int = 350,
               ref_lines: list = None, show_text: bool = True) -> go.Figure:
    c = color or COLORS["violet"]
    marker_colors = [COLORS["red"] if v < 100000 else COLORS["amber"] if v < 500000 else c for v in y]
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers" + ("+text" if show_text else ""),
        line=dict(color=c, width=3),
        marker=dict(size=8, color=marker_colors),
        text=[fmt(v) for v in y] if show_text else None,
        textposition="top center",
        textfont=dict(size=9, family="JetBrains Mono"),
    ))
    if ref_lines:
        for val, label, lcolor in ref_lines:
            fig.add_hline(y=val, line_dash="dash", line_color=lcolor, opacity=0.5,
                          annotation_text=label, annotation_position="top right")
    fig.update_layout(**_layout(height,
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"])))
    return fig

# ─── DUAL AXIS BAR + LINE ───────────────────────────────────────
def dual_axis(months: list, bar_values: list, line_values: list,
              bar_name: str = "Amount", line_name: str = "Count",
              bar_color: str = None, height: int = 340) -> go.Figure:
    bc = bar_color or COLORS["red"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=bar_values, name=bar_name,
        marker_color=bc, marker_opacity=0.7,
        text=[fmt(v) for v in bar_values], textposition="outside",
        textfont=dict(size=8, family="JetBrains Mono")))
    fig.add_trace(go.Scatter(x=months, y=line_values, name=line_name,
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["violet"], width=2.5), marker_size=7))
    fig.update_layout(**_layout(height,
        yaxis=dict(title=bar_name, showgrid=True, gridcolor=COLORS["grid"]),
        yaxis2=dict(title=line_name, overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center")))
    return fig

# ─── TREEMAP ─────────────────────────────────────────────────────
def treemap(labels: list, parents: list, values: list, colors: list = None, height: int = 500) -> go.Figure:
    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        marker=dict(colors=colors) if colors else {},
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percentParent:.1%} of parent<extra></extra>",
    ))
    fig.update_layout(**_layout(height, margin=dict(l=5, r=5, t=30, b=5)))
    return fig

# ─── BENFORD'S LAW ──────────────────────────────────────────────
def benford_chart(actual: dict, expected: dict, height: int = 350) -> go.Figure:
    digits = [str(d) for d in range(1, 10)]
    total = sum(actual.get(d, 0) for d in digits)
    act_pct = [actual.get(d, 0) / total * 100 for d in digits]
    exp_pct = [expected.get(d, 0) for d in digits]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Actual", x=digits, y=act_pct,
        marker_color=COLORS["blue"], marker_opacity=0.8,
        text=[f"{v:.1f}%" for v in act_pct], textposition="outside",
        textfont=dict(size=9, family="JetBrains Mono")))
    fig.add_trace(go.Scatter(name="Benford Expected", x=digits, y=exp_pct,
        mode="lines+markers", line=dict(color=COLORS["red"], width=2, dash="dash"),
        marker=dict(size=7, color=COLORS["red"])))
    fig.update_layout(**_layout(height,
        xaxis=dict(title="First Digit"),
        yaxis=dict(title="Frequency (%)", showgrid=True, gridcolor=COLORS["grid"]),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")))
    return fig

# ─── HISTOGRAM ───────────────────────────────────────────────────
def histogram(values: list, nbins: int = 20, color: str = None, height: int = 300, title: str = "") -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=values, nbinsx=nbins,
        marker_color=color or COLORS["blue"], marker_opacity=0.8,
    ))
    fig.update_layout(**_layout(height, title=title,
        xaxis=dict(title="Amount (₹)"),
        yaxis=dict(title="Frequency", showgrid=True, gridcolor=COLORS["grid"])))
    return fig

# ─── CUMULATIVE LINE ─────────────────────────────────────────────
def cumulative_line(dates: list, amounts: list, color: str = None, height: int = 300) -> go.Figure:
    cum = []
    running = 0
    for a in amounts:
        running += a
        cum.append(running)
    
    fig = go.Figure(go.Scatter(
        x=dates, y=cum, mode="lines",
        fill="tozeroy", fillcolor=f"rgba(59,130,246,0.1)",
        line=dict(color=color or COLORS["blue"], width=2.5),
        hovertemplate="<b>%{x}</b><br>Cumulative: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout(height,
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"], title="Cumulative (₹)")))
    return fig

# ─── GANTT-STYLE TIMELINE ────────────────────────────────────────
def gantt_timeline(phases: list, height: int = 120) -> go.Figure:
    """phases: list of (label, start_week, width_weeks, color)"""
    fig = go.Figure()
    for label, start, width, color in phases:
        fig.add_trace(go.Bar(
            x=[width], y=[0], base=start, orientation="h",
            marker_color=color, marker_opacity=0.85, name=label,
            text=[label], textposition="inside",
            textfont=dict(size=11, color="white"),
        ))
    fig.update_layout(**_layout(height, showlegend=False,
        xaxis=dict(title="Weeks →", range=[0, 14], showgrid=True, gridcolor=COLORS["grid"]),
        yaxis=dict(visible=False), bargap=0))
    return fig

# ─── HEATMAP (Month × Category) ─────────────────────────────────
def month_category_heatmap(months: list, categories: list, values: list, height: int = 400) -> go.Figure:
    """values: 2D list [categories][months]"""
    text = [[fmt(v) if v > 0 else "" for v in row] for row in values]
    fig = go.Figure(go.Heatmap(
        z=values, x=months, y=categories,
        colorscale=[[0, "#f0fdf4"], [0.5, "#fef9c3"], [1, "#fecaca"]],
        text=text, texttemplate="%{text}", textfont_size=9,
        hovertemplate="<b>%{y}</b><br>%{x}: ₹%{z:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout(height, margin=dict(l=150, r=20, t=30, b=40)))
    return fig
