# Telco Customer Churn & Revenue Exposure Analysis

An end-to-end data analytics project diagnosing customer churn dynamics, quantifying recurring revenue leakage, and identifying high-risk customer segments using **PostgreSQL** and an **Executive Spreadsheet Dashboard**.

---

## 📌 Executive Summary

* **Customer vs. Revenue Disconnect:** The business has an overall customer churn rate of **26.54%** (1,869 / 7,043 customers), but an annualized Monthly Recurring Revenue (MRR) loss rate of **30.50%** ($139,130.85 lost out of $456,116.60 total MRR).
* **Annualized Revenue Leakage:** The company loses approximately **$1.67M annualized** in recurring revenue. Departing customers represent higher-paying accounts ($74.44/mo average churned vs. $61.26/mo retained).
* **Concentration of Risk:** A high-risk segment representing only **11.8% of the customer base** accounts for **31.7% of all churn** (593 / 1,869 churned accounts) and nearly **35% of all lost MRR** ($48,489.05/month).

---

## 📊 Executive Dashboard Preview

[![Telco Customer Churn Dashboard](dashboards/dashboard_preview.png)](https://docs.google.com/spreadsheets/d/1txWOi8K12LKhqEunyHWKLgKyrPt0hz5dq3MdSzjqRlI/edit?usp=sharing)

> 🔗 **Interactive Dashboard Link:** [View Live Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/1txWOi8K12LKhqEunyHWKLgKyrPt0hz5dq3MdSzjqRlI/edit?usp=sharing)  
> *Includes dynamic KPI cards, cohort distribution charts, tenure churn trends, and pivot calculation engines.*

---

## 🔍 Key Findings & Root Cause Analysis

### 1. The High-Risk Cohort Profile
Through multi-variable segmentation in SQL, a specific high-exposure customer segment was identified:
* **Contract:** Month-to-month
* **Internet Service:** Fiber Optic
* **Tech Support:** No
* **Tenure:** First year (0–12 months)

**Cohort Performance:**
* **Cohort Churn Rate:** **71.07%** (vs. 26.54% baseline)
* **Lost MRR from Segment:** **$48,489.05 / month** ($581.8K annualized)
* **Average Ticket Size:** **$81.77 / month** (significantly above the account average)

### 2. Contract Structure as the Primary Retention Lever
* **Month-to-Month:** 42.71% churn rate ($122.9K monthly revenue exposure)
* **One-Year Contract:** 11.27% churn rate
* **Two-Year Contract:** 2.83% churn rate
* *Insight:* Customers on longer-term contracts demonstrate a 15x retention improvement over month-to-month subscribers.

### 3. Service & Support Gap in Fiber Optic
* **Fiber Optic Customers:** 41.89% churn rate (compared to 18.96% for DSL)
* **Root Cause:** Fiber customers pay higher price points ($70–$100+/mo) and experience service friction. When paired with no technical support, churn escalates past 70%.

---

## 💡 Strategic Recommendations

1. **Targeted Onboarding for First-Year Fiber Users:**
   * Automatically bundle complimentary 90-day premium Tech Support for new Fiber Optic subscribers.
   * Proactive check-ins at Day 14, 30, and 60 to resolve installation or speed issues before churn triggers.
2. **Contract Migration Incentives:**
   * Offer introductory discounts ($5–$10 off/month) for transitioning month-to-month Fiber users to an annual contract.
3. **Retention Team Prioritization:**
   * Deploy retention resources focused on accounts paying $> $70/mo within their first 12 months, where revenue recovery yield is highest.

---

## 🛠 Tech Stack & Tools

* **Database Engine:** PostgreSQL (pgAdmin 4)
* **Languages & Scripting:** SQL (DDL, Data Cleaning, CTEs, Aggregations, Window Functions)
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
    └── 03_analysis.sql