from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from flask_login import current_user, login_required
from slugify import slugify
from app import db
from blog.blog_forms import PostForm
from models import Post

blog = Blueprint('blog', __name__, template_folder='templates')


@blog.route('/')
def home():
    session['url'] = request.url
    return render_template('blog/index.html')


@blog.route('/new', methods=['GET', 'POST'])
def new():
    form = PostForm()
    session['url'] = url_for('blog.new')
    if current_user.is_authenticated:
        if request.method == 'POST':
            add_new_post = Post(
                title=request.form['title'],
                slug=slugify(request.form['title']),
                body=request.form['body'],
                tags=request.form['tags'],
                author=current_user
            )
            db.session.add(add_new_post)
            db.session.commit()
            # flash('Post was successfully added')
            return redirect(url_for('blog.home'))
    else:
        return current_app.login_manager.unauthorized()
    return render_template('blog/new.html', form=form)
