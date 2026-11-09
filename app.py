import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import streamlit as st

DATABASE_PATH = Path(__file__).resolve().with_name("risk_analytics.db")

kpi_query = """
SELECT COUNT(*) AS total_tx, COUNT(DISTINCT user_id) AS total_users,
       COALESCE(SUM(amount), 0) AS total_volume,
       COALESCE(AVG(amount), 0) AS avg_tx_size
FROM customer_transactions;
"""

feature_query = """
WITH velocity_base AS (
    SELECT user_id, amount, location, CAST(strftime('%s', transaction_timestamp) AS INTEGER) AS transaction_epoch,
        LAG(CAST(strftime('%s', transaction_timestamp) AS INTEGER)) OVER (PARTITION BY user_id ORDER BY transaction_timestamp, transaction_id) as previous_epoch,
        LAG(location, 1) OVER (PARTITION BY user_id ORDER BY transaction_timestamp, transaction_id) as prev_loc
    FROM customer_transactions
),
risk_flagged_base AS (
    SELECT user_id, amount,
        CASE WHEN (transaction_epoch - previous_epoch) BETWEEN 0 AND 30 THEN 1 ELSE 0 END as velocity_alert,
        CASE WHEN location <> prev_loc AND (transaction_epoch - previous_epoch) BETWEEN 0 AND 300 THEN 1 ELSE 0 END as travel_alert
    FROM velocity_base
)
SELECT user_id, COUNT(*) as total_tx_count, ROUND(SUM(amount), 2) as total_spent,
    ROUND(AVG(amount), 2) as avg_tx_value, ROUND(MAX(amount), 2) as max_single_tx,
    SUM(velocity_alert) as velocity_violations, SUM(travel_alert) as travel_violations,
    SUM(CASE WHEN velocity_alert = 1 OR travel_alert = 1 THEN 1 ELSE 0 END) AS flagged_transactions,
    ROUND(CAST(SUM(velocity_alert) AS REAL) / COUNT(*), 4) * 100 as velocity_risk_pct
FROM risk_flagged_base
GROUP BY user_id;
"""
def load_dashboard_data(database_path):
    uri = database_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        conn.execute("BEGIN")
        return pd.read_sql_query(kpi_query, conn), pd.read_sql_query(feature_query, conn)


st.set_page_config(page_title="Enterprise Population Risk Engine", layout="wide")
st.title("Enterprise Population Risk Engine")
st.caption("Explore rule-based transaction alerts in the bundled synthetic dataset.")

try:
    kpi_df, profiles_df = load_dashboard_data(DATABASE_PATH)
except (sqlite3.Error, pd.errors.DatabaseError):
    st.error("Could not load the transaction database. Restore risk_analytics.db from the repository and check that it contains customer_transactions.")
    st.stop()

if profiles_df.empty:
    st.info("The database contains no transactions to analyze.")
    st.stop()


# --- KPI METRIC CARDS ---
st.caption(f"{kpi_df['total_users'][0]:,} distinct accounts")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Transactions", value=f"{kpi_df['total_tx'][0]:,}")
with col2:
    st.metric(label="Transaction volume", value=f"${kpi_df['total_volume'][0]:,.2f}")
with col3:
    st.metric(label="Average transaction", value=f"${kpi_df['avg_tx_size'][0]:,.2f}")
with col4:
    flagged_transactions = profiles_df['flagged_transactions'].sum()
    st.metric(label="Flagged transactions", value=f"{flagged_transactions:,}")

st.divider()

# --- INTERACTIVE INTERFACE: USER LOOKUP ---
st.subheader("🔍 Account lookup")
search_query = st.text_input("Type a User ID to investigate (e.g., USER_0646):", "").strip().upper()

if search_query:
    filtered_user = profiles_df[profiles_df['user_id'].str.upper() == search_query]
    if not filtered_user.empty:
        st.success(f"🎯 Identity Located for {search_query}")
        
        # Display key insights for searched user
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Total Transactions", f"{filtered_user['total_tx_count'].iat[0]}")
        sc2.metric("Total transaction amount", f"${filtered_user['total_spent'].iat[0]:,.2f}")
        sc3.metric("Velocity Violations", f"{filtered_user['velocity_violations'].iat[0]}")
        sc4.metric("Rapid location changes", f"{filtered_user['travel_violations'].iat[0]}")
        
        # Warning trigger if malicious threshold is met
        if filtered_user['travel_violations'].iat[0] > 0 or filtered_user['velocity_violations'].iat[0] > 0:
            st.warning("Review these rule matches alongside other account activity. Location changes and short intervals can have legitimate causes.")
    else:
        st.warning(f"❌ User ID '{search_query}' was not found in the dataset.")

st.divider()

# --- VISUALIZATIONS SECTION ---
st.subheader("📊 Fleet Anomalies Overview")
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.markdown("**Average transaction amount by account (first 50 IDs)**")
    st.bar_chart(profiles_df.sort_values('user_id').set_index('user_id')['avg_tx_value'].head(50))

with viz_col2:
    st.markdown("**Top 30 accounts by transaction amount**")
    st.bar_chart(profiles_df.sort_values(by='total_spent', ascending=False).set_index('user_id')['total_spent'].head(30))

st.divider()

# --- ADVANCED RISK SEGMENTATION ---
st.subheader("🎯 Account risk signals")
st.markdown("Rule matches are screening signals. An individual transaction can trigger both rules.")

high_risk_sorted = profiles_df.sort_values(by=['travel_violations', 'velocity_violations', 'total_spent'], ascending=False)
st.dataframe(high_risk_sorted, width="stretch")
