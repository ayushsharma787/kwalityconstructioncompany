"""
Kwality Construction Company — Forensic Financial Dashboard
Enterprise-grade analytics · FY 2024-25 + FY 2025-26
Run:  pip install -r requirements.txt && streamlit run main.py
"""
import pathlib, os
# Auto-create Streamlit config
_cfg = pathlib.Path(__file__).parent / ".streamlit"
_cfg.mkdir(exist_ok=True)
(_cfg / "config.toml").write_text(
    '[theme]\nprimaryColor="#1e40af"\nbackgroundColor="#f8fafc"\n'
    'secondaryBackgroundColor="#ffffff"\ntextColor="#0f172a"\nfont="sans serif"\n'
    '[server]\nheadless=true\nport=8501\n[browser]\ngatherUsageStats=false\n'
)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict

from utils import COLORS, CAT_COLORS, SEVERITY_COLORS, SEVERITY_BG, SEVERITY_ICON, CUSTOM_CSS, PLOTLY_LAYOUT, BENCHMARKS, fmt, fmt_full, pct
from charts import (waterfall, donut, hbar, grouped_bar, net_bar, line_chart,
                    dual_axis, treemap, benford_chart, histogram, cumulative_line,
                    gantt_timeline, month_category_heatmap)
from bank_data import (
    SUMMARY_FY1, SUMMARY_FY2, MONTHS_FY1, FY1_CREDITS, FY1_DEBITS, FY1_NET, FY1_CLOSING,
    MONTHS_FY2, FY2_CREDITS, FY2_DEBITS, FY2_NET,
    EXPENSE_CATEGORIES, REVENUE_SOURCES,
    RATURI_TRANSACTIONS, RATURI_MONTHLY,
    AMIT_TRANSACTIONS,
    NOORKHAN_COUNT, NOORKHAN_TOTAL, NOORKHAN_MONTHLY,
    BENFORD_ACTUAL, BENFORD_EXPECTED, ROUND_AMOUNT_PCT,
    SUSPICIOUS_ENTITIES, RECOMMENDATIONS, PROFIT_BRIDGE,
    EMI_DETAILS, EMI_MONTHLY_TOTAL, EMI_ANNUAL_TOTAL,
)

# ─── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(page_title="Kwality Construction — Forensic Dashboard", page_icon="🏗️", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("### 🏗️ M/S. Kwality Construction Company")
    st.caption("HDFC Bank A/c 27718630000017 · Mussoorie Branch · Forensic Financial Audit")
with h2:
    st.markdown(
        "<div style='text-align:right;margin-top:10px'>"
        "<span style='background:#fef2f2;color:#dc2626;padding:6px 16px;"
        "border-radius:20px;font-weight:800;font-size:0.82rem'>"
        f"⚠ FY24-25 NET LOSS: {fmt(SUMMARY_FY1['net_change'])}</span></div>",
        unsafe_allow_html=True)
st.divider()

# ─── TABS ─────────────────────────────────────────────────────────
tab_exec, tab_exp, tab_cash, tab_rev, tab_sus, tab_raturi, tab_amit, tab_vendor, tab_debt, tab_reco, tab_raw = st.tabs([
    "🏠 Executive", "📊 Expenses", "📈 Cash Flow", "💰 Revenue",
    "🔴 Suspicious", "🔍 Raturi", "🔍 Amit", "🏗️ Vendors",
    "🏦 Debt/EMI", "🚀 Roadmap", "📑 Raw Data",
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════
with tab_exec:
    st.markdown('<p class="section-head">Board-Level Overview — FY 2024-25</p>', unsafe_allow_html=True)
    
    s = SUMMARY_FY1
    burn = s['total_debits'] / 12
    runway = s['closing_balance'] / (burn / 30)
    
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Revenue", fmt(s['total_credits']), f"{s['credit_count']} txns")
    k2.metric("Total Expenses", fmt(s['total_debits']), f"{s['debit_count']} txns")
    k3.metric("Net Profit/Loss", fmt(s['net_change']), "Loss ↓", delta_color="inverse")
    k4.metric("Closing Balance", fmt(s['closing_balance']), f"{((s['closing_balance']/s['opening_balance'])-1)*100:.0f}%", delta_color="inverse")
    k5.metric("Avg Monthly Burn", fmt(burn))
    k6.metric("Cash Runway", f"{runway:.0f} days", "Danger" if runway < 30 else "Low" if runway < 90 else "OK")
    
    st.markdown("")
    
    # Cash Flow Waterfall
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<p class="sub-head">Cash Flow Waterfall</p>', unsafe_allow_html=True)
        fig = waterfall(
            ["Opening", "Credits (In)", "Debits (Out)", "Closing"],
            [s['opening_balance'], s['total_credits'], -s['total_debits'], s['closing_balance']],
            ["absolute", "relative", "relative", "total"], height=380)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown('<p class="sub-head">Monthly P&L Heatmap</p>', unsafe_allow_html=True)
        # Heatmap
        fig = go.Figure(go.Heatmap(
            z=[FY1_NET], x=MONTHS_FY1, y=["Net"],
            colorscale=[[0, "#fecaca"], [0.5, "#fef9c3"], [1, "#bbf7d0"]],
            text=[[fmt(v) for v in FY1_NET]], texttemplate="%{text}", textfont_size=10,
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=120, margin=dict(l=40, r=10, t=10, b=30),
            yaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True)
        
        loss_months = sum(1 for v in FY1_NET if v < 0)
        st.markdown(f"""
        <div class="alert-box">
            <strong>⚠️ Danger Signals:</strong><br>
            • <strong>{loss_months}/12 months</strong> negative cash flow<br>
            • Balance hit <strong>₹0 twice</strong> (Sep-24, Mar-25)<br>
            • Below ₹50K on <strong>15+ occasions</strong><br>
            • Largest single-day outflow: <strong>₹29.5L</strong> (26-Mar-25)<br>
            • 1:{s['debit_count']//s['credit_count']} credit-to-debit transaction ratio
        </div>""", unsafe_allow_html=True)
    
    # YoY Comparison
    st.markdown('<p class="section-head">Year-over-Year Comparison</p>', unsafe_allow_html=True)
    y1, y2, y3, y4 = st.columns(4)
    s2 = SUMMARY_FY2
    y1.metric("FY25-26 Revenue", fmt(s2['total_credits']),
              f"{((s2['total_credits']/s['total_credits'])-1)*100:+.0f}% vs FY24-25")
    y2.metric("FY25-26 Expenses", fmt(s2['total_debits']),
              f"{((s2['total_debits']/s['total_debits'])-1)*100:+.0f}% vs FY24-25")
    y3.metric("FY25-26 Net", fmt(s2['net_change']),
              "Improved" if s2['net_change'] > s['net_change'] else "Worsened",
              delta_color="normal" if s2['net_change'] > s['net_change'] else "inverse")
    y4.metric("FY25-26 Closing", fmt(s2['closing_balance']),
              f"{((s2['closing_balance']/s['closing_balance'])-1)*100:+.0f}%", delta_color="inverse")
    
    st.markdown("""
    <div class="insight-box">
        <strong>📊 Executive Insight:</strong> FY25-26 shows 41% higher revenue (₹14.0Cr vs ₹9.97Cr) but expenses 
        also grew 45%. The company is growing top-line but margins remain razor-thin. Revenue concentration from 
        schools (58% FY24-25) remains the existential risk. Cash management improved slightly but balance still 
        hit dangerously low levels. The Noorkhan payments continue unabated (268 total across both years).
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2: EXPENSE DEEP DIVE
# ═══════════════════════════════════════════════════════════════════
with tab_exp:
    st.markdown('<p class="section-head">Where Every Rupee Goes — Both FY Combined</p>', unsafe_allow_html=True)
    total_exp = sum(c['amount'] for c in EXPENSE_CATEGORIES)
    st.caption(f"Total categorized expenses: {fmt(total_exp)} across 2,361 debit transactions")
    
    # Donut + Bar side by side
    cd, cb = st.columns([2, 3])
    with cd:
        cats = [c for c in EXPENSE_CATEGORIES if c['amount'] > 0]
        colors = [CAT_COLORS.get(c['name'], "#94a3b8") for c in cats]
        fig = donut([c['name'] for c in cats], [c['amount'] for c in cats], colors, f"<b>{fmt(total_exp)}</b><br>Total", 440)
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        cats_s = sorted(EXPENSE_CATEGORIES, key=lambda c: c['amount'])
        colors_s = [CAT_COLORS.get(c['name'], "#94a3b8") for c in cats_s]
        fig = hbar([c['name'] for c in cats_s], [c['amount'] for c in cats_s], colors_s, 440)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(
        '<div class="alert-box"><strong>🔍 Key Finding:</strong> Materials (34%) + Labor (23%) + Sub-contractors (13%) = '
        '<strong>70% of outflows</strong>. Cash withdrawals + Suspicious + Related Party = <strong>11% with NO audit trail</strong>.</div>',
        unsafe_allow_html=True)
    
    # Treemap
    st.markdown('<p class="sub-head">Expense Treemap — Category → Top Vendors</p>', unsafe_allow_html=True)
    tm_labels, tm_parents, tm_values, tm_colors = ["Total Expenses"], [""], [0], [COLORS["slate"]]
    for cat in EXPENSE_CATEGORIES:
        if cat['amount'] < 100000: continue
        tm_labels.append(cat['name'])
        tm_parents.append("Total Expenses")
        tm_values.append(cat['amount'])
        tm_colors.append(CAT_COLORS.get(cat['name'], COLORS["slate"]))
        for vname, vamt, vcnt in cat['vendors'][:6]:
            tm_labels.append(vname[:25])
            tm_parents.append(cat['name'])
            tm_values.append(vamt)
            tm_colors.append(CAT_COLORS.get(cat['name'], COLORS["slate"]))
    st.plotly_chart(treemap(tm_labels, tm_parents, tm_values, tm_colors, 520), use_container_width=True)
    
    # Vendor Drill-Down
    st.markdown('<p class="section-head">Category Drill-Down</p>', unsafe_allow_html=True)
    for cat in EXPENSE_CATEGORIES:
        if cat['amount'] < 50000: continue
        icon = "🧱" if "Material" in cat['name'] else "👷" if "Sub" in cat['name'] else "🔨" if "Labor" in cat['name'] else "💸" if "Cash" in cat['name'] else "🏛️" if "GST" in cat['name'] else "🔴" if "Suspicious" in cat['name'] or "Related" in cat['name'] else "🏦" if "EMI" in cat['name'] else "⛽" if "Fuel" in cat['name'] else "🚛" if "Equip" in cat['name'] else "🔄" if "Inter" in cat['name'] else "🏢"
        
        with st.expander(f"{icon}  **{cat['name']}** — {fmt(cat['amount'])} ({cat['pct']}%)"):
            ct, cv = st.columns([3, 2])
            with ct:
                df = pd.DataFrame(cat['vendors'], columns=["Vendor", "Amount", "Txns"])
                df["Share"] = (df["Amount"] / cat['amount'] * 100).round(1).astype(str) + "%"
                df["Avg/Txn"] = (df["Amount"] / df["Txns"].clip(lower=1)).apply(fmt)
                df["Amount"] = df["Amount"].apply(lambda x: f"₹{x:,.0f}")
                df.index += 1
                st.dataframe(df, use_container_width=True, height=min(len(cat['vendors'])*36+42, 450))
            with cv:
                top = cat['vendors'][:8]
                if top:
                    fig = hbar([v[0][:25] for v in top], [v[1] for v in top],
                              CAT_COLORS.get(cat['name'], COLORS["blue"]), 280)
                    st.plotly_chart(fig, use_container_width=True)
            
            if cat['insight']:
                st.markdown(f'<div class="insight-box">📊 <strong>CA Insight:</strong> {cat["insight"]}</div>', unsafe_allow_html=True)
            if cat['benchmark']:
                st.markdown(f'<div class="amber-box">📏 <strong>Benchmark:</strong> {cat["benchmark"]}</div>', unsafe_allow_html=True)
    
    # Top 25 Payees
    st.markdown('<p class="section-head">Top 25 Payees — All Categories</p>', unsafe_allow_html=True)
    all_v = []
    for cat in EXPENSE_CATEGORIES:
        for vn, va, vc in cat['vendors']:
            all_v.append((vn, va, cat['name']))
    all_v.sort(key=lambda x: -x[1])
    top25 = all_v[:25]
    fig = hbar([v[0][:30] for v in top25], [v[1] for v in top25], COLORS["navy"], 600)
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 3: CASH FLOW & LIQUIDITY
# ═══════════════════════════════════════════════════════════════════
with tab_cash:
    st.markdown('<p class="section-head">Monthly Cash Flow — FY 2024-25</p>', unsafe_allow_html=True)
    
    st.plotly_chart(grouped_bar(MONTHS_FY1, {"Inflows": FY1_CREDITS, "Outflows": FY1_DEBITS}, 420), use_container_width=True)
    
    st.markdown('<p class="sub-head">Net Surplus / Deficit</p>', unsafe_allow_html=True)
    st.plotly_chart(net_bar(MONTHS_FY1, FY1_NET, 300), use_container_width=True)
    
    loss_m = sum(1 for v in FY1_NET if v < 0)
    worst = MONTHS_FY1[FY1_NET.index(min(FY1_NET))]
    st.markdown(f'<div class="alert-box">⚠️ <strong>{loss_m}/12 months negative</strong>. Worst: <strong>{worst} ({fmt(min(FY1_NET))})</strong>.</div>', unsafe_allow_html=True)
    
    # Balance Trend
    st.markdown('<p class="section-head">Account Balance Trend</p>', unsafe_allow_html=True)
    st.plotly_chart(line_chart(MONTHS_FY1, FY1_CLOSING, COLORS["violet"], 360,
        ref_lines=[(500000, "₹5L Safe Minimum", COLORS["amber"]), (50000, "₹50K Danger", COLORS["red"])]), use_container_width=True)
    
    # FY25-26 comparison
    st.markdown('<p class="section-head">FY 2025-26 Monthly Cash Flow</p>', unsafe_allow_html=True)
    st.plotly_chart(grouped_bar(MONTHS_FY2, {"Inflows": FY2_CREDITS, "Outflows": FY2_DEBITS}, 400), use_container_width=True)
    st.plotly_chart(net_bar(MONTHS_FY2, FY2_NET, 280), use_container_width=True)
    
    # Cash Buffer Analysis
    st.markdown('<p class="section-head">Cash Buffer Analysis</p>', unsafe_allow_html=True)
    daily_burn = SUMMARY_FY1['total_debits'] / 365
    buffer_days = [round(bal / daily_burn, 1) for bal in FY1_CLOSING]
    fig = go.Figure(go.Bar(x=MONTHS_FY1, y=buffer_days,
        marker_color=[COLORS["red"] if d < 5 else COLORS["amber"] if d < 15 else COLORS["green"] for d in buffer_days],
        text=[f"{d:.0f}d" for d in buffer_days], textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono")))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        yaxis=dict(title="Days of Operating Expenses Covered", showgrid=True, gridcolor=COLORS["grid"]))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="alert-box">🚨 In Aug-24 and Feb-25, cash buffer dropped below <strong>1 day</strong> of operating expenses. A single delayed payment could have caused defaults.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 4: REVENUE INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
with tab_rev:
    st.markdown('<p class="section-head">Revenue Sources — Who Pays You</p>', unsafe_allow_html=True)
    
    total_rev = sum(r[1] for r in REVENUE_SOURCES)
    kr1, kr2, kr3, kr4 = st.columns(4)
    kr1.metric("Total Revenue (Both FY)", fmt(total_rev), f"{SUMMARY_FY1['credit_count'] + SUMMARY_FY2['credit_count']} txns")
    kr2.metric("Top Client Share", f"{REVENUE_SOURCES[0][2]}%", REVENUE_SOURCES[0][0][:20])
    top2 = REVENUE_SOURCES[0][2] + REVENUE_SOURCES[1][2]
    kr3.metric("Top 2 Client Share", f"{top2:.1f}%", "⚠️ HIGH RISK" if top2 > 50 else "OK")
    kr4.metric("Avg Payment Size", fmt(total_rev / (SUMMARY_FY1['credit_count'] + SUMMARY_FY2['credit_count'])))
    
    cr, cb = st.columns([2, 3])
    with cr:
        fig = donut([r[0] for r in REVENUE_SOURCES], [r[1] for r in REVENUE_SOURCES],
                    [COLORS["blue"], COLORS["lblue"], COLORS["sky"], COLORS["emerald"], COLORS["green"], COLORS["violet"], COLORS["teal"]],
                    f"<b>{fmt(total_rev)}</b><br>Revenue", 400)
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        fig = hbar([r[0] for r in REVENUE_SOURCES], [r[1] for r in REVENUE_SOURCES],
                   [COLORS["blue"], COLORS["lblue"], COLORS["sky"], COLORS["emerald"], COLORS["green"], COLORS["violet"], COLORS["teal"]], 400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Client Dependency Score
    st.markdown('<p class="section-head">Client Dependency Score</p>', unsafe_allow_html=True)
    monthly_burn = SUMMARY_FY1['total_debits'] / 12
    for rname, ramt, rpct, rcnt in REVENUE_SOURCES[:5]:
        months_to_insolvency = SUMMARY_FY1['closing_balance'] / monthly_burn if rpct > 10 else 99
        risk = "🔴 CRITICAL" if rpct > 25 else "🟠 HIGH" if rpct > 15 else "🟡 MEDIUM" if rpct > 10 else "⚪ LOW"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;padding:8px 12px;background:#f8fafc;border-radius:6px">
            <div style="min-width:200px;font-weight:700;font-size:0.9rem">{rname[:25]}</div>
            <div style="font-family:'JetBrains Mono';font-weight:700">{rpct}%</div>
            <div style="flex:1"><div style="background:#e2e8f0;border-radius:4px;height:8px"><div style="background:{'#dc2626' if rpct>25 else '#ea580c' if rpct>15 else '#f59e0b'};width:{rpct}%;height:8px;border-radius:4px"></div></div></div>
            <div style="font-size:0.82rem">{risk}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="alert-box">
        🎯 <strong>Concentration Risk:</strong> If Wynberg Allen School ({REVENUE_SOURCES[0][2]}%) stops paying,
        the company has <strong>{SUMMARY_FY1['closing_balance']/monthly_burn:.1f} months</strong> before insolvency at current burn rate.
        Revenue from top 2 clients = <strong>{top2:.1f}%</strong> — well above the 40% safe threshold.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 5: SUSPICIOUS TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════
with tab_sus:
    st.markdown('<p class="section-head">🔴 Forensic Audit — Flagged Entities</p>', unsafe_allow_html=True)
    
    crit = [s for s in SUSPICIOUS_ENTITIES if s['severity'] == 'Critical']
    high = [s for s in SUSPICIOUS_ENTITIES if s['severity'] == 'High']
    med = [s for s in SUSPICIOUS_ENTITIES if s['severity'] == 'Medium']
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("🔴 CRITICAL", f"{len(crit)} findings", fmt(sum(s['amount'] for s in crit)))
    sc2.metric("🟠 HIGH", f"{len(high)} findings", fmt(sum(s['amount'] for s in high)))
    sc3.metric("🟡 MEDIUM", f"{len(med)} findings", fmt(sum(s['amount'] for s in med)))
    
    # Bar chart
    sw = [s for s in SUSPICIOUS_ENTITIES if s['amount'] > 0]
    fig = hbar(
        [s['entity'][:35] for s in sw],
        [s['amount'] for s in sw],
        [SEVERITY_COLORS[s['severity']] for s in sw], 380)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detail cards
    for s in SUSPICIOUS_ENTITIES:
        icon = SEVERITY_ICON.get(s['severity'], "⚪")
        with st.expander(f"{icon}  **{s['entity']}** — {fmt(s['amount'])} ({s['severity']})"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Amount", fmt(s['amount']))
            m2.metric("Txns", s['count'])
            m3.metric("Avg/Txn", fmt(s['amount']/s['count']) if s['count'] > 0 else "N/A")
            m4.metric("Account", s['account'][:20])
            st.markdown(f"""<div style="background:{SEVERITY_BG[s['severity']]};border-left:4px solid {SEVERITY_COLORS[s['severity']]};
                border-radius:.5rem;padding:1rem;margin:.5rem 0;font-size:.88rem;line-height:1.7">
                <strong style="color:{SEVERITY_COLORS[s['severity']]}">Risk: {s['risk']}</strong><br>{s['detail']}</div>""", unsafe_allow_html=True)
    
    # Benford's Law
    st.markdown('<p class="section-head">Benford\'s Law Analysis</p>', unsafe_allow_html=True)
    st.caption("First-digit distribution of all 2,361 debit amounts vs Benford's expected distribution")
    st.plotly_chart(benford_chart(BENFORD_ACTUAL, BENFORD_EXPECTED, 350), use_container_width=True)
    
    total_b = sum(BENFORD_ACTUAL.get(str(d), 0) for d in range(1, 10))
    act_1 = BENFORD_ACTUAL.get("1", 0) / total_b * 100
    st.markdown(f"""
    <div class="insight-box">
        <strong>Benford Analysis:</strong> First digit "1" appears in <strong>{act_1:.1f}%</strong> of transactions 
        (expected: 30.1%). {"⚠️ Significant deviation — suggests potential manipulation." if abs(act_1 - 30.1) > 5 else "Within acceptable range."}
        Round-amount transactions: <strong>{ROUND_AMOUNT_PCT}%</strong> of all debits — very high for genuine business payments.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 6: RATURI FAMILY ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab_raturi:
    st.markdown('<p class="section-head">🔍 Special Investigation — Raturi Family</p>', unsafe_allow_html=True)
    st.caption("All transactions containing 'RATURI' across FY 2024-25 and FY 2025-26")
    
    total_deb = sum(t[1] for t in RATURI_TRANSACTIONS)
    total_cred = sum(t[2] for t in RATURI_TRANSACTIONS)
    amounts = [t[1] for t in RATURI_TRANSACTIONS if t[1] > 0]
    
    rk1, rk2, rk3, rk4, rk5 = st.columns(5)
    rk1.metric("Total Transactions", len(RATURI_TRANSACTIONS))
    rk2.metric("Total Debits", fmt(total_deb))
    rk3.metric("Total Credits", fmt(total_cred))
    rk4.metric("Net Outflow", fmt(total_deb - total_cred))
    rk5.metric("Account", "27711530000524", help="HDFC Savings Account — Sumit Raturi")
    
    st.markdown("")
    
    # Stats
    if amounts:
        import statistics
        rk6, rk7, rk8, rk9 = st.columns(4)
        rk6.metric("Min Payment", fmt(min(amounts)))
        rk7.metric("Max Payment", fmt(max(amounts)))
        rk8.metric("Average", fmt(statistics.mean(amounts)))
        rk9.metric("Median", fmt(statistics.median(amounts)))
    
    # Monthly chart
    st.markdown('<p class="sub-head">Monthly Payment Pattern</p>', unsafe_allow_html=True)
    r_months = sorted(RATURI_MONTHLY.keys(), key=lambda x: (
        ['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar'].index(x[:3]) + (0 if '24' in x or '25' in x and x[:3] in ['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'] else 12 if '25' in x else 24)
    ) if x[:3] in ['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar'] else 99)
    # Simple sort by parsing
    def month_sort_key(m):
        parts = m.split('-')
        mon_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
        yr = int(parts[1]) + 2000
        mn = mon_map.get(parts[0], 0)
        return yr * 100 + mn
    r_months = sorted(RATURI_MONTHLY.keys(), key=month_sort_key)
    r_amts = [RATURI_MONTHLY[m]['debit'] for m in r_months]
    r_cnts = [RATURI_MONTHLY[m]['count'] for m in r_months]
    
    st.plotly_chart(dual_axis(r_months, r_amts, r_cnts, "₹ Paid", "Txn Count", COLORS["orange"], 360), use_container_width=True)
    
    # Cumulative
    st.markdown('<p class="sub-head">Cumulative Payment Curve</p>', unsafe_allow_html=True)
    dates_r = [t[0] for t in RATURI_TRANSACTIONS if t[1] > 0]
    amts_r = [t[1] for t in RATURI_TRANSACTIONS if t[1] > 0]
    st.plotly_chart(cumulative_line(dates_r, amts_r, COLORS["orange"], 300), use_container_width=True)
    
    # Amount histogram
    st.markdown('<p class="sub-head">Payment Amount Distribution</p>', unsafe_allow_html=True)
    if amounts:
        st.plotly_chart(histogram(amounts, 15, COLORS["orange"], 280), use_container_width=True)
    
    # Full transaction table
    st.markdown('<p class="section-head">Complete Transaction Ledger — Sumit Raturi</p>', unsafe_allow_html=True)
    df_r = pd.DataFrame(RATURI_TRANSACTIONS, columns=["Date", "Debit", "Credit", "Narration", "FY"])
    df_r["Debit"] = df_r["Debit"].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "")
    df_r["Credit"] = df_r["Credit"].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "")
    df_r.index += 1
    st.dataframe(df_r, use_container_width=True, height=600)
    
    # Risk Assessment
    st.markdown(f"""
    <div class="amber-box">
        <strong>🔍 Forensic Assessment — Sumit Raturi (A/c: 27711530000524)</strong><br><br>
        <strong>Profile:</strong> 43 transactions across 2 fiscal years. HDFC savings account — <strong>same branch as company</strong> (277 prefix = Mussoorie HDFC).
        This suggests a local individual, likely an <strong>employee or family member of a promoter</strong>.<br><br>
        <strong>Pattern:</strong> Payments range from ₹3K to ₹73.6K. Mix of fund transfers (FT-DR) and cheque payments (CHQ).
        2 UPI credits (₹3K + ₹5K + ₹30K) suggest <strong>partial refunds or repayments</strong> — indicating personal rather than business nature.<br><br>
        <strong>Frequency:</strong> 1-3 payments per month, irregular spacing. Not consistent with salary (would be monthly fixed).
        More consistent with <strong>ad-hoc expense reimbursements or drawings</strong>.<br><br>
        <strong>Risk Level: 🟡 MEDIUM</strong> — Net outflow of {fmt(total_deb - total_cred)} across 2 years is moderate.
        The mix of FT + CHQ + UPI refunds suggests this is likely a <strong>trusted employee with drawing privileges</strong>.
        Recommend: Obtain employment records, verify role, ensure proper documentation for each payment.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 7: AMIT ACCOUNT ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab_amit:
    st.markdown('<p class="section-head">🔍 Special Investigation — Amit Accounts</p>', unsafe_allow_html=True)
    st.caption("All transactions containing 'AMIT' — multiple individuals identified")
    
    # Classify Amit types
    amit_types = defaultdict(lambda: {'total':0, 'count':0, 'txns':[]})
    for t in AMIT_TRANSACTIONS:
        date, w, d, atype, narr, fy = t
        amit_types[atype]['total'] += w
        amit_types[atype]['count'] += 1
        amit_types[atype]['txns'].append(t)
    
    # Summary metrics
    total_amit = sum(v['total'] for v in amit_types.values())
    ak1, ak2, ak3 = st.columns(3)
    ak1.metric("Total AMIT Transactions", len(AMIT_TRANSACTIONS))
    ak2.metric("Total Outflow", fmt(total_amit))
    ak3.metric("Distinct Identities", len(amit_types))
    
    # Breakdown by type
    st.markdown('<p class="sub-head">Breakdown by Individual</p>', unsafe_allow_html=True)
    type_items = sorted(amit_types.items(), key=lambda x: -x[1]['total'])
    fig = hbar(
        [f"{name} ({v['count']} txns)" for name, v in type_items],
        [v['total'] for _, v in type_items],
        [COLORS["blue"], COLORS["violet"], COLORS["orange"], COLORS["teal"], COLORS["pink"]][:len(type_items)],
        300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly stacked bar by type
    st.markdown('<p class="sub-head">Monthly Payment by Amit Type</p>', unsafe_allow_html=True)
    amit_monthly = defaultdict(lambda: defaultdict(float))
    for t in AMIT_TRANSACTIONS:
        date, w, d, atype, narr, fy = t
        if w > 0:
            try:
                from datetime import datetime
                dt = datetime.strptime(date, "%d/%m/%y")
                mkey = dt.strftime('%b-%y')
                amit_monthly[mkey][atype] += w
            except: pass
    
    a_months = sorted(amit_monthly.keys(), key=month_sort_key if 'month_sort_key' in dir() else lambda x: x)
    def mk_sort(m):
        parts = m.split('-')
        mon_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
        yr = int(parts[1]) + 2000
        mn = mon_map.get(parts[0], 0)
        return yr * 100 + mn
    a_months = sorted(amit_monthly.keys(), key=mk_sort)
    
    fig = go.Figure()
    type_colors = {"Amit Kumar (FT)": COLORS["blue"], "Amit Kumar (CHQ)": COLORS["violet"],
                   "Amit Semwal (NEFT)": COLORS["orange"], "Amit Singh S/O Mangal": COLORS["teal"], "Other Amit": COLORS["slate"]}
    for atype in amit_types.keys():
        vals = [amit_monthly[m].get(atype, 0) for m in a_months]
        fig.add_trace(go.Bar(name=atype, x=a_months, y=vals,
            marker_color=type_colors.get(atype, COLORS["slate"])))
    fig.update_layout(**PLOTLY_LAYOUT, height=380, barmode="stack",
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"], title="Amount (₹)"))
    st.plotly_chart(fig, use_container_width=True)
    
    # Detail per Amit type
    for atype, data in type_items:
        with st.expander(f"**{atype}** — {fmt(data['total'])} ({data['count']} txns)"):
            df_a = pd.DataFrame(data['txns'], columns=["Date", "Debit", "Credit", "Type", "Narration", "FY"])
            df_a["Debit"] = df_a["Debit"].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "")
            df_a["Credit"] = df_a["Credit"].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "")
            df_a.index += 1
            st.dataframe(df_a[["Date", "Debit", "Credit", "Narration", "FY"]], use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <strong>🔍 Forensic Assessment — Amit Accounts</strong><br><br>
        <strong>4 distinct individuals identified:</strong><br>
        1. <strong>Amit Kumar (A/c: 50100151817759)</strong> — Personal HDFC savings account. {amit_types.get('Amit Kumar (FT)',{}).get('count',0)} FT + {amit_types.get('Amit Kumar (CHQ)',{}).get('count',0)} CHQ = {fmt(amit_types.get('Amit Kumar (FT)',{}).get('total',0) + amit_types.get('Amit Kumar (CHQ)',{}).get('total',0))}. Likely <strong>trusted employee / site supervisor</strong> with cheque signing authority.<br>
        2. <strong>Amit Semwal</strong> — Via SBI NEFT. {amit_types.get('Amit Semwal (NEFT)',{}).get('count',0)} txns = {fmt(amit_types.get('Amit Semwal (NEFT)',{}).get('total',0))}. Separate individual — <strong>laborer or small contractor</strong>.<br>
        3. <strong>Amit Singh S/O Mangal Singh</strong> — Via UBI NEFT. {amit_types.get('Amit Singh S/O Mangal',{}).get('count',0)} txns = {fmt(amit_types.get('Amit Singh S/O Mangal',{}).get('total',0))}. <strong>Different bank (Union Bank), different person</strong>.<br>
        4. <strong>AMIT-CHQPAID</strong> — Cheque withdrawals signed by "Amit" on behalf of company. These represent <strong>cash withdrawals</strong> through cheques.<br><br>
        <strong>Risk Level: 🟡 MEDIUM-HIGH</strong> — Amit Kumar receives both FT and CHQ payments totalling {fmt(amit_types.get('Amit Kumar (FT)',{}).get('total',0) + amit_types.get('Amit Kumar (CHQ)',{}).get('total',0))} to a personal account.
        Combined with AMIT-CHQ cash withdrawals, this individual has significant financial access.
        Recommend: Verify employment, review cheque signing authority, ensure all payments are documented.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 8: VENDOR INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
with tab_vendor:
    st.markdown('<p class="section-head">Vendor Scorecard — Top 30 Payees</p>', unsafe_allow_html=True)
    
    all_v_data = []
    for cat in EXPENSE_CATEGORIES:
        for vname, vamt, vcnt in cat['vendors']:
            avg = vamt / max(vcnt, 1)
            round_pct = 100  # approximation since most construction payments are round
            all_v_data.append({
                "Vendor": vname[:30], "Total": vamt, "Txns": vcnt,
                "Avg/Txn": round(avg), "Category": cat['name'],
            })
    
    df_v = pd.DataFrame(all_v_data).sort_values("Total", ascending=False).head(30)
    df_v.index = range(1, len(df_v)+1)
    df_v["Total"] = df_v["Total"].apply(lambda x: f"₹{x:,.0f}")
    df_v["Avg/Txn"] = df_v["Avg/Txn"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(df_v, use_container_width=True, height=600)
    
    # Concentration Analysis
    st.markdown('<p class="section-head">Vendor Concentration Risk</p>', unsafe_allow_html=True)
    all_v_sorted = sorted(all_v_data, key=lambda x: -x['Total'])
    total_spend = sum(v['Total'] for v in all_v_sorted)
    
    top5_pct = sum(v['Total'] for v in all_v_sorted[:5]) / total_spend * 100
    top10_pct = sum(v['Total'] for v in all_v_sorted[:10]) / total_spend * 100
    top20_pct = sum(v['Total'] for v in all_v_sorted[:20]) / total_spend * 100
    
    vc1, vc2, vc3 = st.columns(3)
    vc1.metric("Top 5 Vendors", f"{top5_pct:.1f}%", "of total spend")
    vc2.metric("Top 10 Vendors", f"{top10_pct:.1f}%", "of total spend")
    vc3.metric("Top 20 Vendors", f"{top20_pct:.1f}%", "of total spend")
    
    # Cost Optimization
    st.markdown('<p class="section-head">Cost Optimization Opportunities</p>', unsafe_allow_html=True)
    big_vendors = [v for v in all_v_data if v['Total'] > 500000]
    st.markdown(f'<div class="green-box"><strong>{len(big_vendors)} vendors</strong> with >₹5L annual spend — candidates for rate contracts. Potential savings: <strong>₹25-40L/year</strong> (5-8% on consolidated volumes).</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 9: DEBT & EMI ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab_debt:
    st.markdown('<p class="section-head">Debt & EMI Burden</p>', unsafe_allow_html=True)
    
    de1, de2, de3, de4 = st.columns(4)
    de1.metric("Active Loans", len(EMI_DETAILS))
    de2.metric("Monthly EMI", fmt(EMI_MONTHLY_TOTAL))
    de3.metric("Annual Burden", fmt(EMI_ANNUAL_TOTAL))
    de4.metric("EMI as % Revenue (FY1)", f"{EMI_ANNUAL_TOTAL/SUMMARY_FY1['total_credits']*100:.1f}%")
    
    for emi in EMI_DETAILS:
        st.markdown(f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin:8px 0">
            <strong>EMI #{emi['id']}</strong> · {emi['type']}<br>
            <span class="mono">₹{emi['monthly']:,}/month</span> · <span class="mono">₹{emi['annual']:,}/year</span><br>
            <span style="color:#64748b;font-size:0.82rem">{emi['status']}</span>
        </div>""", unsafe_allow_html=True)
    
    # DSCR Analysis
    st.markdown('<p class="section-head">Debt Service Coverage Ratio (DSCR)</p>', unsafe_allow_html=True)
    dscr_vals = [(c - d) / EMI_MONTHLY_TOTAL if EMI_MONTHLY_TOTAL > 0 else 0 for c, d in zip(FY1_CREDITS, FY1_DEBITS)]
    fig = go.Figure(go.Bar(x=MONTHS_FY1, y=dscr_vals,
        marker_color=[COLORS["red"] if v < 1 else COLORS["amber"] if v < 2 else COLORS["green"] for v in dscr_vals],
        text=[f"{v:.1f}x" for v in dscr_vals], textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono")))
    fig.add_hline(y=1.0, line_dash="dash", line_color=COLORS["red"], annotation_text="DSCR = 1.0 (minimum)")
    fig.update_layout(**PLOTLY_LAYOUT, height=320,
        yaxis=dict(title="DSCR", showgrid=True, gridcolor=COLORS["grid"]))
    st.plotly_chart(fig, use_container_width=True)
    
    below_1 = sum(1 for v in dscr_vals if v < 1)
    st.markdown(f'<div class="alert-box">⚠️ DSCR below 1.0 in <strong>{below_1}/12 months</strong> — company cannot service debt from operating cash flow. O/S Interest Recovery entries confirm overdue payments.</div>', unsafe_allow_html=True)
    
    # Restructuring scenarios
    st.markdown('<p class="sub-head">Loan Restructuring Scenarios</p>', unsafe_allow_html=True)
    for reduction, label in [(0, "Current"), (0.2, "20% EMI Reduction"), (0.3, "30% EMI Reduction")]:
        new_emi = EMI_MONTHLY_TOTAL * (1 - reduction)
        annual_save = EMI_ANNUAL_TOTAL * reduction
        st.markdown(f"""<div style="display:flex;gap:20px;padding:8px 12px;background:{'#f0fdf4' if reduction > 0 else '#f8fafc'};border-radius:6px;margin-bottom:4px">
            <div style="min-width:180px;font-weight:700">{label}</div>
            <div class="mono">₹{new_emi:,.0f}/month</div>
            <div class="mono">Save ₹{annual_save:,.0f}/year</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 10: RECOMMENDATIONS & ACTION PLAN
# ═══════════════════════════════════════════════════════════════════
with tab_reco:
    st.markdown('<p class="section-head">🎯 The Profit Bridge</p>', unsafe_allow_html=True)
    st.caption("Transforming FY24-25 loss into projected profit")
    
    pb = PROFIT_BRIDGE
    fig = waterfall(
        ["Current Loss", "Stop Leakages", "Cost Reduction", "Revenue Growth", "Tax Optimization", "Projected Profit"],
        [pb['current_loss_fy1'], pb['stop_leakages'], pb['cost_reduction'], pb['revenue_growth'], pb['tax_optimization'], pb['projected_profit']],
        ["absolute", "relative", "relative", "relative", "relative", "total"], 420)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="green-box">
        <strong>✅ Bottom Line:</strong> Your company earns ₹10Cr+ revenue. Even 10% margin = ₹1Cr profit.
        The loss is caused by ₹46.4L suspicious Noorkhan payments, ₹1.67Cr untraceable cash, and ₹42L related-party leakage.
        <strong>Fix these and you're profitable immediately.</strong>
    </div>""", unsafe_allow_html=True)
    
    # Savings donut
    savings = [
        ("Stop Noorkhan", 4640000, COLORS["red"]),
        ("Vendor Consolidation", 3500000, COLORS["amber"]),
        ("Recover Rajender Kumar", 2550000, COLORS["rose"]),
        ("Separate Personal Exp", 4200000, COLORS["orange"]),
        ("GST Input Credit", 1500000, COLORS["green"]),
        ("Reduce Sub-contracting", 2000000, COLORS["violet"]),
        ("Eliminate Excess Cash", 2000000, COLORS["red"]),
        ("Fuel Savings", 400000, COLORS["sky"]),
        ("Refinance EMI", 600000, COLORS["blue"]),
        ("GST Compliance", 400000, COLORS["teal"]),
    ]
    tot_sav = sum(s[1] for s in savings)
    fig = donut([s[0] for s in savings], [s[1] for s in savings], [s[2] for s in savings],
                f"<b>{fmt(tot_sav)}</b><br>Potential", 380)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed recommendations
    for section in RECOMMENDATIONS:
        st.markdown(f"""<div style="background:{section['color']}0d;border:1px solid {section['color']}33;
            border-radius:.5rem;padding:.7rem 1rem;margin-top:1rem;margin-bottom:.4rem">
            <strong style="color:{section['color']};font-size:1.05rem">{section['section']}</strong>
            <span style="float:right;background:{section['color']}1a;color:{section['color']};
            padding:2px 10px;border-radius:12px;font-size:.8rem;font-weight:700">Potential: {section['potential']}</span>
        </div>""", unsafe_allow_html=True)
        
        for action, saving, timeline, difficulty, detail in section['items']:
            diff_color = COLORS["red"] if difficulty == "Hard" else COLORS["amber"] if difficulty == "Medium" else COLORS["green"]
            with st.expander(f"**{action}** — 💰 {saving} · ⏱ {timeline} · {'🔴' if difficulty=='Hard' else '🟡' if difficulty=='Medium' else '🟢'} {difficulty}"):
                st.markdown(f'<div class="insight-box">{detail}</div>', unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                r1.metric("💰 Savings", saving)
                r2.metric("⏱ Timeline", timeline)
                r3.metric("Difficulty", difficulty)
    
    # 90-Day Gantt
    st.markdown('<p class="section-head">📋 90-Day Execution Timeline</p>', unsafe_allow_html=True)
    phases = [
        ("Week 1", 0, 1, COLORS["red"]),
        ("Week 2-3", 1, 2, COLORS["orange"]),
        ("Month 2", 3, 4, COLORS["amber"]),
        ("Month 3", 7, 5, COLORS["green"]),
    ]
    st.plotly_chart(gantt_timeline(phases, 110), use_container_width=True)
    
    tasks = [
        ("Week 1", COLORS["red"], "Freeze Noorkhan payments · Investigate Rajender Kumar · Set ₹5L min balance · Demand invoices from all laborers"),
        ("Week 2-3", COLORS["orange"], "Stop cash >₹50K · Setup UPI/NEFT for all vendors · Separate Ashish Sharma · Apply for OD facility"),
        ("Month 2", COLORS["amber"], "Consolidate to 4-5 material vendors · File pending GST · Get GST invoices from laborers · Monthly filing"),
        ("Month 3", COLORS["green"], "Reduce sub-contracting (2 categories in-house) · Setup bill discounting · Bid for 2 new PWD tenders · Refinance EMI"),
    ]
    for phase, color, task in tasks:
        st.markdown(f"""<div style="display:flex;gap:12px;margin-bottom:6px;align-items:flex-start">
            <div style="background:{color};color:white;font-size:.75rem;font-weight:800;padding:4px 10px;border-radius:4px;flex-shrink:0;min-width:72px;text-align:center">{phase}</div>
            <div style="font-size:.86rem;line-height:1.6">{task}</div></div>""", unsafe_allow_html=True)
    
    st.success("🎯 **₹24 Cr turnover across 2 years. Even 10% margin = ₹2.4 Cr profit. The path is clear — discipline, not miracles.**")


# ═══════════════════════════════════════════════════════════════════
# TAB 11: RAW DATA & SEARCH
# ═══════════════════════════════════════════════════════════════════
with tab_raw:
    st.markdown('<p class="section-head">📑 Transaction Data Explorer</p>', unsafe_allow_html=True)
    
    # Build a searchable dataframe from all categories
    raw_rows = []
    for cat in EXPENSE_CATEGORIES:
        for vname, vamt, vcnt in cat['vendors']:
            raw_rows.append({
                "Category": cat['name'],
                "Vendor/Payee": vname,
                "Total Amount": vamt,
                "Transactions": vcnt,
                "Avg per Txn": round(vamt / max(vcnt, 1)),
                "Type": "Debit",
            })
    for rname, ramt, rpct, rcnt in REVENUE_SOURCES:
        raw_rows.append({
            "Category": "Revenue",
            "Vendor/Payee": rname,
            "Total Amount": ramt,
            "Transactions": rcnt,
            "Avg per Txn": round(ramt / max(rcnt, 1)),
            "Type": "Credit",
        })
    
    df_raw = pd.DataFrame(raw_rows)
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        cat_filter = st.multiselect("Category", df_raw["Category"].unique().tolist(), default=df_raw["Category"].unique().tolist())
        type_filter = st.multiselect("Type", ["Debit", "Credit"], default=["Debit", "Credit"])
        search = st.text_input("Search Vendor Name", "")
        min_amt = st.number_input("Min Amount (₹)", 0, 100000000, 0, step=50000)
    
    # Apply filters
    mask = (df_raw["Category"].isin(cat_filter)) & (df_raw["Type"].isin(type_filter)) & (df_raw["Total Amount"] >= min_amt)
    if search:
        mask = mask & df_raw["Vendor/Payee"].str.contains(search.upper(), case=False, na=False)
    
    df_filtered = df_raw[mask].sort_values("Total Amount", ascending=False)
    
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Matching Records", len(df_filtered))
    fc2.metric("Total Amount", fmt(df_filtered["Total Amount"].sum()))
    fc3.metric("Avg Amount", fmt(df_filtered["Total Amount"].mean()) if len(df_filtered) > 0 else "₹0")
    
    df_display = df_filtered.copy()
    df_display["Total Amount"] = df_display["Total Amount"].apply(lambda x: f"₹{x:,.0f}")
    df_display["Avg per Txn"] = df_display["Avg per Txn"].apply(lambda x: f"₹{x:,.0f}")
    df_display.index = range(1, len(df_display)+1)
    st.dataframe(df_display, use_container_width=True, height=600)
    
    # CSV download
    csv = df_filtered.to_csv(index=False)
    st.download_button("📥 Download as CSV", csv, "kwality_transactions.csv", "text/csv")

    # Raturi quick view
    st.markdown('<p class="section-head">Quick View — Raturi Transactions</p>', unsafe_allow_html=True)
    df_rq = pd.DataFrame(RATURI_TRANSACTIONS, columns=["Date", "Debit", "Credit", "Narration", "FY"])
    df_rq.index += 1
    st.dataframe(df_rq, use_container_width=True, height=300)
    
    st.markdown('<p class="section-head">Quick View — Amit Transactions</p>', unsafe_allow_html=True)
    df_aq = pd.DataFrame(AMIT_TRANSACTIONS, columns=["Date", "Debit", "Credit", "Type", "Narration", "FY"])
    df_aq.index += 1
    st.dataframe(df_aq, use_container_width=True, height=300)


# ─── FOOTER ───────────────────────────────────────────────────────
st.divider()
st.caption("📊 Forensic Financial Analysis · M/S. Kwality Construction Company · FY 2024-25 + FY 2025-26 · HDFC Bank A/c 27718630000017 · Confidential")
