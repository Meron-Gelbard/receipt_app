from sqlalchemy import create_engine
from flask import Flask, flash, session
from flask_sqlalchemy import SQLAlchemy
import requests

# hash these later...
SECRET = '1111'
DB_HOST_NAME = 'localhost'
DB_NAME = 'receipt_app1'
DB_USERN = 'postgres'
APP_KEY = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# make environment variables later...
SQLALCHEMY_DB_URI = f'postgresql+psycopg2://{DB_USERN}:{SECRET}@{DB_HOST_NAME}/{DB_NAME}'
api_key = 'def31c8d33834a5aa3f352665bd954f5'
try:
    client_details = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}').json()
except Exception:
    client_details = None

engine = create_engine(SQLALCHEMY_DB_URI)

app = Flask(__name__)
app.config['SECRET_KEY'] = {APP_KEY}

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"autoflush": False})


class MessageManager:
    def __init__(self):
        self.messages = ['']

    def clear(self):
        if session.get('_flashes'):
            session['_flashes'].clear()
        self.messages = ['']
        self.flash_messages()

    def flash_messages(self):
        for msg in self.messages:
            flash(msg)

    def login_messages(self, details):
        self.messages = []
        if details == 'user not found':
            self.messages.append('User not found, Please try again')
        if details == 'login OK':
            self.messages.append('Logged in successfully.')
        if details == 'pass error':
            self.messages.append('Wrong Password. Please try again.')
        if details == 'pass change':
            self.messages.append('Password was changed successfully.')
        self.flash_messages()

    def database_error(self, details):
        if 'user_name' in details:
            self.messages.append('This user name already exists.')
        if 'address' in details:
            self.messages += ['This address is already in use.',
                              'Please be more specific if needed or choose a different address.']
        if 'email' in details:
            self.messages.append('This E-Mail address is already in use.')
        self.flash_messages()
        if 'company_name' in details:
            self.messages.append('This company name is already in use. Only one account per company is allowed.')
        self.flash_messages()

    def form_validation_error(self, errors):
        self.messages = []
        break_outer = False
        for fieldName, errorMessages in errors:
            for err in errorMessages:
                if err == '* Invalid Email':
                    self.messages.append(
                        'Please enter a valid E-mail address.')
                if err == '* Passwords must match.':
                    self.messages.append(
                        'Please Repeat a matching password.')
                if err == '* Invalid Password':
                    self.messages.append(
                        'Password must contain at least one uppercase, one lowercase and one number character.')
                    break_outer = True
                    break
                if err == '* Required':
                    self.messages.append('Please fill in missing fields.')
                    break_outer = True
                    break
            if break_outer:
                break
        self.flash_messages()

    def communicate(self, details):
        if details == 'doc url':
            self.messages.append('Document URL copied.')
        if details == 'user update':
            self.messages.append('User profile updated.')
        if details == 'customer update':
            self.messages.append('Customer profile updated.')
        self.flash_messages()


message_manager = MessageManager()
