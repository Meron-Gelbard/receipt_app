from sqlalchemy import create_engine
from flask import Flask, flash, session
from flask_sqlalchemy import SQLAlchemy
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv('SECRET')
DB_HOST_NAME = os.getenv('DB_HOST_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_USERN = os.getenv('DB_USERN')
APP_KEY = os.getenv('APP_KEY')
SMTP_CONFIG = {'smtp_server': os.getenv('smtp_server'),
               'smtp_port': os.getenv('smtp_port'),
               'smtp_username': os.getenv('smtp_username'),
               'smtp_password': os.getenv('smtp_password')}

SQLALCHEMY_DB_URI = f'postgresql+psycopg2://{DB_USERN}:{SECRET}@{DB_HOST_NAME}/{DB_NAME}'
api_key = os.getenv('api_key')

try:
    client_details = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}').json()
except Exception:
    client_details = None

engine = create_engine(SQLALCHEMY_DB_URI)

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"autoflush": False})


class MessageManager:
    def __init__(self):
        self.messages = []

    def clear(self):
        if session.get('_flashes'):
            session['_flashes'].clear()
        self.messages = []
        # self.flash_messages()

    def flash_messages(self):
        for msg in self.messages:
            flash(msg)

    def database_error(self, details):
        self.clear()
        if 'user_name' in details:
            self.messages.append('This user name already exists.')
        elif 'email' in details:
            self.messages.append('This E-Mail address is already in use.')
        elif 'phone' in details:
            self.messages.append('This phone number is already in use.')
        elif 'company_name' in details:
            self.messages.append('This company name is already in use. One account per company allowed.')
        self.flash_messages()

    def form_validation_error(self, errors):
        self.clear()
        break_outer = False
        for fieldName, errorMessages in errors:
            for err in errorMessages:
                if err == '* Invalid Email':
                    self.messages.append('Please enter a valid E-mail address.')
                if err == '* Passwords must match.':
                    self.messages.append('Please Repeat a matching password.')
                if err == '* Invalid Password':
                    self.messages.append('Password must contain one uppercase, one lowercase and one number.')
                    break_outer = True
                    break
                if err == '* Required':
                    self.messages.append('Please fill in missing fields.')
                    break_outer = True
                    break
            if break_outer:
                break
        self.flash_messages()

    def communicate(self, message):
        self.clear()
        self.messages.append(message)
        self.flash_messages()


message_manager = MessageManager()
