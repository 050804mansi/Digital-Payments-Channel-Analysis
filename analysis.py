from pathlib import Path
import sqlite3
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Data"
IMAGES = ROOT / "images"
DASHBOARD = ROOT / "dashboard"
REPORT = ROOT / "Docs" / "India_Digital_Payments_Channel_Analytics_Report.pdf"
AUTHOR = "Mansi Saxena"
SOURCE_URL = "https://rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1469"
SOURCE_URL_EARLY = "https://www.rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1409"
NAVY, TEAL, GOLD, MUTED = "#14283f", "#168b8b", "#e5a23b", "#687b8e"
PALETTE = [NAVY, TEAL, GOLD, "#c66752", "#708ca4", "#9473a6", "#81a67c"]
MODES = ["UPI", "NEFT", "IMPS", "Credit_Cards", "Debit_Cards", "Prepaid_Instruments"]
MODE_LABELS = {
    "UPI": "UPI",
    "NEFT": "NEFT",
    "IMPS": "IMPS",
    "Credit_Cards": "Credit cards",
    "Debit_Cards": "Debit cards",
    "Prepaid_Instruments": "Prepaid instruments",
    "RTGS": "RTGS",
}

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#d7dee5",
    "axes.labelcolor": NAVY,
    "axes.titlecolor": NAVY,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def load_data():
    modes = pd.read_csv(DATA / "annual_payment_mode_statistics.csv")
    totals = pd.read_csv(DATA / "annual_payment_system_totals.csv")
    modes = modes.sort_values(["Payment_Mode", "Financial_Year"]).reset_index(drop=True)
    totals = totals.sort_values("Financial_Year").reset_index(drop=True)
    modes["Estimated_Average_Ticket_INR"] = (
        modes["Transaction_Value_Lakh_Crore"]
        / modes["Transaction_Volume_Lakh"]
        * 10_000_000
    )
    modes["YoY_Volume_Growth_Pct"] = (
        modes.groupby("Payment_Mode")["Transaction_Volume_Lakh"].pct_change() * 100
    )
    modes["YoY_Value_Growth_Pct"] = (
        modes.groupby("Payment_Mode")["Transaction_Value_Lakh_Crore"].pct_change() * 100
    )
    upi = modes.loc[modes["Payment_Mode"].eq("UPI"), ["Financial_Year", "Transaction_Volume_Lakh"]]
    totals = totals.merge(upi, on="Financial_Year", validate="one_to_one")
    totals = totals.rename(columns={"Transaction_Volume_Lakh": "UPI_Volume_Lakh"})
    totals["UPI_Share_Of_Retail_Volume_Pct"] = (
        totals["UPI_Volume_Lakh"] / totals["Total_Retail_Volume_Lakh"] * 100
    )
    return modes, totals


def store_sqlite(modes, totals):
    db_path = DATA / "annual_payment_analytics.sqlite"
    with sqlite3.connect(db_path) as connection:
        schema = (ROOT / "sql" / "01_create_tables.sql").read_text(encoding="utf-8")
        connection.execute("DROP TABLE IF EXISTS annual_payment_modes")
        connection.execute("DROP TABLE IF EXISTS annual_payment_totals")
        connection.executescript(schema)
        mode_columns = ["Financial_Year", "Payment_Mode", "Mode_Group", "Transaction_Volume_Lakh",
                        "Transaction_Value_Lakh_Crore", "Estimated_Average_Ticket_INR",
                        "YoY_Volume_Growth_Pct", "YoY_Value_Growth_Pct"]
        total_columns = ["Financial_Year", "Total_Retail_Volume_Lakh", "Total_Retail_Value_Lakh_Crore",
                         "Total_Digital_Volume_Lakh", "Total_Digital_Value_Lakh_Crore",
                         "UPI_Volume_Lakh", "UPI_Share_Of_Retail_Volume_Pct"]
        modes[mode_columns].to_sql("annual_payment_modes", connection, if_exists="append", index=False)
        totals[total_columns].to_sql("annual_payment_totals", connection, if_exists="append", index=False)
    return db_path


def summary(modes, totals):
    first, last = totals.iloc[0], totals.iloc[-1]
    digital_volume = np.asarray(totals["Total_Digital_Volume_Lakh"], dtype=float)
    upi_first = modes.query("Payment_Mode == 'UPI'").iloc[0]
    upi_last = modes.query("Payment_Mode == 'UPI'").iloc[-1]
    return {
        "upi_volume_growth_pct": (upi_last.Transaction_Volume_Lakh / upi_first.Transaction_Volume_Lakh - 1) * 100,
        "upi_retail_share_start_pct": first.UPI_Share_Of_Retail_Volume_Pct,
        "upi_retail_share_end_pct": last.UPI_Share_Of_Retail_Volume_Pct,
        "digital_volume_growth_pct": (digital_volume[-1] / digital_volume[0] - 1) * 100,
        "upi_value_fy_2025_26_lakh_crore": float(upi_last.Transaction_Value_Lakh_Crore),
        "imps_volume_growth_pct": (
            modes.query("Payment_Mode == 'IMPS'").iloc[-1].Transaction_Volume_Lakh
            / modes.query("Payment_Mode == 'IMPS'").iloc[0].Transaction_Volume_Lakh - 1
        ) * 100,
    }


def _save(fig, name):
    IMAGES.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMAGES / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _source_note(fig, text="Source: RBI Annual Reports 2023-24 and 2025-26, Table IX.1 | Prepared by Mansi Saxena"):
    fig.text(.01, .005, text, color=MUTED, fontsize=7.5)


def generate_charts(modes, totals):
    sns.set_theme(style="whitegrid", palette=PALETTE)
    retail = modes[modes["Payment_Mode"].isin(MODES)]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    for idx, mode in enumerate(MODES):
        part = retail[retail.Payment_Mode.eq(mode)]
        ax.plot(part.Financial_Year, part.Transaction_Volume_Lakh, marker="o", lw=2.4,
                color=PALETTE[idx], label=MODE_LABELS[mode])
    ax.set_yscale("log")
    ax.set(title="Annual retail payment mode volumes", ylabel="Transactions (lakh, log scale)", xlabel="Financial year")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", which="both", alpha=.22)
    _source_note(fig)
    _save(fig, "01_retail_mode_volume_log.png")

    fig, ax = plt.subplots(figsize=(11, 5.8))
    for idx, mode in enumerate(MODES):
        part = retail[retail.Payment_Mode.eq(mode)].copy()
        part["Volume_Index"] = part.Transaction_Volume_Lakh / part.Transaction_Volume_Lakh.iloc[0] * 100
        ax.plot(part.Financial_Year, part.Volume_Index, marker="o", lw=2.4,
                color=PALETTE[idx], label=MODE_LABELS[mode])
    ax.axhline(100, color=MUTED, lw=1, ls="--")
    ax.set(title="Relative transaction volume growth (FY 2021-22 = 100)", ylabel="Indexed volume", xlabel="Financial year")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", alpha=.22)
    _source_note(fig)
    _save(fig, "02_mode_volume_index.png")

    fig, ax = plt.subplots(figsize=(11, 5.8))
    value_modes = ["UPI", "NEFT", "IMPS", "Credit_Cards", "Debit_Cards", "Prepaid_Instruments"]
    for idx, mode in enumerate(value_modes):
        part = modes[modes.Payment_Mode.eq(mode)]
        ax.plot(part.Financial_Year, part.Transaction_Value_Lakh_Crore, marker="o", lw=2.4,
                color=PALETTE[idx], label=MODE_LABELS[mode])
    ax.set(title="Annual transaction value by selected retail mode", ylabel="₹ lakh crore", xlabel="Financial year")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", alpha=.22)
    _source_note(fig, "RTGS excluded from this retail-mode comparison; source: RBI Annual Reports 2023-24 and 2025-26, Table IX.1")
    _save(fig, "03_retail_mode_value.png")

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ticket_modes = ["RTGS", *MODES]
    for idx, mode in enumerate(ticket_modes):
        part = modes[modes.Payment_Mode.eq(mode)]
        ax.plot(part.Financial_Year, part.Estimated_Average_Ticket_INR, marker="o", lw=2.2,
                color=PALETTE[idx], label=MODE_LABELS[mode])
    ax.set_yscale("log")
    ax.set(title="Estimated average transaction size by mode", ylabel="₹ per transaction (log scale)", xlabel="Financial year")
    ax.legend(frameon=False, ncol=4)
    ax.grid(axis="y", which="both", alpha=.22)
    _source_note(fig, "Estimated from RBI rounded annual totals; RTGS is a large-value system")
    _save(fig, "04_average_ticket_size.png")

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(totals.Financial_Year, totals.UPI_Share_Of_Retail_Volume_Pct,
            marker="o", lw=2.7, color=TEAL)
    ax.set_ylim(0, 100)
    ax.set(title="UPI share of RBI-reported retail payment volume", ylabel="Share (%)", xlabel="Financial year")
    ax.grid(axis="y", alpha=.22)
    _source_note(fig)
    _save(fig, "05_payment_volume_shares.png")

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(totals.Financial_Year, totals.Total_Retail_Volume_Lakh / 10_000,
            marker="o", lw=2.6, color=NAVY, label="Retail payments")
    ax.plot(totals.Financial_Year, totals.Total_Digital_Volume_Lakh / 10_000,
            marker="o", lw=2.6, color=TEAL, label="Digital payments")
    ax.set(title="RBI aggregate payment volumes", ylabel="Transactions (billion)", xlabel="Financial year")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.22)
    _source_note(fig, "RBI Annual Reports 2023-24 and 2025-26; digital includes RTGS and excludes paper, retail excludes RTGS and includes paper")
    _save(fig, "06_aggregate_payment_volume.png")


def generate_dashboard(modes, totals, metrics):
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(15, 9), facecolor="#f5f8fb")
    fig.text(.045, .95, "INDIA DIGITAL PAYMENTS", fontsize=12, color=TEAL, weight="bold")
    fig.text(.045, .91, "Payment-channel mix & growth | FY 2021-22 to FY 2025-26", fontsize=21, color=NAVY, weight="bold")
    fig.text(.045, .875, f"Prepared by {AUTHOR}  •  Official RBI annual data", fontsize=9.5, color=MUTED)
    cards = [
        (f"{totals.iloc[-1].UPI_Share_Of_Retail_Volume_Pct:.1f}%", "UPI share of retail volume, FY 2025-26"),
        (f"{metrics['upi_volume_growth_pct']:.1f}%", "UPI volume change across the 5-year window"),
        (f"{totals.iloc[-1].Total_Digital_Volume_Lakh / 10_000:.1f}B", "Total digital transactions, FY 2025-26"),
        (f"₹{metrics['upi_value_fy_2025_26_lakh_crore']:.1f}", "UPI value (₹ lakh crore), FY 2025-26"),
    ]
    for i, (num, label) in enumerate(cards):
        x = .045 + i * .235
        fig.patches.append(plt.Rectangle((x, .77), .215, .075, transform=fig.transFigure,
                                         facecolor="white", edgecolor="#d7e1e9", linewidth=1))
        fig.text(x + .014, .805, num, fontsize=17, color=TEAL, weight="bold")
        fig.text(x + .014, .781, label, fontsize=7.2, color=MUTED)
    panels = [
        ("01_retail_mode_volume_log.png", "Retail mode volumes (log scale)"),
        ("02_mode_volume_index.png", "Mode volume index"),
        ("03_retail_mode_value.png", "Retail mode values"),
        ("05_payment_volume_shares.png", "UPI share of retail volume"),
    ]
    for i, (name, title) in enumerate(panels):
        row, col = divmod(i, 2)
        ax = fig.add_axes([.045 + col * .475, .40 - row * .31, .43, .25])
        ax.imshow(plt.imread(IMAGES / name))
        ax.set_title(title, loc="left", fontsize=10, color=NAVY, weight="bold")
        ax.axis("off")
    fig.text(.045, .055, "Volume is in transactions (lakh); value is ₹ lakh crore. RTGS is shown separately in analytical charts.", fontsize=8, color=MUTED)
    fig.text(.045, .035, "Source: RBI Annual Reports 2023-24 and 2025-26, Table IX.1. See DATA_SOURCES.md for caveats.", fontsize=7.5, color=MUTED)
    out = DASHBOARD / "payment_channel_dashboard.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    (DASHBOARD / "payment_channel_dashboard.html").write_text(
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>India Digital Payments Dashboard</title><style>body{font-family:Arial,sans-serif;margin:24px;background:#f5f8fb;color:#14283f}"
        "img{max-width:100%;height:auto;display:block;margin:auto}main{max-width:1500px;margin:auto}</style>"
        "<main><img src='payment_channel_dashboard.png' alt='India Digital Payments channel dashboard'></main></html>",
        encoding="utf-8",
    )


def _add_image_page(pdf, name, title, page):
    fig = plt.figure(figsize=(11.7, 8.3))
    ax = fig.add_axes([.04, .08, .92, .84])
    ax.imshow(plt.imread(IMAGES / name))
    ax.set_title(title, loc="left", fontsize=16, color=NAVY, weight="bold")
    ax.axis("off")
    fig.text(.04, .022, f"India Digital Payments Analytics | {AUTHOR} | RBI Annual Reports 2023-24 and 2025-26", fontsize=8, color=MUTED)
    fig.text(.96, .022, str(page), fontsize=8, color=MUTED, ha="right")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def build_report(modes, totals, metrics):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    latest = totals.iloc[-1]
    upi_latest = modes.query("Payment_Mode == 'UPI'").iloc[-1]
    neft_latest = modes.query("Payment_Mode == 'NEFT'").iloc[-1]
    with PdfPages(REPORT, metadata={
        "Title": "India Digital Payments: Payment-channel Mix and Growth",
        "Author": AUTHOR,
        "Subject": "Descriptive analysis of RBI annual payment system indicators",
    }) as pdf:
        fig = plt.figure(figsize=(11.7, 8.3), facecolor="#f5f8fb")
        fig.text(.07, .92, "INDIA DIGITAL PAYMENTS", fontsize=12, color=TEAL, weight="bold")
        fig.text(.07, .85, "Payment-channel mix & growth", fontsize=26, color=NAVY, weight="bold")
        fig.text(.07, .80, "UPI, NEFT, IMPS, RTGS, cards and prepaid instruments", fontsize=11, color=MUTED)
        fig.text(.07, .755, f"Prepared by {AUTHOR}", fontsize=11, color=NAVY, weight="bold")
        fig.text(.07, .72, "LinkedIn: Mansi Saxena", fontsize=8, color=TEAL, url="https://www.linkedin.com/in/mansi-saxena-049102362")
        fig.text(.39, .72, "GitHub: 050804mansi", fontsize=8, color=TEAL, url="https://github.com/050804mansi")
        fig.text(.68, .72, "Email: mansi53245@gmail.com", fontsize=8, color=TEAL, url="mailto:mansi53245@gmail.com")
        cards = [
            (f"{latest.UPI_Share_Of_Retail_Volume_Pct:.1f}%", "UPI share of retail volume\nFY 2025-26"),
            (f"{metrics['upi_volume_growth_pct']:.1f}%", "UPI volume change\nFY 2021-22 to FY 2025-26"),
            (f"{latest.Total_Digital_Volume_Lakh / 10_000:.1f}B", "Digital transactions\nFY 2025-26"),
        ]
        for i, (num, label) in enumerate(cards):
            x = .07 + i * .30
            fig.patches.append(plt.Rectangle((x, .56), .26, .105, transform=fig.transFigure,
                                             facecolor="white", edgecolor="#d7e1e9"))
            fig.text(x + .018, .615, num, fontsize=17, color=TEAL, weight="bold")
            fig.text(x + .018, .575, label, fontsize=8.5, color=MUTED)
        fig.text(.07, .49, "Executive summary", fontsize=14, color=NAVY, weight="bold")
        bullets = [
            f"UPI recorded {upi_latest.Transaction_Volume_Lakh:,.0f} lakh transactions and ₹{upi_latest.Transaction_Value_Lakh_Crore:,.1f} lakh crore value in FY 2025-26.",
            f"UPI made up {latest.UPI_Share_Of_Retail_Volume_Pct:.1f}% of RBI-reported retail payment volume in FY 2025-26.",
            f"NEFT processed ₹{neft_latest.Transaction_Value_Lakh_Crore:,.1f} lakh crore in FY 2025-26; RTGS is treated separately as a large-value system.",
            f"Across the five-year window, total digital payment volume changed by {metrics['digital_volume_growth_pct']:.1f}%.",
        ]
        y = .435
        for bullet in bullets:
            fig.text(.08, y, "•", fontsize=13, color=GOLD, weight="bold")
            fig.text(.105, y, textwrap.fill(bullet, 105), fontsize=9.5, color=NAVY, va="top", linespacing=1.35)
            y -= .075
        fig.text(.07, .09, "Annual aggregate data for FY 2021-22 to FY 2025-26. Results are descriptive; source units and limitations are documented on page 8.", fontsize=8.5, color=MUTED, wrap=True)
        fig.text(.04, .022, f"Source: RBI Annual Reports 2023-24 and 2025-26, Table IX.1 | {AUTHOR}", fontsize=8, color=MUTED)
        fig.text(.96, .022, "1", fontsize=8, color=MUTED, ha="right")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        _add_image_page(pdf, "01_retail_mode_volume_log.png", "Payment-channel transaction volumes", 2)
        _add_image_page(pdf, "02_mode_volume_index.png", "Relative volume growth by channel", 3)
        _add_image_page(pdf, "03_retail_mode_value.png", "Transaction value by selected retail channel", 4)
        _add_image_page(pdf, "04_average_ticket_size.png", "Estimated average transaction size", 5)
        _add_image_page(pdf, "05_payment_volume_shares.png", "UPI share of retail payment volume", 6)
        _add_image_page(pdf, "06_aggregate_payment_volume.png", "Aggregate retail and digital payment volumes", 7)

        fig = plt.figure(figsize=(11.7, 8.3))
        fig.text(.06, .93, "Definitions, method and limitations", fontsize=19, color=NAVY, weight="bold")
        notes = [
            ("Source", "Reserve Bank of India, Annual Reports 2023-24 and 2025-26, Chapter IX, Table IX.1: Payment System Indicators - Annual Turnover (April-March)."),
            ("Units", "Volume is in lakh transactions; value is in ₹ lakh crore. Financial years run April to March."),
            ("Average ticket", "Estimated as transaction value (₹ lakh crore) divided by volume (lakh transactions), multiplied by 10,000,000. RBI publishes rounded aggregate figures, so this is approximate."),
            ("Mode coverage", "Selected modes include UPI, NEFT, IMPS, credit and debit cards, prepaid instruments and RTGS. RTGS is a large-value system and is not treated as a retail peer."),
            ("Comparisons", "UPI share uses RBI total retail payment volume as the denominator. RBI's total digital aggregate includes RTGS and excludes paper-based instruments; total retail excludes RTGS and includes paper-based instruments. These aggregates are not nested, so no digital-to-retail share is calculated."),
            ("Limitations", "Five annual observations do not show monthly seasonality or individual behaviour. The data are aggregate and cannot establish causes or forecast future activity."),
            ("Source rights", "RBI statistics are attributed to the publisher. The author claims rights only over original code, SQL, notebook, narrative and visual design; see COPYRIGHT.txt."),
        ]
        y = .84
        for head, body in notes:
            fig.text(.07, y, head, fontsize=10.5, color=TEAL, weight="bold", va="top")
            fig.text(.24, y, textwrap.fill(body, 112), fontsize=9, color=NAVY, va="top", linespacing=1.35)
            y -= .105
        fig.text(.07, .08, f"Official RBI sources: 2023-24 {SOURCE_URL_EARLY} | 2025-26 {SOURCE_URL}", fontsize=7.2, color=TEAL, url=SOURCE_URL, wrap=True)
        fig.text(.04, .022, f"India Digital Payments Analytics | {AUTHOR}", fontsize=8, color=MUTED)
        fig.text(.96, .022, "8", fontsize=8, color=MUTED, ha="right")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    modes, totals = load_data()
    metrics = summary(modes, totals)
    store_sqlite(modes, totals)
    generate_charts(modes, totals)
    generate_dashboard(modes, totals, metrics)
    build_report(modes, totals, metrics)
    print(f"Created {len(list(IMAGES.glob('*.png')))} charts, dashboard and report: {REPORT}")
    print({key: round(value, 2) for key, value in metrics.items()})


if __name__ == "__main__":
    main()
