from flask import Blueprint, render_template, redirect, url_for, flash
from extra.forms import LoginForm, ChangePasswordForm
from extra.models import User
from extra.extensions import db, flask_bcrypt
from flask_login import login_user, logout_user, login_required, current_user

authentication = Blueprint("authentication", __name__)


@authentication.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    user = db.session.query(User).filter_by(
        username=form.username.data).first()
    if user:
        if flask_bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("index.main"))
        else:
            flash("Invalid username or password")
    return render_template("login.html", form=form)


@authentication.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))


@authentication.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        condition1 = flask_bcrypt.check_password_hash(current_user.password,
                                                      form.old_password.data)
        if condition1:
            new_password_hash = flask_bcrypt.generate_password_hash(
                form.new_password1.data).decode("utf-8")
            db.session.query(User).filter_by(
                username=current_user.username).update(
                    dict(password=new_password_hash))
            db.session.commit()
            return redirect(url_for("index.main"))
        else:
            flash("Old password is incorrect")
    return render_template("change_password.html", form=form)
