-- ==========================================================
-- 01_SCHEMA.SQL: Database Setup & Raw Table Staging
-- Project: Telco Customer Churn Analysis
-- ==========================================================

-- Drop table if it exists to allow clean re-runs
DROP TABLE IF EXISTS raw_customer_churn;

-- Create staging table
-- total_charges is stored as VARCHAR because new accounts (tenure = 0)
-- contain empty spaces (" ") in the raw CSV.
CREATE TABLE raw_customer_churn (
    customer_id VARCHAR(50) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen INT,
    partner VARCHAR(5),
    dependents VARCHAR(5),
    tenure INT,
    phone_service VARCHAR(5),
    multiple_lines VARCHAR(25),
    internet_service VARCHAR(25),
    online_security VARCHAR(25),
    online_backup VARCHAR(25),
    device_protection VARCHAR(25),
    tech_support VARCHAR(25),
    streaming_tv VARCHAR(25),
    streaming_movies VARCHAR(25),
    contract VARCHAR(25),
    paperless_billing VARCHAR(5),
    payment_method VARCHAR(50),
    monthly_charges NUMERIC(10, 2),
    total_charges VARCHAR(50),
    churn VARCHAR(5)
);

-- Copy command to import the CSV file
COPY raw_customer_churn
FROM 'D:/github/telco-customer-churn-analysis/data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Validation: Verify total count matches 7,043 rows
SELECT COUNT(*) AS total_records_imported FROM raw_customer_churn;