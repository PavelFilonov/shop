from flask import request, redirect, render_template, session, url_for

from application import app, db
from application.models import User, Product, CartProduct
from application.utils import get_active_user, log_out, calculate_total


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if log_out():
            redirect(url_for('main'))
        elif "add_to_cart" in request.form:
            cartProduct = CartProduct(id_user=session['id_user'], id_product=request.form['add_to_cart'])
            db.session.add(cartProduct)
            db.session.commit()
        elif "buy" in request.form:
            purchase = CartProduct(id_user=session['id_user'], id_product=request.form['buy'], purchased=True)
            db.session.add(purchase)
            db.session.commit()
        elif "delete" in request.form:
            deleted_product = Product.query.get(request.form['delete'])
            deleted_cart_products = CartProduct.query.filter(CartProduct.id_product == deleted_product.id).all()
            db.session.delete(deleted_product)
            for c in deleted_cart_products:
                db.session.delete(c)
            db.session.commit()
    products = Product.query.order_by(Product.id).all()
    active_user = get_active_user()
    return render_template('main.html', products=products, **active_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter(User.name == name).first()

        if user is None or user.password != password:
            return render_template('login.html', message="Неверные данные", username=None)
        else:
            session['id_user'] = user.id
            return redirect(url_for('main'))
    active_user = get_active_user()
    return render_template('login.html', **active_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            return render_template('register.html', message="Пароли не совпадают", username=None)

        if len(password1) < 8:
            return render_template('register.html', message="Минимальное количество символов: 8", username=None)

        user = User.query.filter(User.name == name).first()

        if user is not None:
            return render_template('register.html', message="Пользователь уже существует", username=None)

        new_user = User(name=name, password=password1)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['id_user'] = new_user.id
            return redirect(url_for('main'))
        except:
            return render_template('register.html', message="Неправильный ввод", username=None)
    active_user = get_active_user()
    return render_template('register.html', **active_user)


@app.route('/create', methods=['GET', 'POST'])
def create():
    active_user = get_active_user()
    if not active_user['is_admin']:
        return redirect(url_for('main'))

    if request.method == 'POST':
        if log_out():
            return redirect(url_for('main'))

        title = request.form['title']
        description = request.form['description']

        try:
            price = float(request.form['price'])
        except:
            return render_template('create.html', message="Неправильный ввод", **active_user)

        if price < 0:
            return render_template('create.html', message="Отрицательная цена", **active_user)

        product = Product(title=title, price=price, description=description)

        try:
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('main'))
        except:
            return render_template('create.html', message="Неправильный ввод", **active_user)
    return render_template('create.html', **active_user)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    active_user = get_active_user()
    if request.method == 'POST':
        if log_out():
            return redirect(url_for('main'))
        elif "delete" in request.form:
            deleted = CartProduct.query.filter(CartProduct.id_addition == request.form['delete'],
                                               CartProduct.purchased == False).first()
            db.session.delete(deleted)
        elif "update" in request.form:
            cart_products = CartProduct.query.filter(CartProduct.id_user == session['id_user'],
                                                     CartProduct.purchased == False).all()
            for cp in cart_products:
                is_correct = True
                new_volume = 0
                try:
                    new_volume = int(request.form[str(cp.id_addition)])
                except:
                    is_correct = False

                if is_correct and new_volume > 0:
                    cp.volume = new_volume
        elif "buy" in request.form:
            cart_products = CartProduct.query.filter(CartProduct.id_user == session['id_user'],
                                                     CartProduct.purchased == False).all()
            for cp in cart_products:
                cp.purchased = True
    db.session.commit()
    cart_products = CartProduct.query.filter(CartProduct.id_user == session['id_user'],
                                             CartProduct.purchased == False).all()
    total = calculate_total(cart_products)
    return render_template('cart.html', **active_user, cart_products=cart_products, size=len(cart_products),
                           total=total)


@app.route('/products/<int:id>', methods=['GET', 'POST'])
def show_product(id):
    product = Product.query.get(id)
    params = dict(title=product.title, price=product.price, description=product.description,
                  path_to_image=product.path_to_image)

    if request.method == 'POST':
        if log_out():
            return redirect(url_for('main'))
        elif "add_to_cart" in request.form:
            cartProduct = CartProduct(id_user=session['id_user'], id_product=request.form['add_to_cart'])
            db.session.add(cartProduct)
            db.session.commit()
        elif "buy" in request.form:
            purchase = CartProduct(id_user=session['id_user'], id_product=id, purchased=True)
            db.session.add(purchase)
            db.session.commit()
        elif "delete" in request.form:
            deleted_product = Product.query.get(id)
            deleted_cart_products = CartProduct.query.filter(CartProduct.id_product == deleted_product.id).all()
            db.session.delete(deleted_product)
            for c in deleted_cart_products:
                db.session.delete(c)
            db.session.commit()
            return redirect(url_for('main'))
    active_user = get_active_user()
    return render_template('product.html', **params, **active_user)


@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST' and log_out():
        return redirect(url_for('main'))
    active_user = get_active_user()
    return render_template('about.html', **active_user)


@app.route('/users', methods=['GET', 'POST'])
def users():
    active_user = get_active_user()
    if not active_user['is_admin']:
        return redirect(url_for('main'))
    if request.method == 'POST':
        if log_out():
            return redirect(url_for('main'))
        elif "delete_user" in request.form:
            deleted_user = User.query.get(request.form['delete_user'])
            deleted_cart_products = CartProduct.query.filter(CartProduct.id_user == deleted_user.id).all()
            db.session.delete(deleted_user)
            for c in deleted_cart_products:
                db.session.delete(c)
        elif "do_admin" in request.form:
            new_admin = User.query.get(request.form['do_admin'])
            new_admin.is_admin = True
        elif "remove_admin" in request.form:
            old_admin = User.query.get(request.form['remove_admin'])
            old_admin.is_admin = False
        db.session.commit()
    all_users = User.query.order_by(User.id).all()
    return render_template('users.html', users=all_users, **active_user)


@app.route('/purchase', methods=['GET', 'POST'])
def show_purchased():
    active_user = get_active_user()
    purchases = CartProduct.query.filter(CartProduct.id_user == session['id_user'], CartProduct.purchased).all()
    total = calculate_total(purchases)
    if request.method == 'POST' and log_out():
        return redirect(url_for('main'))
    return render_template('purchase.html', purchases=purchases, **active_user, size=len(purchases), total=total)
