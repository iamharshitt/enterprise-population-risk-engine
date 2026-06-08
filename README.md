# Enterprise Financial Risk & Churn Pipeline (10K Scale)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end data analytics and predictive pipeline designed to monitor high-velocity transactions, profile population-level financial risk, and detect early macro-level churn indicators across a simulated fleet of 10,000 active users.

---

## 📊 Live System Telemetry

| Metric | System Dimension |
| :--- | :--- |
| **Total Logged Fleet Transactions** | 10,000 |
| **Total Monitored Financial Volume** | \$16,237,441.61 |
| **Average Ticket Footprint** | \$1,623.74 |
| **Total Pipeline Alerts Triggered** | 144 (~1.44% Alert Rate) |
| **Operational Health Status** | **High Volume / Stable** |

---

## ⚡ Core Engine Features

* **Automated Feature Engineering:** Computes localized transactional velocity windows and dynamic statistical Z-scores to flag anomalous ticket footprints exceeding historical baselines.
* **Risk Behavioral Profiling:** Macro-level population partitioning to isolate high-risk accounts from standard fleet operations.
* **Churn Prediction Pipeline:** Ingests activity degradation patterns to surface customers with a high probability of churn prior to revenue loss.
* **Streamlit Analytical Dashboard:** Interactive frontend built to handle high-velocity states and allow risk analysts to seamlessly triage the 144 active pipeline alerts.

---

## 🛠️ Tech Stack & Architecture

* **Language:** Python 3.9+
* **Data Engineering & Analytics:** Pandas, NumPy, Jupyter Notebook
* **Interactive Frontend UI:** Streamlit Framework
* **Version Control:** Git & GitHub

---

## 🚀 Getting Started

To explore the notebook and launch the interactive analytics server locally, follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME
