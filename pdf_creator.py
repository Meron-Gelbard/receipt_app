from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def create_pdf(doc_name, company_name, date, recipient_name, payment_amount):
    # Load the background template image
    background_image = '/Users/merongelbard/Documents/projects/receipt app/static/assets/doc/doc template.jpg'

    # Set up the canvas with the background image
    pdf_canvas = canvas.Canvas('static/assets/doc/document.pdf', pagesize=A4)
    pdf_canvas.drawImage(background_image, 0, 0, width=A4[0], height=A4[1])

    # Set up the text fields and populate them with the dynamic data
    doc_name_t = pdf_canvas.beginText(18.7, A4[1] - 115.6)
    doc_name_t.textLine(doc_name)

    company_name_t = pdf_canvas.beginText(18.7, A4[1] - 67)
    company_name_t.textLine(company_name)

    date_t = pdf_canvas.beginText(64.5, A4[1] - 250)
    date_t.textLine(date)

    recipient_name_t = pdf_canvas.beginText(58, A4[1] - 288.5)
    recipient_name_t.textLine(recipient_name)

    payment_amount_t = pdf_canvas.beginText(434.5,  A4[1] - 588)
    payment_amount_t.textLine(payment_amount)

    # Add the text fields to the canvas
    pdf_canvas.drawText(doc_name_t)
    pdf_canvas.drawText(company_name_t)
    pdf_canvas.drawText(date_t)
    pdf_canvas.drawText(recipient_name_t)
    pdf_canvas.drawText(payment_amount_t)

    # Save and close the PDF document
    pdf_canvas.save()


create_pdf(doc_name='Merons doc', company_name='Meron Music', date='26/05/87',
           recipient_name='Vanilla Cat', payment_amount='1501')


