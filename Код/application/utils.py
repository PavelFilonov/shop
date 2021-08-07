from flask import request, session
from application.models import User


def get_active_user():
    username = None
    is_admin = None
    if 'id_user' in session:
        user = User.query.get(session['id_user'])
        username = user.name
        is_admin = user.is_admin
    return dict(username=username, is_admin=is_admin)


def log_out():
    if "exit_button" in request.form:
        session.pop('id_user', None)
        return True
    return False


def calculate_total(products):
    total = 0
    for product in products:
        total += product.volume * product.product.price
    return total
