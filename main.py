from datetime import datetime
from sqlalchemy import create_engine, text, update
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime, event, delete
from sqlalchemy.orm import relationship, Mapped
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
    user_id: Mapped[int] = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    phone = Column(String(20), nullable=True, unique=True)
    company_name = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    create_date = Column(Date, nullable=False)
    last_login = Column(DateTime, nullable=True)
    address = relationship("Address", back_populates="user", cascade="all, delete", passive_deletes=True)
    address_id = Column(Integer)

class Address(db.Model, Base):
    __tablename__ = "addresses"
    address_id: Mapped[int] = Column(Integer, primary_key=True)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(300), nullable=False, unique=True)
    user = relationship("User", back_populates="address")
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"))


class Document(db.Model, Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True)
    doc_type = Column(String(30), nullable=False)
    doc_date = Column(Date, nullable=False)
    subject = Column(String(300), nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_type = Column(String(30), nullable=False)
    recipient_id = Column(Integer, ForeignKey('recipients.recipient_id'))
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)


class Recipient(db.Model, Base):
    __tablename__ = "recipients"
    recipient_id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    phone = Column(String(30), nullable=False)
    address = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))


def build_database():
    with app.app_context():
        db.create_all()

def drop_database():
    with app.app_context():
        db.session.remove()
        db.drop_all()


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

        user_address = Address(
            country=input('country:'),
            city=input('city:'),
            address=input('address:'),
            user=new_user
            )

        db.session.add(user_address)
        db.session.commit()
        db.session.execute(text(f"UPDATE users "
                                f"SET address_id={user_address.address_id} "
                                f"WHERE user_id={user_address.user_id}"))
        db.session.commit()

def create_document():
    user = int(input('document user:'))
    new_document = Document(
        user_id=user,
        doc_type=input('document type:'),
        doc_date=datetime.now(),
        subject=input('document subject:'),
        payment_amount=int(input('payment amount(int):')),
        payment_type=input('payment type:'))

    with app.app_context():
        db.session.add(new_document)

        newdoc_recipient = Recipient(
            name=input('recipient name:'),
            phone=input('recipient phone:'),
            address=input('recipient address:'),
            user_id=user)

        db.session.add(newdoc_recipient)
        db.session.commit()
        db.session.execute(text(f"UPDATE documents "
                                f"SET recipient_id={newdoc_recipient.recipient_id} "
                                f"WHERE doc_id={new_document.doc_id}"))
        db.session.commit()


create_document()




