from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import login_manager
from auth.auth_forms import SignUp, SignIn
from models import User, db

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/')
def home():
    # return render_template('auth/index.html')
    return redirect(url_for('index'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUp()
    if request.method == 'POST' and form.validate_on_submit():
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password_hash']))
        db.session.add(new_user)
        db.session.commit()
        flash('You Sing Up successfully.')
        return redirect(url_for('auth.home'))
    return render_template('auth/sign-up.html', form=form)


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(int(user_id))


@auth.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    global form
    if not current_user.is_authenticated:
        form = SignIn()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password_hash.data):
                # login_user(user, remember=form.remember.data)
                login_user(user, remember=True)
                flash('You Sing In successfully.')
                if 'url' in session:
                    return redirect(session['url'])
                else:
                    return redirect(url_for('index'))
    elif current_user.is_authenticated:
        if 'url' in session:
            return redirect(session['url'])
        else:
            return redirect(url_for('index'))
    return render_template('auth/sign-in.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
