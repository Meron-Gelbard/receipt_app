from datetime import datetime
from sqlalchemy import text
from db_architecture import User, Address, Document, Recipient
from main import app, db


def build_database():
    with app.app_context():
        db.create_all()


def drop_database():
    with app.app_context():
        db.session.remove()
        db.drop_all()


def register_new_user(**kwargs):
    with app.app_context():
        new_user = User(
            first_name=kwargs['first_name'],
            last_name=kwargs['last_name'],
            user_name=(kwargs['first_name'] + kwargs['last_name']).lower(),
            email=kwargs['email'],
            phone=kwargs['phone'],
            company_name=kwargs['company_name'],
            password=kwargs['password'],
            doc_count=0,
            create_date=datetime.now())

        db.session.add(new_user)

        user_address = Address(
            country=kwargs['country'],
            city=kwargs['city'],
            address=kwargs['address'],
            user=new_user)

        db.session.add(user_address)
        db.session.commit()
        db.session.execute(text(f"UPDATE users "
                                f"SET address_id={user_address.address_id} "
                                f"WHERE user_id={user_address.user_id}"))
        db.session.commit()


def create_document(**kwargs):
    with app.app_context():
        new_document = Document(
            user_id=kwargs['user_id'],
            doc_type=kwargs['doc_type'],
            doc_date=datetime.now(),
            subject=kwargs['subject'],
            payment_amount=kwargs['payment_amount'],
            payment_type=kwargs['payment_type'])

        db.session.add(new_document)

        newdoc_recipient = Recipient(
            name=kwargs['recipient_name'],
            phone=kwargs['recipient_phone'],
            address=kwargs['recipient_address'],
            email=kwargs['recipient_email'],
            user_id=kwargs['user_id'])

        db.session.add(newdoc_recipient)
        db.session.commit()
        db.session.execute(text(f"UPDATE documents "
                                f"SET recipient_id={newdoc_recipient.recipient_id} "
                                f"WHERE doc_id={new_document.doc_id}"))
        db.session.commit()


def get_user(user_name):
    return User.query.filter_by(user_name=user_name).first()



