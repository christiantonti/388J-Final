from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateProfilePicForm, UpdateAccountForm, ResetPasswordForm
from ..models import PointLog, User
from ..utils import get_status, get_points, get_b64_img

users = Blueprint("users", __name__)

""" ************ User Management views ************ """

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("functions.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # create user
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            uid=form.uid.data, 
            email=form.email.data, 
            phone=form.phone.data,
            password=hashed,
            fname=form.fname.data,
            lname=form.lname.data,
            isAdmin=False
        )
        user.save()
        # create initial points at 100
        points = PointLog(
            user=user,
            points=100,
            reason="Initial Points"
        )
        points.save()
        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("functions.index"))

    form = LoginForm()
    print(list(form))
    if form.validate_on_submit():
        user = User.objects(uid=form.uid.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("functions.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    uform = UpdateAccountForm()
    pform = UpdateProfilePicForm()
    rform = ResetPasswordForm()

    if uform.validate_on_submit():
        current_user.modify(
            email=uform.email.data,
            phone=uform.phone.data,
            fname=uform.fname.data,
            lname=uform.lname.data
        )
        current_user.save()
        return redirect(url_for("users.account"))
    
    if pform.validate_on_submit():
        img = pform.pfp.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'
        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type=content_type)
        else:
            current_user.profile_pic.replace(img.stream, content_type=content_type)
        current_user.save()
        return redirect(url_for('users.account'))

    if rform.validate_on_submit():
        hashed = bcrypt.generate_password_hash(rform.password.data).decode("utf-8")
        current_user.modify(password=hashed)
        current_user.save()
        return redirect(url_for("users.account"))

    # pre-populate form
    uform.email.data = current_user.email
    uform.phone.data = current_user.phone
    uform.fname.data = current_user.fname
    uform.lname.data = current_user.lname

    points = get_points(current_user)
    log = PointLog.objects(user=current_user).order_by('-date')
    return render_template(
        "account.html",
        title="Account",
        points=points,
        log=log,
        status=get_status(points),
        uform=uform,
        pform=pform,
        rform=rform,
        image=get_b64_img(current_user.uid)
    )