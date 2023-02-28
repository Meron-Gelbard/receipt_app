from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import relationship, Mapped, declarative_base
from main import db
from flask_login import UserMixin

Base = declarative_base()


# CONFIGURE TABLES
class User(UserMixin, db.Model, Base):
    __tablename__ = "users"
    id: Mapped[int] = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    user_name = Column(String(100), nullable=False, unique=True)
    email = Column(String(250), nullable=False, unique=True)
    phone = Column(String(20), nullable=True, unique=True)
    company_name = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    create_date = Column(Date, nullable=False)
    last_login = Column(DateTime, nullable=True)
    address = relationship("Address", back_populates="user", cascade="all, delete", passive_deletes=True)
    address_id = Column(Integer, nullable=True)
    documents = relationship('Document', backref='user', cascade="all, delete", passive_deletes=True)
    recipients = relationship('Recipient', backref='user', cascade="all, delete", passive_deletes=True)
    doc_count = Column(Integer, nullable=False)

    def get_user_attrs(self):
        user_attrs = {}
        for key, value in vars(self).items():
            if key not in ['id', 'password', 'address_id', 'documents', 'recipients',
                           'get_user_attrs', 'get_id', '_sa_instance_state']:
                user_attrs[key] = value
        return user_attrs

    def get_id(self):
        return self.id


class Address(db.Model, Base):
    __tablename__ = "addresses"
    address_id: Mapped[int] = Column(Integer, primary_key=True)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(300), nullable=False, unique=True)
    user = relationship("User", back_populates="address")
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))


class Document(db.Model, Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True)
    doc_type = Column(String(30), nullable=False)
    doc_date = Column(Date, nullable=False)
    subject = Column(String(300), nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_type = Column(String(30), nullable=False)
    recipient_id = Column(Integer, ForeignKey('recipients.recipient_id'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient = relationship('Recipient', backref='recipient')


class Recipient(db.Model, Base):
    __tablename__ = "recipients"
    recipient_id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    phone = Column(String(30), nullable=False)
    address = Column(String(300), nullable=False)
    email = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
