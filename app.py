from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Product

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='345678', is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Користувач з таким іменем вже існує!', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Реєстрація успішна! Увійдіть у систему.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    
    if user:
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('product_manager'))
    else:
        flash('Невірний логін або пароль!', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Доступ заборонено!', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>')
def admin_user_products(user_id):
    if not session.get('is_admin'):
        flash('Доступ заборонено!', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    products = Product.query.filter_by(user_id=user_id).all()
    return render_template('product_manager.html', products=products, user=user, is_admin=True)

@app.route('/admin/delete_user/<int:user_id>')
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        flash('Доступ заборонено!', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    Product.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('Користувача успішно видалено!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/products')
def product_manager():
    if not session.get('user_id'):
        flash('Увійдіть у систему!', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    products = Product.query.filter_by(user_id=user_id).all()
    return render_template('product_manager.html', products=products, is_admin=False)

@app.route('/add_product', methods=['POST'])
def add_product():
    if not session.get('user_id'):
        flash('Увійдіть у систему!', 'error')
        return redirect(url_for('index'))
    
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    user_id = session['user_id']
    
    new_product = Product(name=name, quantity=quantity, price=price, user_id=user_id)
    db.session.add(new_product)
    db.session.commit()
    
    flash('Продукт успішно додано!', 'success')
    return redirect(url_for('product_manager'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = request.form['quantity']
        product.price = request.form['price']
        
        db.session.commit()
        flash('Продукт успішно оновлено!', 'success')
        return redirect(url_for('product_manager'))
    
    return render_template('edit.html', product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    user_id = product.user_id  # Зберігаємо user_id перед видаленням
    db.session.delete(product)
    db.session.commit()

    # Оновлюємо ID продуктів після видалення
    products = Product.query.filter_by(user_id=user_id).order_by(Product.id).all()
    for index, product in enumerate(products, start=1):
        product.id = index
    db.session.commit()

    flash('Продукт успішно видалено!', 'success')
    return redirect(url_for('product_manager'))

if __name__ == '__main__':
    app.run(debug=True)