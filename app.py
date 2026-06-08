import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Enterprise Population Risk Engine", layout="wide")
st.title("🛡️ Enterprise Population Risk Engine (10K Users Scale)")
st.markdown("Macro-level risk behavioral profiling, automated feature engineering, and high-velocity fleet monitoring.")

# Connect to database
conn = sqlite3.connect("risk_analytics.db")

# 1. Pipeline High-Level KPIs
kpi_query = "SELECT COUNT(transaction_id) as total_tx, SUM(amount) as total_volume, AVG(amount) as avg_tx_size FROM customer_transactions;"
kpi_df = pd.read_sql_query(kpi_query, conn)

# 2. Complete Feature Engineered Profiles for Dashboard
feature_query = """
WITH velocity_base AS (
    SELECT user_id, amount, location, transaction_timestamp,
        LAG(transaction_timestamp, 1) OVER (PARTITION BY user_id ORDER BY transaction_timestamp) as prev_time,
        LAG(location, 1) OVER (PARTITION BY user_id ORDER BY transaction_timestamp) as prev_loc
    FROM customer_transactions
),
risk_flagged_base AS (
    SELECT user_id, amount,
        CASE WHEN (unixepoch(transaction_timestamp) - unixepoch(prev_time)) <= 30 THEN 1 ELSE 0 END as velocity_alert,
        CASE WHEN location <> prev_loc AND (unixepoch(transaction_timestamp) - unixepoch(prev_time)) <= 300 THEN 1 ELSE 0 END as travel_alert
    FROM velocity_base
)
SELECT user_id, COUNT(*) as total_tx_count, ROUND(SUM(amount), 2) as total_spent,
    ROUND(AVG(amount), 2) as avg_tx_value, ROUND(MAX(amount), 2) as max_single_tx,
    SUM(velocity_alert) as velocity_violations, SUM(travel_alert) as travel_violations,
    ROUND(CAST(SUM(velocity_alert) AS REAL) / COUNT(*), 4) * 100 as velocity_risk_pct
FROM risk_flagged_base
GROUP BY user_id;
"""
profiles_df = pd.read_sql_query(feature_query, conn)
conn.close()

# --- KPI METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Total Logged Fleet Transactions", value=f"{kpi_df['total_tx'][0]:,}")
with col2: st.metric(label="Total Monitored Volume", value=f"${kpi_df['total_volume'][0]:,.2f}")
with col3: st.metric(label="Average Ticket Footprint", value=f"${kpi_df['avg_tx_size'][0]:,.2f}")
with col4: 
    total_violations = profiles_df['velocity_violations'].sum() + profiles_df['travel_violations'].sum()
    st.metric(label="Total Pipeline Alerts Triggered", value=f"{total_violations:,}", delta="High Volume", delta_color="inverse")

st.markdown("---")

# --- INTERACTIVE INTERFACE: USER LOOKUP ---
st.subheader("🔍 Real-Time Account Security Interrogation")
search_query = st.text_input("Type a User ID to investigate (e.g., USER_0646):", "").strip().upper()

if search_query:
    filtered_user = profiles_df[profiles_df['user_id'] == search_query]
    if not filtered_user.empty:
        st.success(f"🎯 Identity Located for {search_query}")
        
        # Display key insights for searched user
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Total Transactions", f"{filtered_user['total_tx_count'].values[0]}")
        sc2.metric("Total Capital Outflow", f"${filtered_user['total_spent'].values[0]:,.2f}")
        sc3.metric("Velocity Violations", f"{filtered_user['velocity_violations'].values[0]}")
        sc4.metric("Impossible Travel Flags", f"{filtered_user['travel_violations'].values[0]}")
        
        # Warning trigger if malicious threshold is met
        if filtered_user['travel_violations'].values[0] > 0 or filtered_user['velocity_violations'].values[0] > 0:
            st.error("⚠️ ACTION REQUIRED: Account exhibits highly anomalous temporal-spatial markers. Recommend lock-out flag.")
    else:
        st.warning(f"❌ User ID '{search_query}' not found in current 10k fleet logs.")

st.markdown("---")

# --- VISUALIZATIONS SECTION ---
st.subheader("📊 Fleet Anomalies Overview")
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.markdown("**Distribution of Transaction Value Sizes**")
    st.bar_chart(profiles_df.set_index('user_id')['avg_tx_value'].head(50))

with viz_col2:
    st.markdown("**Top Users by Total Capital Spent ($)**")
    st.line_chart(profiles_df.sort_values(by='total_spent', ascending=False).set_index('user_id')['total_spent'].head(30))

st.markdown("---")

# --- ADVANCED RISK SEGMENTATION ---
st.subheader("🎯 Machine Learning-Ready Risk Aggregations")
st.markdown("This live relational matrix maps individual user vectors across the entire 10,000 row fleet, isolating statistical outliers for threat mitigation.")

high_risk_sorted = profiles_df.sort_values(by=['travel_violations', 'velocity_violations', 'total_spent'], ascending=False)
st.dataframe(high_risk_sorted, use_container_width=True)
