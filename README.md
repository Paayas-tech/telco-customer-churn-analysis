# Telco Customer Churn & Revenue Exposure Analysis

An end-to-end data analytics project diagnosing customer churn dynamics, quantifying recurring revenue leakage, and deploying automated risk-scoring logic using **PostgreSQL** and an **Executive Spreadsheet Dashboard**.

---

## 📌 Executive Summary

* **Customer vs. Revenue Disconnect:** The business has an overall customer churn rate of **26.54%** (1,869 / 7,043 customers), but an annualized Monthly Recurring Revenue (MRR) loss rate of **30.50%** ($139,130.85 lost out of $456,116.60 total MRR).
* **Annualized Revenue Leakage:** The company loses approximately **$1.67M annualized** in recurring revenue. Departing customers represent higher-paying accounts ($74.44/mo average churned vs. $61.26/mo retained).
* **Concentration of Risk:** Customers paying $\ge \$70/\text{month}$ churn at nearly $4\times$ the rate of budget users ($38.07\%$ vs $8.37\%$). The top 500 departing accounts alone drive **$50,400.10/month** (36.2% of all lost MRR).

---

## 📊 Executive Dashboard Preview

[![Telco Customer Churn Dashboard](dashboards/dashboard_preview.png)](https://docs.google.com/spreadsheets/d/1txWOi8K12LKhqEunyHWKLgKyrPt0hz5dq3MdSzjqRlI/edit?usp=sharing)

> 🔗 **Interactive Dashboard Link:** [View Live Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/1txWOi8K12LKhqEunyHWKLgKyrPt0hz5dq3MdSzjqRlI/edit?usp=sharing)  
> *Includes dynamic KPI cards, cohort distribution charts, tenure churn trends, and pivot calculation engines.*

---

## 🔍 Key Findings & Statistical Insights

### 1. Revenue Decile Segmentation (`NTILE`)
Dividing the customer base into 10 spending deciles revealed that churn is heavily concentrated in premium tiers:
* **Decile 1 ($18.25 – $20.05/mo):** 8.37% churn rate ($1,156.85 lost MRR).
* **Deciles 6 & 7 ($70.35 – $85.50/mo):** 38.07% and 37.93% churn rate ($20,013.40 and $21,950.15 lost MRR).
* *Business Takeaway:* Revenue loss is 19x higher in Decile 7 than Decile 1 despite identical cohort headcounts.

### 2. Cumulative Revenue Loss & Pareto Distribution (`SUM() OVER`)
Ranking churning accounts by monthly spend demonstrated asymmetric revenue loss:
* **Top 500 Churners (26.8% of churned accounts):** Represent **$50,400.10 / month** (36.2% of total churn MRR).
* **Top 1,000 Churners (53.5% of churned accounts):** Represent **$92,804.60 / month** (66.7% of total churn MRR).
* *Business Takeaway:* Retention teams can protect over a third of lost revenue by focusing operational outreach on the top 500 accounts ($> \$90/\text{mo}$).

### 3. Statistical Distribution Profile (IQR & Median Analysis)
Parametric and non-parametric comparison between retained and churned cohorts:
* **Median Monthly Bill:** Retained customers median spend is **$64.43**, while churned customers median spend is **$79.65**.
* **Interquartile Range (IQR):** Retained users span an IQR of **63.30** ($25.10 Q1 to $88.40 Q3). Churned users cluster tightly with an IQR of **38.05** ($56.15 Q1 to $94.20 Q3).
* *Business Takeaway:* Churn is tightly concentrated in high-cost tiers; budget users rarely churn.

---

## ⚙️ Automated Churn Risk Scoring Engine

A PostgreSQL stored function (`fn_get_customer_churn_risk`) was built to score accounts from 0 to 100 based on contract type, internet service tier, technical support status, payment method, and tenure.

### Model Validation Results
Evaluating the scoring function against actual customer outcomes across all 7,043 accounts:

| Risk Tier | Total Accounts | Churned Count | Actual Churn Rate | Lost MRR |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL / HIGH RISK** | 2,243 | 1,258 | **56.09%** | **$101,392.20 / mo** |
| **MODERATE RISK** | 2,000 | 463 | **23.15%** | **$25,817.10 / mo** |
| **HEALTHY / LOW RISK** | 2,800 | 148 | **5.29%** | **$11,921.55 / mo** |

*The model captures **72.9% of all lost MRR** within the High Risk tier, providing an operational filter for proactive retention workflows.*

---

## 💡 Strategic Recommendations

1. **Prioritize Top 500 High-Value Accounts:** Focus high-touch support and dedicated account managers on accounts paying $> \$90/\text{mo}$ to secure 36% of exposed MRR.
2. **First-Year Fiber Optic Support Bundling:** Automatically bundle 90 days of complimentary technical support with month-to-month fiber subscriptions to mitigate early lifecycle attrition.
3. **Contract Migration Incentives:** Provide targeted discounts ($5–$10/mo) for moving month-to-month accounts to annual contracts.

---

## 🛠 Tech Stack & Tools

* **Database Engine:** PostgreSQL 17 (pgAdmin 4)
* **SQL Capabilities:** Window Functions (`NTILE`, `SUM OVER`, `ROW_NUMBER`), Statistical Aggregations (`PERCENTILE_CONT`, `STDDEV`), Materialized Views, PL/pgSQL Stored Functions
* **Visualization & Reporting:** Google Sheets (Pivot Tables, Calculated Fields, Executive Dashboard)
* **Version Control:** Git & GitHub

---

## 📁 Project Structure

```text
telco-customer-churn-analysis/
├── README.md
├── .gitignore
├── dashboards/
│   ├── dashboard_preview.png
│   └── telco_churn_dashboard.xlsx
├── data/
│   ├── raw/
│   │   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
│   └── processed/
│       └── cleaned_telco_churn.csv
└── sql/
    ├── 01_schema.sql
    ├── 02_cleaning.sql
    ├── 03_analysis.sql
    ├── 04_advanced_analytics.sql
    └── 05_views_and_procedures.sql