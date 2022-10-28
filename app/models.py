from app import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
import jwt
from time import time




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False, )
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg')
    post = db.relationship('Blog', backref='author', lazy=True)
    orders = db.relationship('Order', backref='author', lazy=True)
    tables = db.relationship('Table', backref='author', lazy=True)
    menu = db.relationship('Menu', backref='author', lazy=True)
    weekly = db.relationship('Weekly', backref='author', lazy=True)

    def get_reset_token(self, expires_in=300):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),  nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(60), nullable=False)
    food_name = db.Column(db.Text, nullable=False)
    food_quantity = db.Column(db.Text, nullable=False)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Order('{self.name}','{self.food_quantity}','{self.phone}','{self.food_name}','{self.address}','{self.date_ordered}') "


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Text, nullable=False)
    hour = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(20),  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Table('{self.day}','{self.hour}','{self.full_name}','{self.person}','{self.phone}')"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Blog('{self.title}', '{self.content}', '{self.image}')"


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Menu('{self.name}', '{self.price}')"


class Weekly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtitle = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Weekly('{self.title}',{self.subtitle}', '{self.content}', '{self.image}')"
