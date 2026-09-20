-- ==========================================================
-- 02_CLEANING.SQL: Data Hygiene & Type Transformations
-- Project: Telco Customer Churn Analysis
-- ==========================================================

-- 1. Check for duplicates (Verification)
SELECT 
    customer_id, 
    COUNT(*) 
FROM raw_customer_churn
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 2. Inspect the blank spaces in total_charges
-- In the raw file, customers with tenure = 0 have total_charges = ' '
SELECT 
    customer_id, 
    tenure, 
    monthly_charges, 
    total_charges 
FROM raw_customer_churn
WHERE total_charges = ' ' OR total_charges IS NULL;

-- 3. Create Cleaned Production Table
-- We convert total_charges to NUMERIC and cast Boolean/flag columns cleanly
DROP TABLE IF EXISTS cleaned_customer_churn;

CREATE TABLE cleaned_customer_churn AS
SELECT
    customer_id,
    gender,
    senior_citizen,
    partner,
    dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    -- Handle blank values by converting ' ' to 0.00 for brand-new customers
    CASE 
        WHEN total_charges = ' ' THEN 0.00
        ELSE CAST(total_charges AS NUMERIC(10, 2))
    END AS total_charges,
    churn,
    -- Feature Engineering: Create useful tenure cohorts for analysis later
    CASE 
        WHEN tenure <= 12 THEN '0-1 Year'
        WHEN tenure <= 24 THEN '1-2 Years'
        WHEN tenure <= 48 THEN '2-4 Years'
        ELSE '4+ Years'
    END AS tenure_group
FROM raw_customer_churn;

-- 4. Verify the cleaned table and check data types
SELECT 
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN total_charges = 0 THEN 1 END) AS zero_charge_new_customers
FROM cleaned_customer_churn;