from flask import session
from datetime import datetime
from sqlalchemy import text, exc
from db_architecture import User, Address, Document, Customer
from main import app, db, client_details


def build_database():
    with app.app_context():
        db.create_all()


def drop_database():
    with app.app_context():
        db.session.remove()
        db.drop_all()


def update_user_profile(user_name, update_params):
    with app.app_context():
        user = get_user(user_name=user_name)
        address = get_address(user.id)
        if user:
            for attr, value in update_params['user_params'].items():
                setattr(user, attr, value)
            for attr, value in update_params['address_params'].items():
                setattr(address, attr, value)
            try:
                db.session.commit()
                return True
            except exc.SQLAlchemyError as error:
                return {'error': 'Database Error', 'details': (str(error.__dict__['orig']))}


def update_customer_profile(customer_name, update_params):
    with app.app_context():
        customer = get_customer(name=customer_name)
        if customer:
            for attr, value in update_params.items():
                setattr(customer, attr, value)
            try:
                db.session.commit()
                return True
            except exc.SQLAlchemyError as error:
                return {'error': 'Database Error', 'details': (str(error.__dict__['orig']))}


def register_new_user(**kwargs):
    count = User.query.filter_by(user_name=(kwargs['first_name'] + kwargs['last_name']).lower()).count()
    if count > 0:
        user_name = f"{(kwargs['first_name'] + kwargs['last_name']).lower()}_{str(count)}"
    else:
        user_name = (kwargs['first_name'] + kwargs['last_name']).lower()
    with app.app_context():
        new_user = User(
            first_name=kwargs['first_name'].capitalize(),
            last_name=kwargs['last_name'].capitalize(),
            user_name=user_name,
            email=kwargs['email'],
            phone=kwargs['phone'],
            company_name=kwargs['company_name'],
            password=kwargs['password'],
            website=kwargs['website'],
            doc_count=0,
            create_date=datetime.now(),
            currency=client_details["currency"]["code"],
            last_login=datetime.now())

        db.session.add(new_user)

        user_address = Address(
            country=kwargs['country'],
            city=kwargs['city'],
            address=kwargs['address'],
            user=new_user)
        db.session.add(user_address)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as error:
            return {'error': 'Database Error', 'details': str(error.__dict__['orig'])}

        db.session.execute(text(f"UPDATE users "
                                f"SET address_id={user_address.address_id} WHERE id={user_address.user_id}"))
        db.session.commit()
        session['new_user_name'] = new_user.user_name
        return new_user


def create_document(**kwargs):
    with app.app_context():
        user = get_user(user_id=kwargs['user_id'])
        doc_type_count = Document.query.filter_by(user_id=kwargs['user_id'], doc_type=kwargs['doc_type']).count()
        if 'listed_customer' in kwargs.keys():
            customer_id = Customer.query.filter_by(name=kwargs['listed_customer']).first().customer_id
            new_document = Document(
                user_id=kwargs['user_id'],
                doc_type=kwargs['doc_type'],
                doc_date=datetime.now(),
                subject=kwargs['subject'],
                payment_amount=kwargs['payment_amount'],
                payment_type=kwargs['payment_type'],
                extra_details=kwargs['extra_details'],
                currency=kwargs['currency'],
                customer_id=customer_id,
                doc_serial_num=
                f"{user.user_name}_{kwargs['doc_type'].lower().replace(' ', '')}_{doc_type_count + 1}_{datetime.now().strftime('%d%m%Y')}"
            )
            db.session.add(new_document)
            db.session.commit()

        else:
            new_document = Document(
                user_id=kwargs['user_id'],
                doc_type=kwargs['doc_type'],
                doc_date=datetime.now(),
                subject=kwargs['subject'],
                payment_amount=kwargs['payment_amount'],
                payment_type=kwargs['payment_type'],
                extra_details=kwargs['extra_details'],
                currency=kwargs['currency'],
                doc_serial_num=
                f"{user.user_name}_{kwargs['doc_type'].lower().replace(' ', '')}_{doc_type_count+1}_{datetime.now().strftime('%d%m%Y')}"
            )
            db.session.add(new_document)

            newdoc_customer = Customer(
                name=kwargs['customer_name'],
                phone=kwargs['customer_phone'],
                address=kwargs['customer_address'],
                email=kwargs['customer_email'],
                user_id=kwargs['user_id'])
            db.session.add(newdoc_customer)
            db.session.commit()

            db.session.execute(text(f"UPDATE documents "
                                    f"SET customer_id={newdoc_customer.customer_id} WHERE doc_id={new_document.doc_id}"))
            db.session.commit()
        return new_document.doc_id


def change_user_password(user_name, new_pass_hash):
    with app.app_context():
        user = get_user(user_name=user_name)
        setattr(user, 'password', new_pass_hash)
        try:
            db.session.commit()
            return 'OK'
        except exc.SQLAlchemyError as error:
            return {'error': 'Database Error', 'details': (str(error.__dict__['orig']))}


def get_user(**kwargs):
    try:
        return User.query.filter_by(id=kwargs['user_id']).first()
    except KeyError:
        try:
            return User.query.filter_by(user_name=kwargs['user_name']).first()
        except KeyError:
            return User.query.filter_by(email=kwargs['email']).first()



def get_customer(name):
    return Customer.query.filter_by(name=name).first()


def get_address(user_id):
    return Address.query.filter_by(user_id=user_id).first()


def get_user_attrs(user):
    temp = {**user.get_attrs(), **Address.query.filter_by(user_id=user.id).first().get_attrs()}
    attrs = {}
    field_hierarchy = ['first_name', 'last_name', 'email', 'company_name', 'phone', 'website',
                       'address', 'city', 'country']
    for field in field_hierarchy:
        attrs[field] = temp[field]

    return attrs
