from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '6429c683fb2dfc3cba98c220bc354a94'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'danger'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'dummy@dummy.com'
app.config['MAIL_PASSWORD'] = 'dummy@'
mail = Mail(app)

app.app_context().push()
db.create_all()

from blogApp.users.routes import users
from blogApp.posts.routes import posts
from blogApp.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)