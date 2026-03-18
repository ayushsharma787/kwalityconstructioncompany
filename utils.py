"""
utils.py — Constants, color palette, formatting helpers, thresholds.
Kwality Construction Forensic Dashboard.
"""
from typing import Union

# ═══════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════
COLORS = {
    "navy":    "#0f172a",
    "blue":    "#2563eb",
    "lblue":   "#3b82f6",
    "sky":     "#0ea5e9",
    "green":   "#10b981",
    "emerald": "#059669",
    "red":     "#dc2626",
    "rose":    "#f43f5e",
    "amber":   "#f59e0b",
    "orange":  "#ea580c",
    "violet":  "#8b5cf6",
    "purple":  "#a855f7",
    "teal":    "#14b8a6",
    "pink":    "#ec4899",
    "slate":   "#94a3b8",
    "muted":   "#64748b",
    "grid":    "#f1f5f9",
    "card_bg": "#ffffff",
    "bg":      "#f8fafc",
    "text":    "#0f172a",
}

CAT_COLORS = {
    "Materials & Supplies":     "#3b82f6",
    "Sub-contractors":          "#8b5cf6",
    "Labor & Workforce":        "#f59e0b",
    "Cash Withdrawals":         "#ef4444",
    "GST & Tax Payments":       "#10b981",
    "Related Party / Promoter": "#dc2626",
    "EMI & Loan Servicing":     "#6366f1",
    "Inter-Account Transfers":  "#a855f7",
    "Fuel & Transport":         "#0ea5e9",
    "Equipment & Machinery":    "#14b8a6",
    "Overheads & Administration":"#ec4899",
    "Suspicious / Unverified":  "#b91c1c",
    "Uncategorized":            "#94a3b8",
    "Revenue / Inflows":        "#059669",
}

SEVERITY_COLORS = {"Critical": "#dc2626", "High": "#ea580c", "Medium": "#eab308", "Watch": "#f59e0b", "Normal": "#94a3b8"}
SEVERITY_BG     = {"Critical": "#fef2f2", "High": "#fff7ed", "Medium": "#fefce8", "Watch": "#fffbeb", "Normal": "#f8fafc"}
SEVERITY_ICON   = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Watch": "🟡", "Normal": "⚪"}

# ═══════════════════════════════════════════════════════════════════
# BENCHMARKS (Indian Construction, ₹5-15 Cr turnover)
# ═══════════════════════════════════════════════════════════════════
BENCHMARKS = {
    "Materials & Supplies":      (25, 35, "% of turnover"),
    "Sub-contractors":           (15, 25, "% (higher = lower margin)"),
    "Labor & Workforce":         (10, 18, "% of turnover"),
    "Cash Withdrawals":          (0, 5,   "% (above = red flag)"),
    "GST & Tax Payments":        (5, 10,  "% of turnover"),
    "Equipment & Machinery":     (3, 5,   "% of turnover"),
    "Fuel & Transport":          (2, 4,   "% of turnover"),
    "Overheads & Administration": (3, 5,   "% of turnover"),
    "Net Profit Margin":         (8, 15,  "% target"),
    "Debt Servicing":            (0, 10,  "% of revenue"),
}

# ═══════════════════════════════════════════════════════════════════
# PLOTLY BASE LAYOUT
# ═══════════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    font=dict(family="DM Sans, sans-serif", size=12),
    margin=dict(l=45, r=20, t=45, b=40),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="DM Sans"),
)

# ═══════════════════════════════════════════════════════════════════
# FORMATTING HELPERS
# ═══════════════════════════════════════════════════════════════════
def fmt(n: Union[int, float]) -> str:
    """Format number to Indian shorthand: Cr / L / K."""
    a = abs(n)
    sign = "−" if n < 0 else ""
    if a >= 1e7:  return f"{sign}₹{a/1e7:.2f} Cr"
    if a >= 1e5:  return f"{sign}₹{a/1e5:.1f} L"
    if a >= 1e3:  return f"{sign}₹{a/1e3:.0f}K"
    return f"{sign}₹{a:,.0f}"

def fmt_full(n: Union[int, float]) -> str:
    """Format with full Indian comma system."""
    a = abs(n)
    sign = "-" if n < 0 else ""
    s = f"{a:,.0f}"
    return f"{sign}₹{s}"

def pct(part: float, whole: float) -> str:
    if whole == 0: return "0%"
    return f"{part/whole*100:.1f}%"

# ═══════════════════════════════════════════════════════════════════
# CSS INJECTION
# ═══════════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
html, body, .stApp { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; font-size: 1.45rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }
[data-testid="stMetricLabel"] { font-weight: 600 !important; color: #64748b !important; font-size: 0.82rem !important; text-transform: uppercase; letter-spacing: 0.04em; }
.section-head { font-size: 1.25rem; font-weight: 800; margin-top: 0.8rem; margin-bottom: 0.2rem; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.35rem; }
.sub-head { font-size: 1.05rem; font-weight: 700; margin-top: 0.6rem; color: #334155; }
.insight-box { background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%); border-left: 4px solid #3b82f6; border-radius: 0.5rem; padding: 0.9rem 1.1rem; margin: 0.4rem 0 0.8rem 0; font-size: 0.88rem; line-height: 1.7; color: #1e293b; }
.alert-box { background: linear-gradient(135deg, #fef2f2 0%, #fff1f2 100%); border-left: 4px solid #ef4444; border-radius: 0.5rem; padding: 0.9rem 1.1rem; margin: 0.4rem 0 0.8rem 0; font-size: 0.88rem; line-height: 1.7; }
.green-box { background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border-left: 4px solid #10b981; border-radius: 0.5rem; padding: 0.9rem 1.1rem; margin: 0.4rem 0 0.8rem 0; font-size: 0.88rem; line-height: 1.7; }
.amber-box { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-left: 4px solid #f59e0b; border-radius: 0.5rem; padding: 0.9rem 1.1rem; margin: 0.4rem 0 0.8rem 0; font-size: 0.88rem; line-height: 1.7; }
div[data-testid="stExpander"] details summary p { font-weight: 700 !important; font-size: 0.92rem !important; }
.stTabs [data-baseweb="tab"] { padding: 10px 20px; font-weight: 700; font-size: 0.88rem; }
.mono { font-family: 'JetBrains Mono', monospace; }
</style>
"""
