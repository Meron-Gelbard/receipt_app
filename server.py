from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, request, abort, session, url_for
from email_manager import EmailManager
from db_management import *
from forms import *
from main import app, db, message_manager
from pdf_document import DocPdf
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyperclip
import uuid
import os

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
    if logged_check():
        return redirect('/')
    session['new_doc'] = False
    with app.app_context():
        form = LoginForm()
        if form.validate_on_submit():
            user_2_login = User.query.filter_by(email=form.email.data.lower()).first()
            if not user_2_login:
                message_manager.clear()
                message_manager.communicate('User not found, Please try again')
                return render_template("login.html", form=form)
            elif user_2_login:
                password_ok = check_password_hash(pwhash=user_2_login.password, password=form.password.data)
                if not password_ok:
                    message_manager.clear()
                    message_manager.communicate('Wrong Password. Please try again.')
                    return render_template("login.html", form=form)
                elif password_ok:
                    if user_2_login.email_confirmed:
                        login_user(user_2_login, remember=False)
                        session['user_last_log'] = user_2_login.last_login.strftime("%d.%m.%y | %H:%M")
                        user_2_login.last_login = datetime.now()
                        db.session.commit()

                        # source url checker
                        _next = request.args.get('next')
                        if not is_safe_url(_next):
                            return abort(400)

                        message_manager.clear()
                        message_manager.communicate('Logged in successfully.')
                        return redirect(f'/{user_2_login.user_name}/dashboard/documents')
                    else:
                        message_manager.clear()
                        message_manager.communicate(f'Please confirm E-mail address. '
                                                    f'Confirmation link sent to {user_2_login.email}.')
                        return render_template("login.html", form=form)
        message_manager.form_validation_error(form.errors.items())
        return render_template("login.html", form=form)


@app.route('/<user_name>/dashboard/documents', methods=["POST", "GET"])
@login_required
def user_documents(user_name):
    new_doc = session.get('new_doc')
    session['new_doc'] = None
    user = get_user(user_name=user_name)
    user.doc_count = Document.query.filter_by(user_id=user.id).count()
    db.session.commit()
    return render_template('dashboard_docs.html', user=user, new_doc=new_doc, doc_url=copy_doc_url)


@app.route('/copy_doc_url')
@login_required
def copy_doc_url():
    message_manager.clear()
    serial = request.args['serial']
    user_name = request.args['user']
    host = request.url_root
    doc_local_url = f'{host}{user_name}/doc_preview/{serial}'
    pyperclip.copy(doc_local_url)
    message_manager.communicate('Document URL copied.')
    return redirect(f'/{user_name}/dashboard/documents')


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
                email=form.email.data.lower(),
                phone=form.phone.data,
                company_name=form.company_name.data,
                password=hashed_password,
                country=form.country.data,
                city=form.city.data,
                address=form.address.data,
                website=form.website.data)
            if isinstance(response, User):
                user_name = session.get('new_user_name')
                del session['new_user_name']
                session[f'uuid_{user_name}'] = uuid.uuid4()
                new_user = User.query.filter_by(user_name=user_name).first()
                EmailManager.send_email_confirm(name=f'{new_user.first_name} {new_user.last_name}', user_name=user_name,
                                                email=new_user.email, uuid=session[f'uuid_{user_name}'])
                message_manager.clear()
                message_manager.communicate(f'Email confirmation sent to {new_user.email}.')
                return redirect(f'/login')
            elif response['error'] == 'Database Error':
                message_manager.clear()
                message_manager.database_error(response['details'])
        message_manager.form_validation_error(form.errors.items())
        return render_template("register.html", form=form)


@app.route('/email_confirm/<user_name>/<sent_uuid>')
def email_confirm(user_name, sent_uuid):
    with app.app_context():
        if not session.get(f'uuid_{user_name}'):
            message_manager.communicate('Confirmation token expired.')
            return redirect('/login')
        if sent_uuid == str(session[f'uuid_{user_name}']):
            if request.args.get('subject') == 'email confirm':
                del session[f'uuid_{user_name}']
                confirmed_user = get_user(user_name=user_name)
                confirmed_user.email_confirmed = True
                db.session.commit()
                message_manager.clear()
                message_manager.communicate('Email address confirmed!')
                return redirect('/login')
            elif request.args.get('subject') == 'password recover':
                return redirect(url_for('password_renew', user_name=user_name, sent_uuid=sent_uuid))
        else:
            return abort(404)


@app.route('/password_recovery', methods=['POST', 'GET'])
def password_recovery():
    form = EmailFieldForm()
    with app.app_context():
        if form.validate_on_submit():
            user_2_recover = get_user(email=form.email.data)
            if isinstance(user_2_recover, User):
                session[f'uuid_{user_2_recover.user_name}'] = uuid.uuid4()
                EmailManager.send_pass_recover(name=f'{user_2_recover.first_name} {user_2_recover.last_name}',
                                               user_name=user_2_recover.user_name, email=user_2_recover.email,
                                               uuid=session[f'uuid_{user_2_recover.user_name}'])
                message_manager.clear()
                message_manager.communicate(f'Password recovery link sent to {user_2_recover.email}.')
                return redirect(f'/login')
            else:
                message_manager.communicate('User not found, Please try again')
                return render_template("recover_password.html", form=form)
        message_manager.form_validation_error(form.errors.items())
        return render_template("recover_password.html", form=form)


@app.route('/<user_name>/password_renew', methods=['POST', 'GET'])
def password_renew(user_name):
    if request.args.get('sent_uuid') == str(session[f'uuid_{user_name}']):
        sent_uuid = request.args.get('sent_uuid')
        with app.app_context():
            user = get_user(user_name=user_name)
            form = RenewPasswordForm()
            if form.validate_on_submit():
                new_pass_hash = generate_password_hash(password=form.new_pass.data,
                                                       method='pbkdf2:sha256', salt_length=8)
                response = change_user_password(user_name, new_pass_hash)
                if response == 'OK':
                    message_manager.communicate('Password changed successfully.')
                    del session[f'uuid_{user_name}']
                    return redirect(f'/login')
                else:
                    message_manager.database_error(response)
                    return redirect(url_for('password_renew', user_name=user_name, sent_uuid=sent_uuid))
            return render_template('renew_password.html', form=form, user=user, sent_uuid=sent_uuid)
    else:
        return abort(404)


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
                    message_manager.clear()
                    message_manager.communicate('User profile updated.')
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


@app.route('/<user_name>/change_password', methods=['GET', 'POST'])
@login_required
def change_password(user_name):
    with app.app_context():
        message_manager.clear()
        user = get_user(user_name=user_name)
        form = ChangePasswordForm()
        if form.validate_on_submit():
            current_pass_ok = check_password_hash(pwhash=user.password, password=form.current_pass.data)
            if current_pass_ok:
                new_pass_hash = generate_password_hash(password=form.new_pass.data,
                                                       method='pbkdf2:sha256', salt_length=8)
                response = change_user_password(user_name, new_pass_hash)
                if response == 'OK':
                    message_manager.communicate('Password changed successfully.')
                    return redirect(f'/{user.user_name}/profile')
                else:
                    message_manager.database_error(response)
                    return render_template('change_password.html', form=form, user=user)
            else:
                message_manager.communicate('Wrong Password. Please try again.')
                render_template('change_password.html', form=form, user=user)

        message_manager.form_validation_error(form.errors.items())
        return render_template('change_password.html', form=form, user=user)


@app.route('/<user_name>/customers/<customer>', methods=["POST", "GET"])
@login_required
def customer_profile(user_name, customer):
    edit = request.args.get('edit')
    user = get_user(user_name=user_name)
    form = UpdateCustomerForm()
    customer = get_customer(customer)
    customer_attrs = customer.get_attrs()
    doc_count = Document.query.filter_by(user_id=user.id, customer_id=customer.customer_id).count()
    with app.app_context():
        if edit:
            if form.validate_on_submit():
                update_params = {'name': form.name.data,
                                 'email': form.email.data,
                                 'phone': form.phone.data,
                                 'address': form.address.data}

                updated_response = update_customer_profile(customer.name, update_params)

                if updated_response:
                    customer = get_customer(update_params['name'])
                    message_manager.clear()
                    message_manager.communicate('Customer profile updated.')
                    return redirect(f'/{user.user_name}/customers/{customer.name}')

                elif updated_response['error'] == 'Database Error':
                    return render_template("customer_profile.html", form=form, user=user, edit=True,
                                           customer_attrs=customer_attrs, customer=customer, doc_count=doc_count)
            else:
                message_manager.form_validation_error(form.errors.items())
                return render_template("customer_profile.html", form=form, user=user, edit=True,
                                       customer_attrs=customer_attrs, customer=customer, doc_count=doc_count)
    return render_template("customer_profile.html", form=form, user=user, customer=customer,
                           customer_attrs=customer_attrs,  doc_count=doc_count)


@app.route('/<user_name>/dashboard/create_document', methods=["POST", "GET"])
@login_required
def new_document(user_name):
    message_manager.clear()
    checkbox = request.args.get('checkbox')
    form = NewDocumentForm.create(checkbox=checkbox)
    form.currency.render_kw = {'value': form.currency.default}
    user = get_user(user_name=user_name)
    if request.args.get('selection'):
        form.doc_type.data = request.args.get('selection')
    if form.validate_on_submit():
        if checkbox == 'true':
            new_doc_id = create_document(
                user_id=user.id,
                doc_type=form.doc_type.data,
                subject=form.subject.data,
                payment_amount=int(form.payment_amount.data),
                currency=form.currency.data.split(' ')[-3],
                payment_type=form.payment_type.data,
                extra_details=form.extra_details.data,
                listed_customer=form.listed_customers.data)
        else:
            new_doc_id = create_document(
                user_id=user.id,
                doc_type=form.doc_type.data,
                subject=form.subject.data,
                payment_amount=int(form.payment_amount.data),
                currency=form.currency.data.split(' ')[-3],
                payment_type=form.payment_type.data,
                extra_details=form.extra_details.data,
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


@app.route('/<user_name>/upload_logo', methods=['GET', 'POST'])
@login_required
def upload_logo(user_name):
    message_manager.clear()
    with app.app_context():
        user = get_user(user_name=user_name)
        logo_path = f'static/assets/img/users/{user_name}'
        if not os.path.exists(logo_path):
            os.mkdir(logo_path)
        if request.method == 'POST':
            file = request.files['file']
            file.save(f'{logo_path}/logo.png')
            user.logo = f'/{logo_path}/logo.png'
            db.session.commit()
            message_manager.communicate('Logo upload successful.')
            return redirect(url_for('user_profile', user_name=user_name))
        message_manager.communicate('File upload failed.')
        return redirect(url_for('user_profile', user_name=user_name))


@app.route('/<user_name>/remove_logo')
@login_required
def remove_logo(user_name):
    message_manager.clear()
    with app.app_context():
        user = get_user(user_name=user_name)
        user.logo = '/static/assets/img/default_logo.png'
        db.session.commit()
    message_manager.communicate('Logo removed.')
    return redirect(url_for('user_profile', user_name=user_name))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
