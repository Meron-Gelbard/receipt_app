from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, SelectField,\
    IntegerField, TextAreaField, BooleanField
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
        for choice in self.choices:
            if current_user._get_current_object().currency in choice:
                self.default = choice
                break


class CustomerSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CustomerSelectField, self).__init__(*args, **kwargs)
        self.choices = []
        self.populate()

    def populate(self):
        user = current_user
        for customer in user.customers:
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
    first_name = StringField("First Name", validators=[InputRequired()], id='first_name')
    last_name = StringField("Last Name", validators=[InputRequired()], id='last_name')
    email = StringField("E-mail Address", validators=[InputRequired(),
                                                      Email('* Invalid Email')], id='email')
    phone = StringField("Phone Number", validators=[InputRequired()], id='phone')
    company_name = StringField("Company Name", validators=[InputRequired()], id='company_name')
    password = PasswordField('Create Password', validators=[InputRequired(), password_validation], id='new_p')
    pass_repeat = PasswordField('Re-Enter Password', validators=[InputRequired(),
                                EqualTo('password', '* Passwords must match.')], id='new_r')
    country = CountrySelectField('Country', validators=[InputRequired()], id='country')
    city = StringField("City", validators=[InputRequired()], id='city')
    address = StringField("Full Address", validators=[InputRequired()], id='address')
    website = StringField("Web Site URL", id='website')
    submit = SubmitField("Register User", id='submit')
    show_pass = BooleanField('Show password')


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


class UpdateCustomerForm(FlaskForm):
    name = StringField("Customer Name", validators=[InputRequired()])
    email = StringField("E-mail Address", validators=[InputRequired(),
                                                      Email('* Invalid Email')])
    phone = StringField("Phone Number", validators=[InputRequired()])
    address = StringField("Full Address", validators=[InputRequired()])
    submit = SubmitField("Save Edits")


class NewDocumentForm:
    @classmethod
    def create(cls, checkbox='false'):
        if checkbox == 'true':
            class NewDocForm(FlaskForm):
                listed_customers = CustomerSelectField("Listed Customers:", validators=[InputRequired()])
                doc_type = DocTypeSelectField('Document Type', validators=[InputRequired()])
                subject = StringField("Subject", validators=[InputRequired()])
                payment_amount = IntegerField("Payment Amount", validators=[InputRequired()])
                currency = CurrencySelectField('Select Currency', validators=[InputRequired()])
                payment_type = PaymentTypeSelectField('Payment Type', validators=[InputRequired()])
                extra_details = TextAreaField('Extra Details')
                submit = SubmitField("Create Document")

                def __init__(self):
                    super(NewDocForm, self).__init__()
                    self.fields = ['doc_type', 'subject', 'listed_customers', 'payment_amount', 'payment_type', 'extra_details']

            return NewDocForm()

        elif checkbox == 'false' or checkbox is None:

            class NewDocForm1(FlaskForm):
                doc_type = DocTypeSelectField('Document Type', validators=[InputRequired()])
                subject = StringField("Subject", validators=[InputRequired()])
                payment_amount = IntegerField("Payment Amount", validators=[InputRequired()])
                currency = CurrencySelectField('Select Currency', validators=[InputRequired()])
                payment_type = PaymentTypeSelectField('Payment Type', validators=[InputRequired()])
                customer_name = StringField("Customer Name", validators=[InputRequired()])
                customer_phone = StringField("Customer Phone Number")
                customer_address = StringField("Customer Address")
                customer_email = StringField("Customer E-Mail Address",
                                              validators=[InputRequired(), Email('* Invalid Email')])
                extra_details = TextAreaField('Extra Details')
                submit = SubmitField("Create Document")

                def __init__(self):
                    super(NewDocForm1, self).__init__()
                    self.fields = ['doc_type', 'subject', 'customer_name', 'customer_phone', 'customer_address',
                                   'customer_email', 'payment_amount', 'payment_type', 'extra_details']

            return NewDocForm1()


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")
    show_pass = BooleanField('Show Password')


class ChangeCurrencyFrom(FlaskForm):
    currency = CurrencySelectField('Select Currency', validators=[InputRequired()])
    submit = SubmitField("Change")


class ChangePasswordForm(FlaskForm):
    current_pass = PasswordField('Enter current password', validators=[InputRequired(), password_validation], id='current_p')
    current_repeat = PasswordField('Re-Enter current password', validators=[InputRequired(),
                                   EqualTo('current_pass', '* Passwords must match.')], id='current_r')
    new_pass = PasswordField('Create new password', validators=[InputRequired(), password_validation], id='new_p')
    new_repeat = PasswordField('Re-Enter new password',
                               validators=[InputRequired(), EqualTo('new_pass', '* Passwords must match.')], id='new_r')
    submit = SubmitField("Update Password")
    show_pass = BooleanField('Show Passwords')


class RenewPasswordForm(FlaskForm):
    new_pass = PasswordField('Create new password', validators=[InputRequired(), password_validation], id='new_p')
    new_repeat = PasswordField('Re-Enter new password',
                               validators=[InputRequired(), EqualTo('new_pass', '* Passwords must match.')], id='new_r')
    submit = SubmitField("Save new password")
    show_pass = BooleanField('Show Passwords')


class EmailFieldForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    submit = SubmitField("Send confirmation")
