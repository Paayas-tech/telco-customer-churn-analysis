# Power BI model and report setup

Status: baseline and Month-to-month report exports are now available: [overall PDF](dashboard_overall.pdf), [Month-to-month PDF](dashboard_month_to_month.pdf), [overall PNG](../images/dashboard_overview.png), and [Month-to-month PNG](../images/dashboard_sliced_risk.png). Both PNGs are first-page renders at 200 DPI. The exports show report cards, slicers, a contract churn chart, risk distribution, and a formatted action table.

The overall export shows 7,043 accounts, 26.54% churn, $456.12K MRR, and $183.54K exposure. The Month-to-month export shows 3,875 accounts, 42.71% churn, $257.29K MRR, and $179.76K exposure. The latter is a contract slice, not a high-risk-only slice. The guide below documents setup/reproduction; a PBIX and live interactions have not been inspected, and the authored DAX still needs validation against the actual semantic model.

## Prepare and join the inputs

1. Run the documented training/scoring commands in the repository README.
2. In Power BI Desktop, import `data/processed/cleaned_telco_churn.csv` and `data/predictions/customer_churn_scored.csv` as Power Query staging queries.
3. Type both `customer_id` columns as text; reject blanks and duplicates. Each source should contain 7,043 unique IDs for this snapshot. Confirm the IDs match in both directions.
4. Left-outer merge cleaned data with scored data on `customer_id`. Expand ONLY `churn_probability`, `predicted_churn_flag`, and `monthly_revenue_at_risk`. Use cleaned data's tenure, contract, and monthly charges. Name the resulting table `Customers`; disable staging-query loads to avoid duplicate tables and totals.
5. Confirm the join preserves 7,043 rows and produces no null scoring fields. Do not silently convert missing scores to zero/safe.
6. Use whole numbers for tenure and risk flag; decimal numbers for probability; fixed decimal/currency for charges and exposure. Keep `churn` as Yes/No text and categorical columns as text.
7. Add each definition in `dax/measures.dax` separately using New measure. A multi-definition source file is not a paste-and-run DAX query. Format counts, percentages, and currency as described in README.

The historical target comes from the cleaned CSV. Do not derive observed churn from `predicted_churn_flag`. Exposed MRR sums the export's flagged revenue at cutoff 0.35; it is not expected loss and does not dynamically change its cutoff.

## Build the page

- Cards: Total Customers, Churn Rate, Total MRR, Exposed MRR.
- Slicers: contract and internet_service; optionally predicted_churn_flag and tenure.
- Contract chart: Churn Rate by contract. Internet chart: Churn Rate by internet_service.
- Action table: customer_id (masked for public sharing), tenure, contract, monthly_charges, churn_probability, predicted_churn_flag, monthly_revenue_at_risk, churn.
- Sort the action table by probability descending, then monthly charges descending. Apply probability data bars/color scale and currency formats to the table cells.
- Use Edit interactions so both categorical slicers filter all relevant charts, cards, and the table. Reset slicers before baseline validation.

Proposed retention queue: high-risk flag 1, historical churn No, tenure <3, charges >=80 and <=95. Treat this as a targeting hypothesis; historical retention is not evidence that an account is currently active. Real outreach requires current eligibility and consent/process checks appropriate to the business.

## Validate and capture

Baseline: 7,043 customers; 1,869 historical churners; churn 26.54%; total MRR $456,116.60; exposure $183,535.15; high-risk flags 2,357.

With only a contract filter: Month-to-month churn 42.71%; One year 11.27%; Two year 2.83%. With combined filters, compare to the same filtered source cohort rather than these baseline values. Because measures respect filter context, selecting a churn label changes the denominator cohort too.

Check conditional formats, probability sort, slicer clearing, row uniqueness, and no missing scores. The supplied PDF exports and their PNG renders are complete. Save the editable report as `pbix/Telco_Revenue_Risk_Dashboard.pbix` when available. For future exports, retain the canonical `images/dashboard_overview.png` and `images/dashboard_sliced_risk.png` paths; see `images/README.md`.

To reopen an existing PBIX, update source paths in Power Query and refresh before comparing totals. Review embedded data before sharing; report screenshots should mask identifiers.

DAX reference: [Microsoft CALCULATE documentation](https://learn.microsoft.com/dax/calculate-function-dax).
