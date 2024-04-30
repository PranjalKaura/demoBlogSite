from blogApp.models import User, Post
from blogApp.forms import (RegisterationForm, LoginForm, UpdateAccountForm, PostForm, 
                           RequestResetForm, ResetPasswordForm)
from blogApp import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
import secrets
from PIL import Image
import os

app.app_context().push()
db.create_all()


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page = 3, page = page)
    return render_template('home.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title = "Barca")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Unsuccessful login! Please check email and password', 'danger')
    return render_template('login.html', title = 'Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def savePicture(formPicture):
    randomHex = secrets.token_hex(8)
    _, fileExt = os.path.splitext(formPicture.filename)
    randomFileName = randomHex + fileExt
    filePath = os.path.join(app.root_path, 'static/profile_pics', randomFileName)
    #resizing image
    output_size = (125, 125)
    i = Image.open(formPicture)
    i.thumbnail(output_size)
    i.save(filePath)

    return randomFileName

@app.route('/account', methods = ['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.imageFile)
    return render_template('account.html', title = 'Account', 
                           image_file = image_file, form = form)

@login_required
@app.route('/post/new', methods = ['GET', 'POST'])
def newPost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, 
                    author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('home'))
    return render_template('createPost.html', title = 'New Post', 
                           legend = 'New Post', form = form)



@app.route('/post/<int:postID>')
def post(postID):
    post = Post.query.get_or_404(postID)
    return render_template('post.html', title = post.title, post = post)

@login_required
@app.route('/post/<int:postID>/update', methods = ['GET', 'POST'])
def updatePost(postID):
    post = Post.query.get_or_404(postID)
    if post.author!=current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', postID = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('createPost.html', title = 'Update Post', 
                           legend = 'Update Post', form = form)

@login_required
@app.route('/post/<int:postID>/delete', methods = ['POST'])
def deletePost(postID):
    post = Post.query.get_or_404(postID)
    if post.author!=current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def userPosts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page = 3, page = page)
    return render_template('userPosts.html', posts = posts, user = user)

def sendResetEmail(user):
    token = user.getResetToken()
    msg = Message('Password Reset Request', sender='pranjalkaura22@gmail.com', 
                  recipients=[user.email])
    msg.body = f''' To reset your password visit the following link:
    {url_for('resetPassword', token = token, _external = True)}

    If you did not make this request, please ignore this message.
    '''
    mail.send(msg)

@app.route('/resetPassword', methods = ['GET', 'POST'])
def resetRequest():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        sendResetEmail(user)
        flash('An email has been sent with instructions to reset password', 'info')
        return redirect(url_for('login'))
    return render_template('resetRequests.html', title = 'Reset Password', form = form)

@app.route('/resetPassword/<token>', methods = ['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verifyResetToken(token)
    if user is None:
        flash('That is an invalid or expired link!', 'warning')
        return redirect(url_for('resetRequest'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('resetPassword.html', title = 'Reset Password', form = form)




