from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, SelectField, IntegerField
from wtforms.validators import InputRequired, Email, EqualTo
import re
import pycountry
from main import client_details


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
        if client_details:
            self.default = client_details["country_name"]


def password_validation(form, field):
    if re.search(r'[A-Z]', field.data):
        if re.search(r'[a-z]', field.data):
            if re.search(r'\d', field.data):
                return
    print('Password Error')
    raise ValidationError('* Invalid Password')


# WTForms

class RegisterUserForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("E-mail Address", validators=[InputRequired(),
                                                      Email('* Invalid Email')])
    phone = StringField("Phone Number", validators=[InputRequired()])
    company_name = StringField("Company Name", validators=[InputRequired()])
    password = PasswordField('Create Password', validators=[InputRequired(), password_validation])
    pass_repeat = PasswordField('Re-Enter Password', validators=[InputRequired(),
                                                                 EqualTo('password', '* Passwords must match.')])
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
                                  validators=[InputRequired(), Email('* Invalid Email')])
    payment_amount = IntegerField("Payment Amount", validators=[InputRequired()])
    payment_type = PaymentTypeSelectField('Payment Type', validators=[InputRequired()])
    submit = SubmitField("Create Document")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")


