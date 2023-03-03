from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
from db_architecture import Address

# Define the font and font size for the paragraph
FONT = "Helvetica"
F_SIZE = 12

# Define a ParagraphStyle object with the desired attributes
P_STYLE = ParagraphStyle(
    name="Normal",
    fontName=FONT,
    fontSize=F_SIZE,
    leading=F_SIZE*1.2,
    alignment=TA_CENTER)


def create_pdf(user, document):
    address = Address.query.filter_by(user_id=user.id).first()
    address_attrs = address.get_attrs()
    # Set up the canvas with the background image
    background_image = '/Users/merongelbard/Documents/projects/receipt app/static/assets/doc/doc_template.jpg'
    pdf_canvas = canvas.Canvas('static/assets/doc/document.pdf', pagesize=A4)
    pdf_canvas.drawImage(background_image, 0, 0, width=A4[0], height=A4[1])

    # Set up the text fields and populate them with the dynamic data
    sender_name = pdf_canvas.beginText(18.7, A4[1] - 45.5)
    sender_name.textLine(f'{user.first_name} {user.last_name}')

    sender_company = pdf_canvas.beginText(18.7, A4[1] - 67)
    sender_company.textLine(user.company_name)

    issue_date = pdf_canvas.beginText(524, A4[1] - 29)
    issue_date.textLine(datetime.now().strftime("%m/%d/%Y"))

    doc_header = pdf_canvas.beginText(18.7, A4[1] - 115.6)
    doc_header.textLine(f'{document.doc_type} - {document.doc_id}')

    list_date = pdf_canvas.beginText(64.5, A4[1] - 250)
    list_date.textLine(document.doc_date.strftime("%m/%d/%Y"))

    doc_recipient = pdf_canvas.beginText(64, A4[1] - 288)
    doc_recipient.textLine(document.recipient.name)

    doc_subject = pdf_canvas.beginText(89.5, A4[1] - 330)
    doc_subject.textLine(document.subject)

    payment_amount = pdf_canvas.beginText(434.5, A4[1] - 588)
    payment_amount.textLine(str(document.payment_amount))

    payment_type = pdf_canvas.beginText(433, A4[1] - 634)
    payment_type.textLine(document.payment_type)

    contact_details_text = f'{user.first_name} {user.last_name} - {user.company_name}\n' \
                           f'{user.email} | {user.phone} | ' \
                           f'{address_attrs["address"]}, {address_attrs["city"]}, {address_attrs["country"]}'
    contact_details = Paragraph(text=contact_details_text, style=P_STYLE)

    # Add the text fields to the canvas
    pdf_canvas.drawText(sender_name)
    pdf_canvas.drawText(sender_company)
    pdf_canvas.drawText(issue_date)
    pdf_canvas.drawText(doc_header)
    pdf_canvas.drawText(list_date)
    pdf_canvas.drawText(doc_recipient)
    pdf_canvas.drawText(doc_subject)
    pdf_canvas.drawText(payment_amount)
    pdf_canvas.drawText(payment_type)

    contact_details.wrapOn(pdf_canvas, 100, 100)
    contact_details.drawOn(pdf_canvas, 66, A4[1] - 770)

    # Save and close the PDF document
    pdf_canvas.save()



