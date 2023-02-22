from flask import render_template, redirect
from db_management import get_user, register_new_user, create_document
from forms import *
from main import app, db


@app.route('/<user_name>/details')
def user_details(user_name):
    user = get_user(user_name)
    return render_template('user_details.html', user=user)


@app.route('/<user_name>/documents')
def user_documents(user_name):
    user = get_user(user_name)
    return render_template('user_documents.html', user=user)


@app.route('/register', methods=["POST", "GET"])
def register_user():
    form = RegisterUserForm()
    if form.validate_on_submit():
        register_new_user(
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

        return redirect(f'/{user_name}/details')
    else:
        # flash("User Email does not exist. Please try again.")
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
    else:
        return render_template("new_document.html", form=form, user=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
