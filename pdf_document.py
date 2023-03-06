from io import BytesIO
from flask import Response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from db_architecture import Address


class DocPdf:
    def __init__(self, user, document):
        self.user = user
        self.document = document
        self.response = None
        self.create_pdf()

    def create_pdf(self):
        address = Address.query.filter_by(user_id=self.user.id).first()
        address_attrs = address.get_attrs()

        buffer = BytesIO()

        background_image = 'static/assets/doc/doc_template.jpg'
        pdf_canvas = canvas.Canvas(buffer, pagesize=A4)
        pdf_canvas.setTitle(f'{self.user.company_name} - {self.document.doc_type} {self.document.doc_id}')
        pdf_canvas.setAuthor(f'{self.user.first_name} {self.user.last_name}')
        pdf_canvas.setCreator('Kabalar - Document Management')

        pdf_canvas.drawImage(background_image, 0, 0, width=A4[0], height=A4[1])

        sender_name = pdf_canvas.beginText(18.7, A4[1] - 45.5)
        sender_name.textLine(f'{self.user.first_name} {self.user.last_name}')
    
        sender_company = pdf_canvas.beginText(18.7, A4[1] - 63)
        sender_company.textLine(self.user.company_name)
    
        issue_date = pdf_canvas.beginText(340, A4[1] - 29)
        issue_date.textLine(datetime.now().strftime("Copy Issued On: %m/%d/%Y"))
    
        doc_header = pdf_canvas.beginText(18.7, A4[1] - 115.6)
        doc_header.textLine(f'{self.document.doc_type} - {self.document.doc_serial_num.split("_")[2]}')
    
        list_date = pdf_canvas.beginText(68, A4[1] - 250)
        list_date.textLine(self.document.doc_date.strftime("%m/%d/%Y"))
    
        doc_recipient = pdf_canvas.beginText(64, A4[1] - 285)
        doc_recipient.textLine(self.document.recipient.name)
    
        doc_subject = pdf_canvas.beginText(90.5, A4[1] - 328)
        doc_subject.textLine(self.document.subject)

        payment_amount = pdf_canvas.beginText(434.5, A4[1] - 584)
        payment_amount.textLine(f'{str(self.document.payment_amount)} {self.user.currency}')

        payment_type = pdf_canvas.beginText(433, A4[1] - 630)
        payment_type.textLine(self.document.payment_type)

        contact_a = pdf_canvas.beginText(37, A4[1] - 776)
        contact_a.textLine(f'{self.user.first_name} {self.user.last_name} - {self.user.company_name}')
        contact_b = pdf_canvas.beginText(37, A4[1] - 792)
        contact_b.textLine(f'{self.user.email} | {self.user.phone}')
        contact_c = pdf_canvas.beginText(37, A4[1] - 808)
        contact_c.textLine(f'{address_attrs["address"]}, {address_attrs["city"]}, {address_attrs["country"]}')

        pdf_canvas.setFont('Helvetica', 17)
        pdf_canvas.drawText(doc_header)

        pdf_canvas.setFont('Courier', 15)
        pdf_canvas.drawText(list_date)
        pdf_canvas.drawText(sender_name)
        pdf_canvas.drawText(sender_company)
        pdf_canvas.drawText(issue_date)
        pdf_canvas.drawText(doc_recipient)
        pdf_canvas.drawText(doc_subject)
        pdf_canvas.drawText(payment_amount)
        pdf_canvas.drawText(payment_type)

        pdf_canvas.setFont('Helvetica', 11)
        pdf_canvas.drawText(contact_a)
        pdf_canvas.drawText(contact_b)
        pdf_canvas.drawText(contact_c)

        pdf_canvas.save()

        buffer.seek(0)
        self.response = Response(buffer, mimetype='application/pdf')
        self.response.headers['Content-Disposition'] =\
            f'inline; filename={self.document.doc_type} {self.document.doc_id}.pdf'
