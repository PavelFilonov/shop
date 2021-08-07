from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from application import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)


class CartProduct(db.Model):
    id_addition = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, ForeignKey(User.id))
    id_product = db.Column(db.Integer, ForeignKey(Product.id))
    volume = db.Column(db.Integer, default=1)
    purchased = db.Column(db.Boolean, default=False)
    product = relationship("Product")
