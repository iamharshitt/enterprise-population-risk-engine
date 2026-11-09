# Financial Risk Analytics Dashboard

An independent portfolio project for exploring rule-based transaction risk in a synthetic dataset. The bundled synthetic dataset contains 10,000 transactions across 1,000 distinct accounts.

The dashboard shows transaction volume, account summaries, and flagged transactions. A transaction is flagged when it follows another transaction for the same account within 30 seconds or changes recorded location within five minutes. A transaction that matches both rules is counted once in the flagged-transaction total. These rules are for triage and do not establish fraud, physical travel, or churn.

## Delivery and validation

I scoped the dashboard around two tasks: review transaction signals across the dataset and investigate a single account. During validation, I found that 144 rule matches came from 139 distinct transactions. I corrected the dashboard to report unique flagged transactions and checked the result against the bundled data. I also verified account lookup and tested missing, empty, and incompatible demo data in Streamlit.

## Run the dashboard

Use Python 3.12 and run the following commands in a terminal.

```sh
git clone https://github.com/iamharshitt/enterprise-population-risk-engine.git
cd enterprise-population-risk-engine
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app reads its bundled demo data from the local risk_analytics.db file next to app.py. It runs without an external database service.

## Repository contents

- app.py contains the Streamlit dashboard and the SQLite aggregation queries.
- risk_analytics.db contains the synthetic dashboard data.
- The notebook records exploratory data generation and feature engineering. Some cells recreate the database or overwrite app.py. Review those cells before running them, and use a separate checkout if you want to rerun the experiments.
