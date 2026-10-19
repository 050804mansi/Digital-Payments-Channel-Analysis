-- Run after loading the two CSV files into the tables in 01_create_tables.sql.

-- 1. Year-on-year transaction volume growth by payment mode.

WITH mode_growth AS (
    SELECT
        Financial_Year,
        Payment_Mode,
        Transaction_Volume_Lakh,
        LAG(Transaction_Volume_Lakh) OVER (
            PARTITION BY Payment_Mode ORDER BY Financial_Year
        ) AS Previous_Year_Volume_Lakh
    FROM annual_payment_modes
)
SELECT
    Financial_Year,
    Payment_Mode,
    Transaction_Volume_Lakh,
    ROUND(100.0 * (Transaction_Volume_Lakh / Previous_Year_Volume_Lakh - 1), 2)
        AS YoY_Volume_Growth_Pct
FROM mode_growth
ORDER BY Payment_Mode, Financial_Year;

-- 2. UPI volume as a share of all retail payment transactions.

SELECT
    t.Financial_Year,
    u.Transaction_Volume_Lakh AS UPI_Volume_Lakh,
    t.Total_Retail_Volume_Lakh,
    ROUND(100.0 * u.Transaction_Volume_Lakh / t.Total_Retail_Volume_Lakh, 2)
        AS UPI_Share_Of_Retail_Volume_Pct
FROM annual_payment_totals AS t
JOIN annual_payment_modes AS u
  ON u.Financial_Year = t.Financial_Year
 AND u.Payment_Mode = 'UPI'
ORDER BY t.Financial_Year;

-- 3. Estimated average transaction size (₹) by mode.
-- Value is ₹ lakh crore and volume is lakh transactions, so multiply the ratio by 10^7.

SELECT
    Financial_Year,
    Payment_Mode,
    ROUND(Transaction_Value_Lakh_Crore / Transaction_Volume_Lakh * 10000000, 2)
        AS Estimated_Average_Ticket_INR
FROM annual_payment_modes
WHERE Transaction_Volume_Lakh > 0
ORDER BY Payment_Mode, Financial_Year;

-- 4. RBI aggregate digital and retail totals are reported separately.
-- Digital includes RTGS and excludes paper; retail excludes RTGS and includes paper.
-- Do not divide one aggregate by the other and label it a share.

SELECT
    Financial_Year,
    Total_Retail_Volume_Lakh,
    Total_Digital_Volume_Lakh
FROM annual_payment_totals
ORDER BY Financial_Year;
