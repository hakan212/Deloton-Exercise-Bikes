from datetime import date

from fpdf import FPDF

from visualisation_generator import (get_mean_heart_rate,
                                     get_mean_power_output,
                                     get_mean_total_power)

# A4 page size in mm
HEIGHT = 297
WIDTH = 210


def create_cover_title(pdf):
    """
    Creates a cover title
    """
    pdf.set_font("Times", "", 36)
    pdf.ln(75)
    pdf.write(5, "Deloton Daily Report")
    pdf.ln(10)
    pdf.set_font("Times", "", 20)
    pdf.write(4, f"{date.today()}")
    pdf.ln(5)


def create_page_title(pdf, text):
    """Creates a page title"""
    pdf.set_font("Times", "", 24)
    pdf.ln(15)
    pdf.write(5, f"{text}")


def generate_report(df_rides):
    """Generate a PDF report with data insights"""
    pdf = FPDF()  # A4 by default
    pdf.compress = False

    pdf.add_page()
    pdf.image("./assets/images/deloton-logo.png", -0.1, 0, WIDTH + 1)
    pdf.ln(5)

    create_cover_title(pdf)
    pdf.line(0, 110, 210, 110)

    pdf.ln(5)
    create_page_title(pdf, "Ride Analytics")

    pdf.set_font("Times", "", 16)
    pdf.ln(15)
    pdf.write(
        5,
        f"Average total power generated: {round(get_mean_total_power(df_rides)/1000)} kW",
    )
    pdf.ln(10)
    pdf.write(
        5, f"Average power generated per rider: {get_mean_power_output(df_rides)} W"
    )
    pdf.ln(10)
    pdf.write(
        5, f"Average heart rate per rider: {round(get_mean_heart_rate(df_rides))} bpm"
    )

    pdf.image("./assets/tmp/gender_fig.png", 0, 185, w=95, h=100)
    pdf.image("./assets/tmp/age_fig.png", 100, 185, w=115, h=100)

    pdf.output(name="./assets/tmp/deloton_daily_report.pdf", dest="F")
