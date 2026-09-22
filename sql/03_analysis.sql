-- ==========================================================
-- 03_ANALYSIS.SQL: Core Business Metrics & Segmentation
-- Project: Telco Customer Churn Analysis
-- ==========================================================

-- ----------------------------------------------------------
-- 1. Executive Summary: High-Level Churn & Revenue Exposure
-- Business Question: What is our baseline churn rate, and how 
-- much Monthly Recurring Revenue (MRR) are we losing to churn?
-- ----------------------------------------------------------
SELECT 
    COUNT(*) AS total_customers,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue,
    ROUND(
        SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 
        2
    ) AS churned_monthly_revenue,
    ROUND(
        SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) * 100.0 / SUM(monthly_charges),
        2
    ) AS revenue_loss_pct
FROM cleaned_customer_churn;


-- ----------------------------------------------------------
-- 2. Cohort Analysis: Churn by Tenure Group
-- Business Question: When are customers leaving? (First year vs long term)
-- ----------------------------------------------------------
SELECT 
    tenure_group,
    COUNT(*) AS total_customers,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM cleaned_customer_churn
GROUP BY tenure_group
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------
-- 3. Contract Type Risk Analysis
-- Business Question: Does contract commitment reduce churn?
-- ----------------------------------------------------------
SELECT 
    contract,
    COUNT(*) AS total_customers,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_mrr
FROM cleaned_customer_churn
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- ----------------------------------------------------------
-- 4. Internet Service Type Breakdown
-- Business Question: Are specific infrastructure tiers churn risks?
-- ----------------------------------------------------------
SELECT 
    internet_service,
    COUNT(*) AS total_customers,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_bill
FROM cleaned_customer_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------
-- 5. Support & Security Add-Ons Impact
-- Business Question: Do tech support and online security retain users?
-- ----------------------------------------------------------
SELECT 
    tech_support,
    COUNT(*) AS total_customers,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct
FROM cleaned_customer_churn
WHERE internet_service != 'No'
GROUP BY tech_support
ORDER BY churn_rate_pct DESC;

-- ----------------------------------------------------------
-- 6. The High-Risk Segment Persona
-- Business Question: What happens when month-to-month, fiber optic, 
-- and no tech support overlap in the first year?
-- ----------------------------------------------------------
SELECT 
    COUNT(*) AS total_high_risk_cohort,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_high_risk,
    ROUND(
        COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS cohort_churn_rate_pct,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS mrr_lost_from_this_cohort
FROM cleaned_customer_churn
WHERE contract = 'Month-to-month'
  AND internet_service = 'Fiber optic'
  AND tech_support = 'No'
  AND tenure_group = '0-1 Year';