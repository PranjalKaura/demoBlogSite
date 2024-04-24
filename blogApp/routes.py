from blogApp.models import User, Post
from blogApp.forms import RegisterationForm, LoginForm
from blogApp import app
from flask import render_template, url_for, flash, redirect



posts = [
    {
        'author': 'Pranjal Kaura',
        'title': 'How to play football',
        'content': 'Pretty self explanatory',
        'date_posted': 'April 20, 2024'
    },
    {
        'author': 'Leo Messi',
        'title': 'How to play football Better',
        'content': 'Pretty self explanatory Dun!!',
        'date_posted': 'April 21, 2024'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title = "Barca")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'admin':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Unsuccessful login!', 'danger')
    return render_template('login.html', title = 'Login', form=form)