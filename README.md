# India Digital Payments: Payment-Channel Mix & Growth

**Author: Mansi Saxena**

## Contact

- LinkedIn: [Mansi Saxena](https://www.linkedin.com/in/mansi-saxena-049102362)
- GitHub: [050804mansi](https://github.com/050804mansi)
- Email: [mansi53245@gmail.com](mailto:mansi53245@gmail.com)

An original data analytics project using aggregate annual payment-system statistics published by the Reserve Bank of India (RBI). It compares UPI, NEFT, IMPS, RTGS, credit and debit cards, and prepaid payment instruments across FY 2021-22 to FY 2025-26.

## Purpose

The project turns official annual tables into comparable indicators, SQL summaries, charts, a dashboard and a short report. It explores how payment modes differ in volume and value, how UPI's share changed, and how estimated transaction sizes compare across modes. The data are aggregated; there are no user or merchant records.

## Data source and project distinction

The dataset was transcribed from RBI Annual Reports 2023-24 and 2025-26, Chapter IX, Table IX.1. It is a different dataset from the Kaggle monthly UPI-only data in the reference ZIP: this project uses RBI annual system-level indicators across multiple payment channels. No files or code from the reference ZIP are included. See [DATA_SOURCES.md](DATA_SOURCES.md) for source, units, calculations and limitations.

## Questions explored

1. How did transaction volumes and values change across selected payment modes?
2. How does the relative volume growth of UPI, NEFT, IMPS, cards and prepaid instruments compare?
3. What share of RBI-reported retail transaction volume came from UPI and digital payments?
4. How did estimated average transaction size differ by payment mode?
5. How did aggregate retail and digital transaction volumes change over the five financial years?

## Project files

- `Data/annual_payment_mode_statistics.csv`: selected mode-level annual statistics.
- `Data/annual_payment_system_totals.csv`: RBI aggregate retail and digital totals.
- `analysis.py`: data preparation, derived metrics, SQLite load, charts, dashboard and PDF report.
- `sql/`: SQLite-compatible schema and example analysis queries.
- `notebooks/01_data_prep_sql.ipynb`: load, inspect and query the tables.
- `notebooks/02_channel_analysis.ipynb`: charts and descriptive analysis.
- `dashboard/payment_channel_dashboard.png` and `.html`: one-page shareable dashboard.
- `Docs/India_Digital_Payments_Channel_Analytics_Report.pdf`: eight-page report with all six analysis charts.
- `DATA_SOURCES.md`: citations, units, calculations and caveats.
- `COPYRIGHT.txt`: authorship and reuse notice.

## Run

Python 3.12 is recommended. From this project folder, install packages and generate all outputs:

```powershell
python -m pip install -r requirements.txt
python analysis.py
```

The script creates six charts in `images/`, a dashboard in `dashboard/`, an eight-page PDF in `Docs/`, and a local SQLite database in `Data/`.

To explore the notebooks, run:

```powershell
python -m jupyter notebook
```

Then open the `notebooks/` folder in the browser and run cells from top to bottom.

## Tools and technology

- Python 3.12
- pandas and NumPy for data handling and calculations
- Matplotlib and Seaborn for charts, dashboard layout and PDF pages
- SQLite (`sqlite3`, included with Python) for the local relational database
- SQL window functions for year-on-year comparisons
- Jupyter Notebook and `nbformat` for interactive analysis
- CSV for the source tables

No database server, credentials, external API or user-level data are needed.

## Method and limitations

Figures are annual aggregates for five financial years. Volume is reported in lakh transactions and value in ₹ lakh crore. Average transaction size is estimated from these rounded figures. RTGS is a large-value system, so it is kept distinct in the interpretation. RBI's total digital and total retail aggregates use different components; the project does not divide one by the other as if they were nested. The analysis is descriptive and does not establish causes or forecast future activity.

## Selected findings

- UPI volume increased 425.8% from FY 2021-22 to FY 2025-26; its share of RBI-reported retail transaction volume rose from 63.4% to 85.7%.
- Total digital payment volume increased 291.4% across the five-year window, reaching about 281.7 billion transactions in FY 2025-26.
- The five-year view compares growth across UPI, NEFT, IMPS, cards and prepaid instruments, rather than UPI alone.

## Original work and reuse

The original code, SQL query design, notebooks, narrative, report and visual design are © 2026 Mansi Saxena, All Rights Reserved. RBI figures are separately attributed; no exclusive ownership of source statistics is claimed. See [COPYRIGHT.txt](COPYRIGHT.txt) and [DATA_SOURCES.md](DATA_SOURCES.md).

A copyright notice records authorship and reuse terms, but cannot technically prevent copying from a public repository. Keep the repository private if access itself must be restricted.

This independent project is not endorsed by the Reserve Bank of India or the Government of India.
