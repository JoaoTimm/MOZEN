from datetime import datetime

from flask_login import UserMixin

from app import db, login_manager




@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __searchable__ = ['username']
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy=True)


class Post(db.Model):
    __searchable__ = ['body', 'title', 'tags']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    slug = db.Column(db.String())
    body = db.Column(db.String())
    tags = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
