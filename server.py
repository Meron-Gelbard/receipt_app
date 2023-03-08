from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, request, abort, session, url_for, Response
from db_architecture import Document, User
from db_management import get_user, get_customer, register_new_user, create_document, \
    update_user_profile, get_user_attrs, update_customer_profile
from forms import *
from main import app, db, message_manager
from pdf_document import DocPdf
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyperclip
from sqlalchemy import func


# start flask-login
login_manager = LoginManager()
login_manager.init_app(app)


def logged_check():
    with app.app_context():
        if current_user.is_authenticated:
            return True
        else:
            return False


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(_id):
    return User.query.filter_by(id=int(_id)).first()


@app.route('/')
def home_redirect():
    if logged_check():
        user_name = current_user.user_name
        message_manager.clear()
        return redirect(f'{user_name}/dashboard/documents')
    else:
        return redirect(f'/login')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    message_manager.clear()
    return redirect('/login')


@app.route('/login', methods=["POST", "GET"])
def login():
    session['new_doc'] = False
    message_manager.clear()
    with app.app_context():
        form = LoginForm()
        if form.validate_on_submit():
            user_2_login = User.query.filter_by(email=form.email.data).first()
            if not user_2_login:
                message_manager.login_messages('user not found')
                return render_template("login_new.html", form=form)
            elif user_2_login:
                password_ok = check_password_hash(pwhash=user_2_login.password, password=form.password.data)
                if not password_ok:
                    message_manager.login_messages('pass error')
                    return render_template("login_new.html", form=form)
                elif password_ok:
                    login_user(user_2_login, remember=False)
                    session['user_last_log'] = user_2_login.last_login.strftime("%d/%m/%Y  |  %H:%M")
                    user_2_login.last_login = datetime.now()
                    db.session.commit()

                    # source url checker
                    _next = request.args.get('next')
                    if not is_safe_url(_next):
                        return abort(400)

                    message_manager.clear()
                    return redirect(f'/{user_2_login.user_name}/dashboard/documents')
        message_manager.form_validation_error(form.errors.items())
        return render_template("login_new.html", form=form)


@app.route('/<user_name>/dashboard/documents', methods=["POST", "GET"])
@login_required
def user_documents(user_name):
    new_doc = session.get('new_doc')
    session['new_doc'] = None
    user = get_user(user_name=user_name)
    user.doc_count = Document.query.filter_by(user_id=user.id).count()
    db.session.commit()
    message_manager.clear()
    return render_template('dashboard_docs.html', user=user, new_doc=new_doc, doc_url=copy_doc_url)


@app.route('/copy_doc_url')
@login_required
def copy_doc_url():
    serial = request.args['serial']
    user_name = request.args['user']
    host = request.url_root
    doc_local_url = f'{host}{user_name}/doc_preview/{serial}'
    pyperclip.copy(doc_local_url)
    return Response(status=204)


@app.route('/<user_name>/dashboard/customers')
@login_required
def user_customers(user_name):
    user = get_user(user_name=user_name)
    message_manager.clear()
    return render_template('dashboard_customers.html', user=user)


@app.route('/register', methods=["POST", "GET"])
def register_user():
    with app.app_context():
        form = RegisterUserForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
            response = register_new_user(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company_name=form.company_name.data,
                password=hashed_password,
                country=form.country.data,
                city=form.city.data,
                address=form.address.data,
                website=form.website.data)
            user_name = (form.first_name.data + form.last_name.data).lower()
            if isinstance(response, User):
                user_2_login = User.query.filter_by(user_name=user_name).first()
                login_user(user_2_login, remember=False)
                session['user_last_log'] = datetime.now().strftime("%d/%m/%Y  |  %H:%M")
                return redirect(f'/{user_name}/dashboard/documents')
            elif response['error'] == 'Database Error':
                message_manager.database_error(response['details'])
        message_manager.form_validation_error(form.errors.items())
        return render_template("register_new.html", form=form)


@app.route('/<user_name>/profile', methods=["POST", "GET"])
@login_required
def user_profile(user_name):
    edit = request.args.get('edit')
    edit_currency = request.args.get('edit_currency')
    user = get_user(user_name=user_name)
    form = UpdateUserForm()
    form_c = ChangeCurrencyFrom()
    user_attrs = get_user_attrs(user)
    with app.app_context():
        if edit:
            if form.validate_on_submit():
                update_params = {
                    'user_params':
                        {"first_name": form.first_name.data,
                         "last_name": form.last_name.data,
                         "email": form.email.data,
                         "phone": form.phone.data,
                         "company_name": form.company_name.data,
                         "user_name": f'{form.first_name.data.lower()}{form.last_name.data.lower()}'},
                    'address_params':
                        {"country": form.country.data,
                         "city": form.city.data,
                         "address": form.address.data}
                    }

                updated_response = update_user_profile(user_name, update_params)

                if updated_response:
                    user = get_user(user_name=update_params['user_params']['user_name'])
                    return redirect(f'/{user.user_name}/profile')
                elif updated_response['error'] == 'Database Error':
                    message_manager.database_error(updated_response['details'])
                    return render_template("user_profile.html", form=form, user=user, edit=True, user_attrs=user_attrs)
            else:
                message_manager.form_validation_error(form.errors.items())
                return render_template("user_profile.html", form=form, user=user, edit=True, user_attrs=user_attrs)
        if edit_currency:
            if form_c.validate_on_submit():
                user = get_user(user_name=user_name)
                user.currency = form_c.currency.data.split(' ')[-3]
                db.session.commit()
                return render_template("user_profile.html", form=form, user=user,
                                       last_log=session['user_last_log'], user_attrs=user_attrs, currency=user.currency)
            return render_template("user_profile.html", form=form, form_c=form_c, user=user,
                                   last_log=session['user_last_log'], edit_currency=True, user_attrs=user_attrs)
    return render_template("user_profile.html", form=form, user=user,
                           user_attrs=user_attrs, last_log=session['user_last_log'],
                           currency=user.currency)


@app.route('/<user_name>/customers/<customer>', methods=["POST", "GET"])
@login_required
def customer_profile(user_name, customer):
    edit = request.args.get('edit')
    user = get_user(user_name=user_name)
    form = UpdateCustomerForm()
    customer = get_customer(customer)
    customer_attrs = customer.get_attrs()
    with app.app_context():
        if edit:
            if form.validate_on_submit():
                update_params = {'name': form.name.data,
                                 'email': form.email.data,
                                 'phone': form.phone.data,
                                 'address': form.address.data}

                updated_response = update_customer_profile(customer, update_params)

                if updated_response:
                    customer = get_customer(update_params['name'])
                    return redirect(f'/{user.user_name}/{customer.name}')
                elif updated_response['error'] == 'Database Error':
                    return render_template("customer_profile.html", form=form, user=user, edit=True,
                                           customer_attrs=customer_attrs, customer=customer)
            else:
                message_manager.form_validation_error(form.errors.items())
                return render_template("customer_profile.html", form=form, user=user, edit=True,
                                       customer_attrs=customer_attrs, customer=customer)
    return render_template("customer_profile.html", form=form, user=user, customer=customer,
                           customer_attrs=customer_attrs)


@app.route('/<user_name>/dashboard/create_document', methods=["POST", "GET"])
@login_required
def new_document(user_name):
    message_manager.clear()
    checkbox = request.args.get('checkbox')
    form = NewDocumentForm.create(checkbox=checkbox)
    user = get_user(user_name=user_name)
    if form.validate_on_submit():
        if checkbox == 'true':
            new_doc_id = create_document(
                user_id=user.id,
                doc_type=form.doc_type.data,
                subject=form.subject.data,
                payment_amount=int(form.payment_amount.data),
                payment_type=form.payment_type.data,
                listed_customer=form.listed_customers.data)
        else:
            new_doc_id = create_document(
                user_id=user.id,
                doc_type=form.doc_type.data,
                subject=form.subject.data,
                payment_amount=int(form.payment_amount.data),
                payment_type=form.payment_type.data,
                customer_name=form.customer_name.data,
                customer_phone=form.customer_phone.data,
                customer_address=form.customer_address.data,
                customer_email=form.customer_email.data)

        session['new_doc'] = Document.query.filter_by(doc_id=new_doc_id).first().doc_serial_num
        return redirect(url_for('user_documents', user_name=user_name))
    message_manager.form_validation_error(form.errors.items())
    return render_template("dashboard_create.html", form=form, user=user, checkbox=checkbox)


@app.route('/<user_name>/doc_preview/<doc_serial>', methods=["POST", "GET"])
def view_doc_pdf(user_name, **kwargs):
    user = get_user(user_name=user_name)
    doc = Document.query.filter_by(doc_serial_num=kwargs['doc_serial']).first()
    doc_pdf = DocPdf(user=user, document=doc)
    return doc_pdf.response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
