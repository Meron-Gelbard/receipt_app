from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, request, abort, session, url_for
from db_management import get_user, register_new_user, create_document, update_user_profile, User, get_user_attrs
from forms import *
from main import app, db, message_manager
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

# start flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(_id):
    return User.query.filter_by(id=int(_id)).first()


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


@app.route('/<user_name>/dashboard/documents')
@login_required
def user_documents(user_name):
    user = get_user(user_name)
    if user:
        message_manager.clear()
        return render_template('dashboard_docs.html', user=user)
    else:
        return render_template('error_page.html', error='user not found', user=user_name)


@app.route('/<user_name>/dashboard/customers')
@login_required
def user_customers(user_name):
    user = get_user(user_name)
    if user:
        message_manager.clear()
        return render_template('dashboard_customers.html', user=user)
    else:
        return render_template('error_page.html', error='user not found', user=user_name)


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
                address=form.address.data)
            user_name = (form.first_name.data + form.last_name.data).lower()
            if isinstance(response, User):
                user_2_login = User.query.filter_by(user_name=user_name).first()
                login_user(user_2_login, remember=True, duration=timedelta(minutes=30))
                return redirect(f'/{user_name}/dashboard/documents')
            elif response['error'] == 'Database Error':
                message_manager.database_error(response['details'])
        message_manager.form_validation_error(form.errors.items())
        return render_template("register_new.html", form=form)


# @app.route('/<user_name>/profile/edit', methods=["POST", "GET"])
# @login_required
# def user_profile_edit(user_name):
#     """Receives a user profile page call with the 'Edit' parameter set to True/False
#     in order to redirect to profile page with correct state without 'Edit'
#     parameter appearing in url"""
#
#     edit = request.args.get('edit')
#     session['edit'] = edit
#     return redirect(url_for('user_profile', user_name=user_name))


@app.route('/<user_name>/profile', methods=["POST", "GET"])
@login_required
def user_profile(user_name):
    edit = request.args.get('edit')
    user = get_user(user_name)
    form = UpdateUserForm()
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

                if updated_response is None:
                    edit = False
                    user = get_user(update_params['user_params']['user_name'])
                    user_attrs = get_user_attrs(user)
                    return redirect(f'/{user.user_name}/profile')
                elif updated_response['error'] == 'Database Error':
                    message_manager.database_error(updated_response['details'])
                    return render_template("user_profile.html", form=form, user=user, edit=edit, user_attrs=user_attrs)
                # elif user_updated['error'] == 'user error':
                #     message_manager.login_messages(user_updated['details'])
            else:
                message_manager.form_validation_error(form.errors.items())
                edit = True
                return render_template("user_profile.html", form=form, user=user, edit=edit, user_attrs=user_attrs)
    return render_template("user_profile.html", form=form, user=user, edit=edit, user_attrs=user_attrs)


@app.route('/<user_name>/dashboard/create_document', methods=["POST", "GET"])
@login_required
def new_document(user_name):
    message_manager.clear()
    form = NewDocumentForm()
    user = get_user(user_name)
    if form.validate_on_submit():
        create_document(
            user_id=user.id,
            doc_type=form.doc_type.data,
            subject=form.subject.data,
            payment_amount=int(form.payment_amount.data),
            payment_type=form.payment_type.data,
            recipient_name=form.recipient_name.data,
            recipient_phone=form.recipient_phone.data,
            recipient_address=form.recipient_address.data,
            recipient_email=form.recipient_email.data)

        user.doc_count += 1
        db.session.commit()
        return redirect(f'/{user_name}/dashboard/documents')
    message_manager.form_validation_error(form.errors.items())
    return render_template("dashboard_create.html", form=form, user=user, logged_in=logged_check())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
