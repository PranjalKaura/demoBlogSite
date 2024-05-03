from blogApp import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    imageFile = db.Column(db.String(20), nullable = False, default='default.jpg')
    password = db.Column(db.String(60), nullable = False)
    posts = db.relationship('Post', backref='author', lazy = True)

    def getResetToken(self, expiresSec = 1800):
        s = Serializer(current_app.config['SECRET_KEY'], str(expiresSec))
        return s.dumps({'userID': self.id})
    
    @staticmethod
    def verifyResetToken(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            userID = s.loads(token)['userID']
            return User.query.get(userID)
        except:
            return None

    
    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}', '{self.imageFile}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default=datetime.now)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self) -> str:
        return f"Post('{self.title}', '{self.date_posted}')"