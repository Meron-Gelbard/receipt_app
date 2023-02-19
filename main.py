from datetime import datetime
from sqlalchemy import create_engine, text
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"autoflush": False})

Base = declarative_base()


# CONFIGURE TABLES

class User(db.Model, Base):
    __tablename__ = "users"
    user_id = db.Column(Integer, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    email = db.Column(String(250), nullable=False)
    phone = db.Column(String(20), nullable=True)
    company_name = db.Column(String(250), nullable=False)
    address_id = db.Column(Integer, ForeignKey('addresses.address_id'), nullable=True)
    password = db.Column(String(250), nullable=False)
    create_date = db.Column(Date, nullable=False)
    last_login = db.Column(DateTime, nullable=True)


class Address(db.Model, Base):
    __tablename__ = "addresses"
    address_id = db.Column(Integer, primary_key=True)
    country = db.Column(String(100), nullable=False)
    city = db.Column(String(100), nullable=False)
    address = db.Column(String(300), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.user_id'), nullable=False)


class Document(db.Model, Base):
    __tablename__ = "documents"
    doc_id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id'), nullable=False)
    doc_type = db.Column(String(30), nullable=False)
    doc_date = db.Column(Date, nullable=False)
    subject = db.Column(String(300), nullable=False)
    payment_amount = db.Column(Integer, nullable=False)
    payment_type = db.Column(String(30), nullable=False)
    recipient_id = db.Column(Integer, ForeignKey('recipients.recipient_id'), nullable=False)


class Recipient(db.Model, Base):
    __tablename__ = "recipients"
    recipient_id = db.Column(Integer, primary_key=True)
    name = db.Column(String(300), nullable=False)
    phone = db.Column(String(30), nullable=False)
    address = db.Column(String(300), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # db.create_all()


def create_new_user():
    new_user = User(
        first_name=input('first name:'),
        last_name=input('last name:'),
        email=input('email:'),
        phone=input('phone:'),
        company_name=input('company name:'),
        password=input('set password:'),
        create_date=datetime.now(),
        )
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
        connection = engine.connect()
        result = connection.execute(text('SELECT MAX(user_id) FROM users')).fetchall()
    print(type(result[0][0]))
    user_address = Address(
        user_id=result[0][0],
        country=input('country:'),
        city=input('city:'),
        address=input('address:'),
        )
    with app.app_context():
        db.session.add(user_address)
        db.session.commit()


create_new_user()


