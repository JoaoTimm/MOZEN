import os
import secrets

from PIL import Image

from flask import Blueprint, render_template, url_for, request, redirect, flash, session
from flask_login import login_required, current_user
from htmlmin.minify import html_minify

from account.forms import UpdateAccountForm
from app import db, app, current_user_image_file
from blog.routes import search_form
from models import User, Post

account = Blueprint('account', __name__, template_folder='templates')


@account.route("/", methods=['GET', 'POST'])
def home():
    rendered_html = render_template('account/index.html')
    return html_minify(rendered_html)


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


@account.route("/update", methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image_file.data:
            image_file = save_picture(form.image_file.data)
            current_user.image_file = image_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.git_username = form.git_username.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account.update_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.git_username.data = current_user.git_username
        # Private image path
    return render_template('account/account.html',
                           title='Account',
                           image_file=current_user_image_file(),
                           input_search_form=search_form(),
                           form=form)


@account.route("/profile/<user>", methods=['GET', 'POST'])
def profile(user):
    session['url'] = '/account/profile/' + user
    # print(session['url'])
    user = User.query.filter_by(username=user).first_or_404()
    # Public image path
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    if current_user.is_authenticated:
        return render_template('account/profile.html',
                               title='Account',
                               user=user,
                               image_file=current_user_image_file(),
                               input_search_form=search_form(),
                               posts=posts)
    return render_template('account/profile.html',
                           title='Account',
                           user=user,
                           posts=posts,
                           input_search_form=search_form()
                           )
