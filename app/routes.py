import datetime
import secrets
import os
from PIL import Image
from flask import abort, render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, MakePost
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/<yas>")
def notfound(yas):
    return render_template("404.html", page=yas, title="404", type="Page")

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=Post.query.all())

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"You account has been created! You are now able to log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        flash("Login Unsuccessful. Check email and password.", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=["GET", "POST"])
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
        flash("Your account has been updated.", "success")
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data= current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route("/posts/new", methods=["GET", "POST"])
@login_required
def make_post():
    form = MakePost()
    if form.validate_on_submit():
        post = Post(title=form.title.data, date_posted=form.date_posted.data or datetime.datetime.utcnow(), content=form.content.data, user_id=current_user.get_id())
        db.session.add(post)
        db.session.commit()
        flash("Post made successfully!", "success")
        return redirect(f"/posts/{post.id}")
    return render_template("newpost.html", title="New Post", form=form)

@app.route("/posts/<num>")
def post(num):
    post = Post.query.get(num)
    if post:
        return render_template("post.html", title=post.title, post=post, content=post.content.split("\n"))
    return render_template("404.html", title="404", page=num, type="Post")

@app.route("/posts/<num>/edit", methods=["GET", "POST"])
def edit(num):
    post = Post.query.get(num)
    if post:
        if post.author != current_user:
            return render_template("403.html", title="403", page=f"{num}/edit", type="Resource")
        form = MakePost()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Your post has been updated!", "success")
            return redirect(url_for('post', num=post.id))
        elif request.method == "GET":
            form.title.data = post.title
            form.content.data = post.content
        return render_template("newpost.html", title="Update Post", form=form)

@app.route("/posts/<num>/delete", methods=["GET", "POST"])
def delete(num):
    post = Post.query.get(num)
    if post:
        if post.author != current_user:
            return render_template("403.html", title="403", page=f"{num}/delete", type="Resource")
        db.session.delete(post)
        db.session.commit()
        flash("Your post has been deleted!", "success")
        return redirect(url_for("home"))