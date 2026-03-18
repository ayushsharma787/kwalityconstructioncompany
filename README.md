# 🏗️ Kwality Construction — Forensic Financial Dashboard

**Enterprise-grade bank statement analysis dashboard**
M/S. Kwality Construction Company · FY 2024-25 + FY 2025-26
HDFC Bank A/c 27718630000017 · Mussoorie Branch

## 🚀 Run
```bash
pip install -r requirements.txt
streamlit run main.py
```
Opens at http://localhost:8501

## 📊 11 Dashboard Tabs

| Tab | Description |
|-----|-------------|
| 🏠 Executive | Board-level KPIs, waterfall chart, P&L heatmap, YoY comparison |
| 📊 Expenses | Donut + bar + treemap, 13 category drill-downs with vendor detail |
| 📈 Cash Flow | Monthly inflows/outflows, net surplus/deficit, balance trend, cash buffer |
| 💰 Revenue | Source breakdown, concentration risk, client dependency scores |
| 🔴 Suspicious | 8 flagged entities, Benford's Law analysis, round-amount detection |
| 🔍 Raturi | Deep investigation: 43 txns, monthly pattern, cumulative curve, histogram |
| 🔍 Amit | 4 distinct Amits identified: 73 txns, stacked monthly, per-type ledgers |
| 🏗️ Vendors | Top 30 scorecard, concentration risk, cost optimization opportunities |
| 🏦 Debt/EMI | 2 active loans, DSCR analysis, restructuring scenarios |
| 🚀 Roadmap | Profit bridge waterfall, 17 recommendations, 90-day Gantt |
| 📑 Raw Data | Searchable/filterable table with CSV download |

## 📁 Files
```
main.py         → Streamlit app (11 tabs)
bank_data.py    → All extracted transaction data
charts.py       → Reusable Plotly chart builders
utils.py        → Colors, formatting, CSS
requirements.txt
README.md
```

## 🔑 Key Findings
- **2,531 transactions** parsed across 2 fiscal years
- **₹24 Cr revenue** with net loss in FY24-25
- **Noorkhan**: 268 payments (₹46.4L) to personal account — #1 red flag
- **Cash withdrawals**: ₹1.67Cr untraceable
- **Revenue concentration**: 58% from 2 school clients
- **Raturi**: 43 transactions (₹12.3L net outflow) — medium risk
- **Amit**: 4 distinct individuals, 73 transactions (₹21.7L)
- **Potential savings identified**: ₹1.5 Cr/year
