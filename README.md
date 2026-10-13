# Telco Customer Churn & Revenue Exposure Analysis

An end-to-end data analytics project diagnosing customer churn dynamics, quantifying recurring revenue leakage, and deploying automated risk-scoring logic using **PostgreSQL**, a **Python machine-learning pipeline**, and a live **Google Sheets dashboard**.

---

## 📌 Executive Summary

* **Customer vs. Revenue Disconnect:** The business has an overall customer churn rate of **26.54%** (1,869 / 7,043 customers), while **30.50% of snapshot Monthly Recurring Revenue (MRR)** is associated with churned accounts ($139,130.85 out of $456,116.60). This is a snapshot revenue share, not an annual churn rate.
* **Annualized Revenue Leakage:** Multiplying churned accounts' monthly charges by 12 gives approximately **$1.67M annualized** ($1,669,570.20). This extrapolation is not a measured annual loss or a forecast. Departing customers represent higher-paying accounts ($74.44/mo average churned vs. $61.26/mo retained).
* **Concentration of Risk:** Customers paying at least $70/month have **35.48% churn** (1,274 / 3,591); the lowest spending decile has **8.37% churn**. The 38.07% rate belongs to Decile 6, not the entire $70+ segment. The top 500 departing accounts alone drive **$50,400.10/month** (36.2% of all lost MRR).

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

### Retrospective SQL Heuristic Results
Evaluating the scoring function against actual customer outcomes across all 7,043 accounts:

| Risk Tier | Total Accounts | Churned Count | Actual Churn Rate | Lost MRR |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL / HIGH RISK** | 2,243 | 1,258 | **56.09%** | **$101,392.20 / mo** |
| **MODERATE RISK** | 2,000 | 463 | **23.15%** | **$25,817.10 / mo** |
| **HEALTHY / LOW RISK** | 2,800 | 148 | **5.29%** | **$11,921.55 / mo** |

*The heuristic identifies **72.9% of all lost MRR** within the High Risk tier, providing an operational filter for proactive retention workflows.*

---

## Python Baseline ML Pipeline

`python/train_baseline.py` fits a **Logistic Regression** pipeline with **StandardScaler** for tenure, monthly charges, and total charges, plus **OneHotEncoder(handle_unknown="ignore")** for categorical features. Customer ID and the redundant tenure cohort are excluded from features. Schema, unique IDs, and churn labels are validated before modeling.

Validation uses a **stratified 80/20 train/test split (random_state=42)**: 5,634 training accounts and 1,409 test accounts, including 374 test churners. Preprocessing and the classifier are fitted strictly on training rows. The dummy classifier and retrospective SQL heuristic are evaluated on the exact same test fold.

| Model / cutoff | ROC-AUC | Average Precision (PR-AUC summary) | Precision | Recall |
| :--- | ---: | ---: | ---: | ---: |
| Dummy (most frequent) | 0.5000 | 0.2654 | 0.0000 | 0.0000 |
| SQL heuristic (score >=70) | 0.8238 | 0.5722 | 0.5479 | 0.6578 |
| Logistic Regression (0.50) | 0.8420 | 0.6337 | 0.6572 | 0.5588 |
| Logistic Regression (0.40) | 0.8420 | 0.6337 | 0.5682 | 0.6684 |
| Logistic Regression (0.35) | 0.8420 | 0.6337 | 0.5432 | 0.7059 |

**Chosen business cutoff: 0.35**, prioritizing churn capture. It captures **70.59% recall (264 / 374 test churners)**, with 222 false positives. This was a preset threshold comparison; it has not been optimized on a separate validation set or validated against retention costs. Test results describe the observed tradeoff, not proof of an optimal cutoff.

### Coefficients and persistence

The script matches coefficients to the fitted transformed feature names and prints the top five positive and negative weights. Examples include **Fiber optic (+0.65)**, **Month-to-month (+0.59)**, and **Tenure (-1.26)**. These are conditional model weights on the log-odds scale, not causal effects. Numeric coefficients represent one training-set standard deviation; categorical coefficients represent indicators.

**Multicollinearity:** Total Charges, Monthly Charges, and Tenure are related because accumulated charges depend on billing amount and customer duration. Their coefficients can redistribute shared information and have counterintuitive signs. Full one-hot encoding and correlated service features further limit direct comparisons; individual weights should not be interpreted as standalone business effects.

The complete training-fitted preprocessor and classifier are saved to `models/baseline_logistic_pipeline.joblib`. Reload verification confirms identical probabilities on all test rows. The binary is ignored by Git and must be regenerated locally; only load trusted model artifacts.

### Batch scoring and revenue exposure

`python/predict.py` loads the saved pipeline without refitting, scores **7,043 accounts**, and flags **2,357 accounts** at probability >=0.35. Their monthly charges total **$183,535.15 in monthly revenue exposure**. Average churn probability is **26.59%**.

The ignored audit export `data/predictions/customer_churn_scored.csv` contains `customer_id`, `tenure`, `contract`, `monthly_charges`, `churn_probability`, `predicted_churn_flag`, and `monthly_revenue_at_risk`. Revenue at risk equals monthly charges for flagged accounts and zero otherwise; it is not probability-weighted expected loss. Flag 0 means below the cutoff, not guaranteed safe.

This is retrospective scoring of the full snapshot, including training rows and historical churners. It is not a fresh holdout evaluation, a live retention list, or a forecast with a defined future horizon.

### Reproduce locally (Windows PowerShell)

Run from the repository root with `data/processed/cleaned_telco_churn.csv` available:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r python/requirements.txt
.\.venv\Scripts\python.exe python/train_baseline.py
.\.venv\Scripts\python.exe python/predict.py
```

The five direct dependencies are pandas, numpy, scikit-learn, joblib, and matplotlib; their versions are pinned in `python/requirements.txt`.

---

## 💡 Strategic Recommendations

1. **Prioritize Top 500 High-Value Accounts:** Focus high-touch support and dedicated account managers on accounts paying $> \$90/\text{mo}$ to secure 36% of exposed MRR.
2. **First-Year Fiber Optic Support Bundling:** Automatically bundle 90 days of complimentary technical support with month-to-month fiber subscriptions to mitigate early lifecycle attrition.
3. **Contract Migration Incentives:** Provide targeted discounts ($5–$10/mo) for moving month-to-month accounts to annual contracts.

---

## 🛠 Tech Stack & Tools

* **Database Engine:** PostgreSQL 17 (pgAdmin 4)
* **SQL Capabilities:** Window Functions (`NTILE`, `SUM OVER`, `ROW_NUMBER`), Statistical Aggregations (`PERCENTILE_CONT`, `STDDEV`), PL/pgSQL Stored Functions
* **Visualization & Reporting:** Google Sheets (Pivot Tables, Calculated Fields, Executive Dashboard)
* **Machine Learning:** Python, pandas, numpy, scikit-learn, joblib, matplotlib
* **Version Control:** Git & GitHub

---

## 📁 Project Structure

```text
telco-customer-churn-analysis/
├── README.md
├── .gitignore
├── dashboards/
│   └── dashboard_preview.png
├── data/
│   ├── raw/                      # optional source CSV; ignored, not bundled
│   ├── processed/
│   │   └── cleaned_telco_churn.csv
│   └── predictions/
│       └── customer_churn_scored.csv  # generated locally; ignored
├── models/
│   └── baseline_logistic_pipeline.joblib  # generated locally; ignored
├── python/
│   ├── requirements.txt
│   ├── train_baseline.py
│   └── predict.py
└── sql/
    ├── 01_schema.sql
    ├── 02_cleaning.sql
    ├── 03_analysis.sql
    ├── 04_advanced_analytics.sql
    └── 05_views_and_procedures.sql
```

The interactive dashboard is hosted directly on [Google Sheets](https://docs.google.com/spreadsheets/d/1txWOi8K12LKhqEunyHWKLgKyrPt0hz5dq3MdSzjqRlI/edit?usp=sharing); the repository includes its PNG preview.
