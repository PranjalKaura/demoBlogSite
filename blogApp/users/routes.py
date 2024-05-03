from blogApp.models import User, Post
from blogApp.users.forms import (RegisterationForm, LoginForm, UpdateAccountForm, 
                           RequestResetForm, ResetPasswordForm)
from blogApp import db, bcrypt
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from blogApp.users.utils import sendResetEmail, savePicture

users = Blueprint('users', __name__)


@users.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title = 'Register', form=form)

@users.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Unsuccessful login! Please check email and password', 'danger')
    return render_template('login.html', title = 'Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = savePicture(form.picture.data)
            current_user.imageFile = pictureFile

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated.", 'success')
        return redirect(url_for('users.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.imageFile)
    return render_template('account.html', title = 'Account', 
                           image_file = image_file, form = form)


@users.route("/user/<string:username>")
def userPosts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page = 3, page = page)
    return render_template('userPosts.html', posts = posts, user = user)


@users.route('/resetPassword', methods = ['GET', 'POST'])
def resetRequest():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        sendResetEmail(user)
        flash('An email has been sent with instructions to reset password', 'info')
        return redirect(url_for('users.login'))
    return render_template('resetRequests.html', title = 'Reset Password', form = form)

@users.route('/resetPassword/<token>', methods = ['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verifyResetToken(token)
    if user is None:
        flash('That is an invalid or expired link!', 'warning')
        return redirect(url_for('users.resetRequest'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('users.login'))
    
    return render_template('resetPassword.html', title = 'Reset Password', form = form)





