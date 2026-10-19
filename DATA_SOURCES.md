# Data Sources and Definitions

## Primary source

Reserve Bank of India, Chapter IX, “Payment and Settlement Systems and Information Technology,” Table IX.1, “Payment System Indicators - Annual Turnover (April-March),” in:

- Annual Report 2023-24 (FY 2021-22 and FY 2022-23 figures): https://www.rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1409
- Annual Report 2025-26 (FY 2023-24 to FY 2025-26 figures): https://rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1469

The two CSV files in `Data/` contain selected rows transcribed from Table IX.1 for FY 2021-22 through FY 2025-26. FY 2023-24 appears in both reports; the 2025-26 report's figure is retained for that year. The data cover RTGS, UPI, NEFT, IMPS, credit cards, debit cards, prepaid payment instruments, and RBI's aggregate retail/digital payment totals.

## Units and definitions

- Transaction volume is reported in lakh transactions.
- Transaction value is reported in ₹ lakh crore.
- Estimated average transaction size is calculated as `value_lakh_crore / volume_lakh * 10,000,000` rupees.
- UPI share of retail volume is calculated as UPI volume divided by RBI's total retail payment volume. It is a share of the reported total, not a sum across selected rows.
- RBI's total digital aggregate includes RTGS and excludes paper-based instruments; total retail excludes RTGS and includes paper-based instruments. These aggregates are not nested, so this project does not calculate a digital-to-retail share.
- RTGS is a large-value payment system; it is displayed separately from retail payment channels in interpretations.
- “Credit_Cards” and “Debit_Cards” are RBI's card subcategories. The aggregate “Card Payments” row is intentionally not included in the channel CSV so card totals are not double-counted in mode-level charts.
- RBI reports rounded values. Small differences between component rows and totals can occur because of rounding and because only selected modes are included.

## Limitations and attribution

The dataset is a five-financial-year annual snapshot, not a monthly series. It does not contain individual users, merchants, banks, or transaction records. It supports descriptive comparisons only; it cannot identify causes or predict future volumes.

Attribution: Reserve Bank of India, Annual Reports 2023-24 and 2025-26, Chapter IX, Table IX.1. The project does not represent the RBI source as being under a particular open-data license. Check the publisher's applicable terms before reusing source material.
