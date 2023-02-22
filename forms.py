from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, SelectField, IntegerField
from wtforms.validators import InputRequired, Email, EqualTo
import re
import pycountry


class DocTypeSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(DocTypeSelectField, self).__init__(*args, **kwargs)
        self.choices = ['Receipt', 'Job Order', 'Receipt Cancellation', 'Invoice', 'Quotation']


class PaymentTypeSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(PaymentTypeSelectField, self).__init__(*args, **kwargs)
        self.choices = ['Cash', 'Bank Transfer', 'Credit Card', 'Payment App', 'Bank Cheque', 'Crypto Currency']


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [country.name for country in pycountry.countries]


def password_validation(form, field):
    if re.search(r'[A-Z]', field.data):
        if re.search(r'[a-z]', field.data):
            if re.search(r'\d', field.data):
                return
    print('Password Error')
    raise ValidationError('Password must contain at least one uppercase, one lowercase and one number character.')


# WTForms

class RegisterUserForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("E-mail Address", validators=[InputRequired(), Email(message="Enter a valid email address.")])
    phone = StringField("Phone Number", validators=[InputRequired()])
    company_name = StringField("Company Name", validators=[InputRequired()])
    password = PasswordField('Create Password', validators=[InputRequired(), password_validation,
                                                            EqualTo('pass_repeat', message='Passwords must match.')])
    pass_repeat = PasswordField('Re-Enter Password', validators=[InputRequired()])
    country = CountrySelectField('Country', validators=[InputRequired()])
    city = StringField("City:", validators=[InputRequired()])
    address = StringField("Full Address:", validators=[InputRequired()])
    submit = SubmitField("Register User")


class NewDocumentForm(FlaskForm):
    doc_type = DocTypeSelectField('Document Type', validators=[InputRequired()])
    subject = StringField("Subject", validators=[InputRequired()])
    recipient_name = StringField("Recipient Name")
    recipient_phone = StringField("Recipient Phone Number")
    recipient_address = StringField("Recipient Address")
    recipient_email = StringField("Recipient E-Mail Address",
                                  validators=[InputRequired(), Email(message="Enter a valid email address.")])
    payment_amount = IntegerField("Payment Amount", validators=[InputRequired()])
    payment_type = PaymentTypeSelectField('Payment Type', validators=[InputRequired()])
    submit = SubmitField("Create Document")


