import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, current_app
from app import app, db, bcrypt, mail, mail_username
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, FoodForm, TableForm, BlogForm, MenuForm, RequestResetForm, ResetPasswordForm, WeeklyForm, ContactForm
from app.models import User, Order, Table, Blog, Menu, Weekly
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from threading import Thread


@app.route('/', methods=['GET', 'POST'])
def index():
    blog = Blog.query.all()
    weekly = Weekly.query.all()
    return render_template("index.html", blog=blog, weekly=weekly)


@app.route('/blog')
def blog():
    blog = Blog.query.all()
    return render_template("blog.html", blog=blog)


@app.route('/menu')
def menu():
    menu = Menu.query.all()
    return render_template("menu.html", menu=menu)


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    user = User
    form = ContactForm()
    if form.validate_on_submit():

        msg = Message(f'New Message from {current_user.username}', sender=f'{user.email}',
                      recipients=['eorji452@gmail.com'])
        msg.body = f"""
           Name :  {form.name.data}

           Email :  {form.email.data}

           Subject :  {form.subject.data}

           Message :  {form.message.data}
           """
        mail.send(msg)
        flash('your message have been sent', 'success')

    return render_template('contact.html', title='contact Form', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have logged in successfully.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('login unsuccessful.please check your Email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)

    # output_size = (1000, 1000)output_size
    i = Image.open(form_picture)
    i.thumbnail()
    i.save(picture_path)

    return picture_fn


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_token()
    send_email('[Sir Trendy] Reset Your Password', sender='wishotstudio@gmail.com', recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template("account.html", image_file=image_file, form=form)


@app.route('/admin')
def admin():
    menu = Menu.query.all()
    users = User.query.all()
    food = Order.query.all()
    table = Table.query.all()
    weekly = Weekly.query.all()
    if current_user.id != 2:
        flash('Please You cant access this page', 'danger')
        return redirect(url_for('home', menu=menu, weekly=weekly, users=users, food=food, table=table))
    else:
        render_template('Admin/home.html', users=users, weekly=weekly, menu=menu, food=food, table=table)
        image_file = url_for('static', filename='img/' + current_user.image_file)

    return render_template('Admin/home.html', users=users, weekly=weekly, menu=menu, food=food, table=table, image_file=image_file)


@app.route('/food', methods=['GET', 'POST'])
@login_required
def food():
    form = FoodForm()
    if form.validate_on_submit():
        order = Order(name=form.name.data, address=form.address.data, phone=form.phone.data,
                      food_name=form.food_name.data, food_quantity=form.food_quantity.data, author=current_user)
        db.session.add(order)
        db.session.commit()
        flash("Food booked successfully", 'success')
        return redirect(url_for('food'))
    return render_template('food.html', form=form)


@app.route('/table', methods=['GET', 'POST'])
@login_required
def table():
    form = TableForm()
    if form.validate_on_submit():
        table = Table(name=form.name.data, day=form.day.data, hour=form.hour.data,
                      phone=form.phone.data, person=form.person.data, author=current_user)
        db.session.add(table)
        db.session.commit()
        flash("Food booked successfully", 'success')
        return redirect(url_for('table'))
    return render_template('table.html', form=form)


@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    global image_file
    form = BlogForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            image = picture_file
        title = form.title.data
        content = form.content.data
        author = current_user
        post = Blog(title=title, content=content, author=author, image=image)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        image_file = url_for('static', filename='img/' + Blog.image)
        image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('admin/create_blog.html', form=form, image_file=image_file)


@app.route('/weekly', methods=['GET', 'POST'])
@login_required
def weekly():
    global image_file
    form = WeeklyForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            image = picture_file
        subtitle = form.subtitle.data
        price = form.price.data
        title = form.title.data
        content = form.content.data
        author = current_user
        weekly = Weekly(price=price, title=title, subtitle=subtitle, content=content, author=author, image=image)
        db.session.add(weekly)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        image_file = url_for('static', filename='img/' + Weekly.image)
        image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('admin/create_weekly.html', form=form, image_file=image_file)


@app.route('/menu/new', methods=['GET', 'POST'])
@login_required
def new_menu():
    form = MenuForm()
    if form.validate_on_submit():
        menu = Menu(name=form.name.data, price=form.price.data, author=current_user)
        db.session.add(menu)
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('admin'))
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('admin/create_menu.html', form=form, image_file=image_file)


@app.route("/delete_food/<int:foods_id>/delete", methods=['GET', 'POST'])
def delete_food(foods_id):
    food = Order.query.get_or_404(foods_id)
    if current_user.id != 2:
        abort(403)
    db.session.delete(food)
    db.session.commit()
    flash("deleted", 'success')
    return redirect(url_for('admin'))
    return render_template("Admin/home.html", food=food)


@app.route("/delete_table/<int:tables_id>/delete", methods=['GET', 'POST'])
def delete_table(tables_id):
    table = Table.query.get_or_404(tables_id)
    if current_user.id != 2:
        abort(403)
    db.session.delete(table)
    db.session.commit()
    flash("deleted", 'success')
    return redirect(url_for('admin'))
    return render_template("Admin/home.html", table=table)


@app.route("/delete_user/<int:user_id>/delete", methods=['GET', 'POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id != 2:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    flash("deleted", 'success')
    return redirect(url_for('admin'))
    return render_template("Admin/home.html", user=user)


@app.route("/delete_menu/<int:menu_id>/delete", methods=['GET', 'POST'])
def delete_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    if current_user.id != 2:
        abort(403)
    db.session.delete(menu)
    db.session.commit()
    flash("deleted", 'success')
    return redirect(url_for('admin'))
    return render_template("Admin/home.html", user=user)


@app.route("/delete_weekly/<int:weekly_id>/delete", methods=['GET', 'POST'])
def delete_weekly(weekly_id):
    weekly = Weekly.query.get_or_404(weekly_id)
    if current_user.id != 2:
        abort(403)
    db.session.delete(weekly)
    db.session.commit()
    flash("deleted", 'success')
    return redirect(url_for('admin'))
    return render_template("Admin/home.html", weekly=weekly)


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password-<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('your password has been updated!.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
