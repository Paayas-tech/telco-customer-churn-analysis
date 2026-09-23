CREATE OR REPLACE FUNCTION fn_get_customer_churn_risk(p_customer_id VARCHAR)
RETURNS TABLE (
    out_customer_id VARCHAR,
    calculated_risk_score INT,
    risk_tier VARCHAR,
    monthly_revenue NUMERIC,
    primary_risk_driver TEXT
) 
LANGUAGE plpgsql
AS $$
DECLARE
    v_record RECORD;
    v_score INT := 0;
    v_driver TEXT := 'Low inherent risk';
BEGIN
    SELECT * INTO v_record 
    FROM cleaned_customer_churn t 
    WHERE t.customer_id = p_customer_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Customer ID % not found', p_customer_id;
    END IF;

    -- Factor 1: Contract Structure (Max 40 pts)
    IF v_record.contract = 'Month-to-month' THEN
        v_score := v_score + 40;
        v_driver := 'Month-to-month contract flexibility';
    ELSIF v_record.contract = 'One year' THEN
        v_score := v_score + 10;
    END IF;

    -- Factor 2: Internet Service & Support Friction (Max 30 pts)
    IF v_record.internet_service = 'Fiber optic' AND v_record.tech_support = 'No' THEN
        v_score := v_score + 30;
        v_driver := 'Fiber optic service without technical support';
    ELSIF v_record.internet_service = 'Fiber optic' THEN
        v_score := v_score + 15;
    END IF;

    -- Factor 3: Tenure Risk (Max 20 pts)
    IF v_record.tenure <= 12 THEN
        v_score := v_score + 20;
    ELSIF v_record.tenure <= 24 THEN
        v_score := v_score + 10;
    END IF;

    -- Factor 4: Payment Friction (Max 10 pts)
    IF v_record.payment_method = 'Electronic check' THEN
        v_score := v_score + 10;
    END IF;

    RETURN QUERY
    SELECT 
        v_record.customer_id,
        v_score,
        CASE 
            WHEN v_score >= 70 THEN 'CRITICAL / HIGH RISK'
            WHEN v_score >= 40 THEN 'MODERATE RISK'
            ELSE 'HEALTHY / LOW RISK'
        END::VARCHAR,
        ROUND(v_record.monthly_charges::numeric, 2),
        v_driver;
END;
$$;