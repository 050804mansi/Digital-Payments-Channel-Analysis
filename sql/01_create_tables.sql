-- SQLite-compatible schema for the RBI annual payment-system data.


CREATE TABLE IF NOT EXISTS annual_payment_modes (
    Financial_Year TEXT NOT NULL,
    Payment_Mode TEXT NOT NULL,
    Mode_Group TEXT NOT NULL,
    Transaction_Volume_Lakh REAL NOT NULL,
    Transaction_Value_Lakh_Crore REAL NOT NULL,
    Estimated_Average_Ticket_INR REAL,
    YoY_Volume_Growth_Pct REAL,
    YoY_Value_Growth_Pct REAL,
    PRIMARY KEY (Financial_Year, Payment_Mode)
);

CREATE TABLE IF NOT EXISTS annual_payment_totals (
    Financial_Year TEXT PRIMARY KEY,
    Total_Retail_Volume_Lakh REAL NOT NULL,
    Total_Retail_Value_Lakh_Crore REAL NOT NULL,
    Total_Digital_Volume_Lakh REAL NOT NULL,
    Total_Digital_Value_Lakh_Crore REAL NOT NULL,
    UPI_Volume_Lakh REAL,
    UPI_Share_Of_Retail_Volume_Pct REAL
);
