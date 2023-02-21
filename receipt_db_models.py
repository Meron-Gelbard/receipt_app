
from sqlalchemy import Column, Integer, ForeignKey, String, Date, DateTime, event, delete
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import declarative_base

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

