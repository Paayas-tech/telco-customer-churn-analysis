-- ============================================================================
-- 04_advanced_analytics.sql
-- Project: Telco Customer Churn & Revenue Exposure Analysis
-- Techniques: Window Functions (NTILE, SUM OVER, RANK), Statistical Aggregations
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. REVENUE DECILE SEGMENTATION (NTILE)
-- Question: Is churn concentrated among low spenders or high-value accounts?
-- ----------------------------------------------------------------------------
WITH customer_deciles AS (
    SELECT 
        customer_id,
        monthly_charges,
        churn,
        NTILE(10) OVER (ORDER BY monthly_charges ASC) AS revenue_decile
    FROM cleaned_customer_churn
)
SELECT 
    revenue_decile,
    ROUND(MIN(monthly_charges)::numeric, 2) AS min_monthly_fee,
    ROUND(MAX(monthly_charges)::numeric, 2) AS max_monthly_fee,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        COUNT(*) FILTER (WHERE churn = 'Yes') * 100.0 / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'Yes')::numeric, 2) AS lost_mrr
FROM customer_deciles
GROUP BY revenue_decile
ORDER BY revenue_decile ASC;


-- ----------------------------------------------------------------------------
-- 2. CUMULATIVE REVENUE LOSS (RUNNING TOTALS VIA WINDOW FUNCTIONS)
-- Question: What percentage of total lost MRR is accounted for by the highest-paying churners?
-- ----------------------------------------------------------------------------
WITH churned_accounts AS (
    SELECT 
        customer_id,
        contract,
        internet_service,
        monthly_charges,
        SUM(monthly_charges) OVER () AS total_churn_mrr,
        SUM(monthly_charges) OVER (ORDER BY monthly_charges DESC) AS cumulative_lost_mrr,
        ROW_NUMBER() OVER (ORDER BY monthly_charges DESC) AS rank_by_loss
    FROM cleaned_customer_churn
    WHERE churn = 'Yes'
)
SELECT 
    rank_by_loss,
    customer_id,
    contract,
    internet_service,
    monthly_charges,
    ROUND(cumulative_lost_mrr::numeric, 2) AS cumulative_lost_mrr,
    ROUND((cumulative_lost_mrr * 100.0 / total_churn_mrr)::numeric, 2) AS cumulative_pct_of_lost_mrr
FROM churned_accounts
WHERE rank_by_loss IN (100, 250, 500, 1000, 1500, 1869)
ORDER BY rank_by_loss;


-- ----------------------------------------------------------------------------
-- 3. STATISTICAL DISTRIBUTION METRICS (IQR, MEAN, STDDEV, MEDIAN)
-- Question: Compare the revenue distribution profiles between retained and churned cohorts.
-- ----------------------------------------------------------------------------
SELECT 
    churn,
    COUNT(*) AS customer_count,
    ROUND(AVG(monthly_charges)::numeric, 2) AS mean_monthly_charges,
    ROUND(STDDEV(monthly_charges)::numeric, 2) AS stddev_monthly_charges,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY monthly_charges)::numeric, 2) AS q1_25th_percentile,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY monthly_charges)::numeric, 2) AS median_50th_percentile,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monthly_charges)::numeric, 2) AS q3_75th_percentile,
    ROUND(
        (PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monthly_charges) - 
         PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY monthly_charges))::numeric, 
        2
    ) AS interquartile_range_iqr
FROM cleaned_customer_churn
GROUP BY churn;