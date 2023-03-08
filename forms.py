from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, SelectField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Email, EqualTo
import re
import pycountry
from main import client_details
import csv


class CurrencySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CurrencySelectField, self).__init__(*args, **kwargs)
        with open('static/assets/currencies.csv') as file:
            csv_reader = csv.DictReader(file)
            currencies = {}
            for row in csv_reader:
                currency = row["Currency"]
                code = row["Code"]
                symbol = row["Symbol"]
                currencies[code] = {"currency": currency, "symbol": symbol}
        self.choices = [f'{value["currency"]} - {code} / {value["symbol"]}' for code, value in currencies.items()]


class RecipientSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(RecipientSelectField, self).__init__(*args, **kwargs)
        self.choices = []
        self.populate()

    def populate(self):
        user = current_user
        for customer in user.recipients:
            self.choices.append(customer.name)


class DocTypeSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(DocTypeSelectField, self).__init__(*args, **kwargs)
        self.choices = ['Receipt', 'Job Order', 'Receipt Cancellation', 'Invoice', 'Quotation']
        self.default = None


class PaymentTypeSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(PaymentTypeSelectField, self).__init__(*args, **kwargs)
        self.choices = ['Cash', 'Bank Transfer', 'Credit Card', 'Payment App', 'Bank Cheque', 'Crypto Currency']
        self.default = None


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
    city = StringField("City", validators=[InputRequired()])
    address = StringField("Full Address", validators=[InputRequired()])
    website = StringField("Web Site URL")
    submit = SubmitField("Register User")


class UpdateUserForm(FlaskForm):

    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("E-mail Address", validators=[InputRequired(),
                                                      Email('* Invalid Email')])
    phone = StringField("Phone Number", validators=[InputRequired()])
    company_name = StringField("Company Name", validators=[InputRequired()])
    country = CountrySelectField('Country', validators=[InputRequired()])
    city = StringField("City", validators=[InputRequired()])
    address = StringField("Full Address", validators=[InputRequired()])
    website = StringField("Web Site URL")
    submit = SubmitField("Save Edits")


class UpdateRecipientForm(FlaskForm):
    name = StringField("Customer Name", validators=[InputRequired()])
    email = StringField("E-mail Address", validators=[InputRequired(),
                                                      Email('* Invalid Email')])
    phone = StringField("Phone Number", validators=[InputRequired()])
    address = StringField("Full Address", validators=[InputRequired()])
    submit = SubmitField("Save Edits")


class NewDocumentForm(FlaskForm):

    doc_type = DocTypeSelectField('Document Type', validators=[InputRequired()])
    subject = StringField("Subject", validators=[InputRequired()])
    listed_customers = RecipientSelectField("Listed Customers:", validators=[InputRequired()])
    recipient_name = StringField("Customer Name", validators=[InputRequired()])
    recipient_phone = StringField("Recipient Phone Number")
    recipient_address = StringField("Recipient Address")
    recipient_email = StringField("Recipient E-Mail Address",
                                  validators=[InputRequired(), Email('* Invalid Email')])
    payment_amount = IntegerField("Payment Amount", validators=[InputRequired()])
    payment_type = PaymentTypeSelectField('Payment Type', validators=[InputRequired()])

    submit = SubmitField("Create Document")

    new_customer_form = ['doc_type', 'subject', 'recipient_name', 'recipient_phone', 'recipient_address',
                         'payment_amount', 'payment_type', 'recipient_email']

    listed_customer_form = ['doc_type', 'subject', 'listed_customers',
                            'payment_amount', 'payment_type', 'recipient_email']



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")


class ChangeCurrencyFrom(FlaskForm):
    currency = CurrencySelectField('Select Currency', validators=[InputRequired()])
    submit = SubmitField("Change")
