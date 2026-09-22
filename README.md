# Telco Customer Churn & Revenue Exposure Analysis

An end-to-end SQL analytics project investigating customer attrition, revenue leakage, and retention drivers across 7,043 telecommunications customer accounts using PostgreSQL.

---

## 📌 Executive Summary

* **Customer vs. Revenue Disconnect:** The business has an overall customer churn rate of **26.54%** (1,869 / 7,043 customers), but a Monthly Recurring Revenue (MRR) loss rate of **30.50%** ($139,130.85 lost out of $456,116.60 total MRR).
* **Annualized Revenue Leakage:** The company loses approximately **$1.67M annualized** in recurring revenue. Because revenue loss outpaces customer churn, departing customers represent higher-paying accounts ($74.44/mo average churned vs. $61.26/mo retained).
* **Concentration of Risk:** A high-risk segment representing only **11.8% of the customer base** accounts for **31.7% of all churn**[cite: 5, 10] and nearly **35% of all lost MRR** ($48,489.95/month)[cite: 5, 10].

---

## 🔍 Key Business Findings

### 1. The First-Year Drop-Off Cliff
* **47.44%** of customers in their first year (`0-1 Year`) churn.
* First-year cancellations account for **55.5% of total churned users** (1,037 out of 1,869)[cite: 5, 6].
* Retention improves dramatically with tenure: accounts active for 4+ years churn at only **9.51%**, despite paying the highest average monthly charges ($73.95/mo)[cite: 6].

### 2. Contract Friction & Lock-in
* **Month-to-month contracts** experience a **42.71% churn rate**[cite: 7] and represent **88.5% of all churned customers** (1,655 / 1,869)[cite: 5, 7].
* Moving customers to committed plans reduces attrition significantly: churn drops to **11.27%** on 1-year contracts[cite: 7] and **2.83%** on 2-year contracts[cite: 7].

### 3. High-Tier Service Defection (Fiber Optic)
* **Fiber Optic** accounts churn at **41.89%**[cite: 8], compared to **18.96%** for DSL[cite: 8] and **7.40%** for landline-only customers[cite: 8].
* Fiber optic subscribers comprise **69.4% of total churns** (1,297 customers)[cite: 5, 8] while paying the highest tier bills at **$91.50/mo** on average[cite: 8].

### 4. Technical Support as a Retention Anchor
* Customers without Tech Support churn at **41.64%**, compared to **15.17%** for those with active tech support[cite: 9].
* **82.3% of churned internet users** had no tech support active on their account[cite: 8, 9].

---

## 🎯 The High-Risk Segment Persona

Isolating accounts that combine the primary risk indicators:
* **Criteria:** `Contract = 'Month-to-month'` + `Internet = 'Fiber optic'` + `Tech Support = 'No'` + `Tenure = '0-1 Year'`[cite: 10]
* **Cohort Size:** 833 customers (11.8% of total base)[cite: 5, 10]
* **Cohort Churn Rate:** **71.07%** (592 churned accounts)[cite: 10]
* **Financial Impact:** **$48,489.95/month** ($581,879/year) in lost recurring revenue[cite: 10]

---

## 💡 Strategic Recommendations

1. **Complimentary Onboarding Tech Support:** Bundle free tech support for the first 90–180 days on all new Fiber Optic installations to eliminate unassisted early technical friction[cite: 9, 10].
2. **First-Year Contract Conversion Campaigns:** Target month-to-month Fiber customers between months 2 and 6 with discounted 1-year contract lock-ins[cite: 6, 7, 10].
3. **Proactive Health Checks:** Implement proactive outreach and usage checks during the first 60 days of onboarding, where attrition risk is most acute[cite: 6].

---

## 📂 Project Structure

```text
├── sql/
│   ├── 01_schema.sql      # Database initialization & raw data ingestion
│   ├── 02_cleaning.sql    # Data hygiene, casting, handling blanks, tenure cohorts
│   └── 03_analysis.sql    # Business KPIs, cohort breakdown, high-risk persona
├── data/
│   └── raw/               # Raw dataset (excluded via .gitignore)
└── README.md              # Project documentation and executive insights