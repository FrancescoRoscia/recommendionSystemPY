from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, login_user, logout_user, current_user 
from sqlalchemy import func

auth = Blueprint('auth', __name__) # we are defining a Blueprint

@auth.route('/login', methods=['GET', 'POST']) # url where this blueprint is located
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()

        if user:
            if check_password_hash(user.password, str(password)):
                flash('Logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html.j2", user=current_user) # for passing values


@auth.route('/logout') # url where this blueprint is located
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST']) # url where this blueprint is located
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()
        usern = User.query.filter(func.lower(User.username) == func.lower(username)).first()

        if user:
            flash('Email already exists', category='error')
        elif usern:
            flash('Username already exists', category='error')
        elif len(str(email)) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(str(username)) < 3:
            flash('Username must be greater than 2 characters. ', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(str(password1)) < 4:
            flash('Password must be greater than 3 characters.', category='error')
        else:
            new_user = User(email=email, username = username, password = generate_password_hash(str(password1), method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html.j2", user=current_user)