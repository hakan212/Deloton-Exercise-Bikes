"""Generates pdf report with logo, graphs and data"""

from datetime import date

from fpdf import FPDF

from visualisation_generator import (get_data_between_timestamps, get_mean_heart_rate,
                                     get_mean_power_output,
                                     get_mean_total_power, get_number_of_rides,
                                     plot_age_rides_bar, plot_gender_rides_pie)

A4_DOC_WIDTH = 210


def create_image_header(pdf):
    """Creates an image header with the logo"""
    pdf.image("./assets/deloton-logo.png", -0.1, 0, A4_DOC_WIDTH + 1)
    pdf.ln(5)


def create_cover_title(pdf):
    """Creates a cover title"""
    pdf.set_font("Times", "", 36)
    pdf.ln(75)
    pdf.write(5, "Deloton Daily Report")
    pdf.ln(10)
    pdf.set_font("Times", "", 20)
    pdf.write(4, f"{date.today()}")
    pdf.ln(10)


def create_page_title(pdf, text):
    """Creates a page title"""
    pdf.set_font("Times", "", 24)
    pdf.ln(15)
    pdf.write(5, f"{text}")
    pdf.line(0, 110, 210, 110)


def create_text_block(pdf, df_rides, df_yesterday):
    """
    Creates a text block with key ride analytics:
    total number of rides, average total power generated,
    average power generated per ride, and average heart rate
    per rider.
    """
    pdf.set_font("Times", "", 16)
    pdf.ln(15)
    pdf.write(5, f"Total number of rides in past 24 hours: {get_number_of_rides(df_rides)}")
    pdf.ln(10)
    pdf.write(5, f"Total number of rides 24 to 48 hours ago: {get_number_of_rides(df_yesterday)}")
    pdf.ln(10)
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


def create_graph_block(pdf):
    """
    Creates a block with two data insight graphs:
    gender split for rides, and age split for rides
    """
    pdf.image("/tmp/gender_fig.png", 0, 185, w=95, h=100)
    pdf.image("/tmp/age_fig.png", 100, 185, w=115, h=100)


def save_pdf_file(pdf):
    """Saves the pdf into the temp directory in /tmp"""
    pdf.output(name="/tmp/deloton_daily_report.pdf", dest="F")


def generate_report(df_rides, df_yesterday):
    """Generate a PDF report with data insights"""
    pdf = FPDF()  # A4 by default
    pdf.compress = False
    pdf.add_page()

    create_image_header(pdf)
    create_cover_title(pdf)
    create_page_title(pdf, text="Ride Analytics")
    create_text_block(pdf, df_rides, df_yesterday)
    create_graph_block(pdf)
    save_pdf_file(pdf)


if __name__ == "__main__":
    df_rides = get_data_between_timestamps("(NOW() - INTERVAL '24 hours')", "NOW()")
    plot_age_rides_bar(df_rides)
    plot_gender_rides_pie(df_rides)
    generate_report(df_rides)
