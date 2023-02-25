from flask import render_template, redirect, flash
from db_management import get_user, register_new_user, create_document, User
from forms import *
from main import app, db, message_manager
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# initiate flask-login
login_manager = LoginManager()
login_manager.init_app(app)


def flash_messages():
    for msg in message_manager.messages:
        flash(msg)

@login_manager.user_loader
def load_user(user_name):
    return User.query.filter_by(user_name=user_name).first()


def logged_check():
    if current_user.is_authenticated:
        return True
    else:
        return False


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@app.route('/')
def home_redirect():
    return redirect(f'/register')

@app.route('/<user_name>/details')
def user_details(user_name):
    user = get_user(user_name)
    if user:
        return render_template('user_details.html', user=user)
    else:
        return render_template('error_page.html', error='user not found', user=user_name)


@app.route('/<user_name>/documents')
def user_documents(user_name):
    user = get_user(user_name)
    if user:
        return render_template('user_documents.html', user=user)
    else:
        return render_template('error_page.html', error='user not found', user=user_name)

@app.route('/register', methods=["POST", "GET"])
def register_user():
    form = RegisterUserForm()
    if form.validate_on_submit():
        response = register_new_user(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            company_name=form.company_name.data,
            password=form.password.data,
            country=form.country.data,
            city=form.city.data,
            address=form.address.data)
        user_name = (form.first_name.data + form.last_name.data).lower()
        if response == 'OK':
            return redirect(f'/{user_name}/details')
        if response['error'] == 'Database Error':
            message_manager.database_error(response['details'])
            flash_messages()
    message_manager.form_validation_error(form.errors.items())
    flash_messages()
    return render_template("register_user.html", form=form)


@app.route('/<user_name>/new_document', methods=["POST", "GET"])
def new_document(user_name):
    form = NewDocumentForm()
    user = get_user(user_name)
    if form.validate_on_submit():
        create_document(
            user_id=user.user_id,
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
        # Change later to redirect to the new document page!!
        return redirect(f'/{user_name}/documents')
    message_manager.form_validation_error(form.errors.items())
    flash_messages()
    return render_template("new_document.html", form=form, user=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
