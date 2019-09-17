from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from flask_login import current_user
from htmlmin.minify import html_minify
from slugify import slugify

from app import db, app
from blog.blog_forms import PostForm
from models import Post

blog = Blueprint('blog', __name__, template_folder='templates')


@blog.route('/')
def home():
    session['url'] = request.url
    return render_template('blog/index.html')


@blog.route('/all', methods=['GET', 'POST'])
def all_posts():
    session['url'] = url_for('blog.all_posts')
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=9)
    if current_user.is_authenticated:
        image_file = url_for('static', filename=app.config['PROFILE_PICTURE_PATH'] + current_user.image_file)
        rendered_html = render_template('blog/all.html', posts=posts, image_file=image_file)
        return html_minify(rendered_html)
    rendered_html = render_template('blog/all.html', posts=posts)
    return html_minify(rendered_html)


@blog.route('/new', methods=['GET', 'POST'])
def new():
    form = PostForm()
    session['url'] = url_for('blog.new')
    if current_user.is_authenticated:
        image_file = url_for('static', filename=app.config['PROFILE_PICTURE_PATH'] + current_user.image_file)
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
            return redirect(url_for('blog.all_posts'))
    else:
        return current_app.login_manager.unauthorized()
    rendered_html = render_template('blog/new.html', form=form, image_file=image_file)
    return html_minify(rendered_html)


@blog.route("/blog/<int:id>/delete", methods=['POST'])
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.all_posts'))


@blog.route('/<slug>', methods=['GET', 'POST'])
def post(slug):
    title_post = Post.query.filter_by(slug=slug).first_or_404()
    rendered_html = render_template('blog/post.html', title_post=title_post, title=title_post.title)
    return html_minify(rendered_html)
