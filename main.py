
from sqlalchemy import create_engine, text, update
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# hash these later...
SECRET = '1111'
DB_HOST_NAME = 'localhost'
DB_NAME = 'receipt_app1'
DB_USERN = 'postgres'
# make env variable later...
SQLALCHEMY_DB_URI = f'postgresql+psycopg2://{DB_USERN}:{SECRET}@{DB_HOST_NAME}/{DB_NAME}'

engine = create_engine(SQLALCHEMY_DB_URI)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"autoflush": False})


# TODO - build form error management with flash messages
# TODO - add defaults to selection fields
# TODO - choose from past recipients on doc creation
# TODO - create login system
# TODO - add currency selection
# TODO - add more restriction on user and document forms
# TODO - autopopulate form when known recipient found (even cross users)
