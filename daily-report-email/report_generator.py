from fpdf import FPDF
from datetime import date

WIDTH = 210
HEIGHT = 297

def create_cover_title(pdf):
    """
    Creates a cover title
    """
    pdf.set_font("Times", "", 36)
    pdf.ln(100)
    pdf.write(5, "Deloton Daily Report")
    pdf.ln(10)
    pdf.set_font("Times", "", 16)
    pdf.write(4, f"{date.today()}")
    pdf.ln(5)

def create_page_title(pdf, text):
    """Creates a page title"""
    pdf.set_font("Times", "", 30)
    pdf.ln(10)
    pdf.write(5, f"{text}")


def generate_report():
    pdf = FPDF() #A4 by default
    pdf.compress = False

    # Cover Page
    pdf.add_page()
    pdf.set_font('Times', '', 20)  
    pdf.image("./assests/images/deloton-logo.png", 0, 0, WIDTH)
    create_cover_title(pdf)


    # Page 1 Analytics
    pdf.add_page() 
    create_page_title(pdf, "Ride Analytics")



    pdf.output('py3k.pdf', 'F')

generate_report()