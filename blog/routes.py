import os
import secrets

import arrow
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from flask_login import current_user, login_required
from htmlmin.minify import html_minify
from slugify import slugify

from app import db, app, current_user_image_file, csrf
from blog.blog_forms import PostForm, SearchForm
from models import Post

blog = Blueprint('blog', __name__, template_folder='templates')


def save_picture(post_form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(post_form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (1250, 1250)
    i = Image.open(post_form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def search_form():
    input_search_form = SearchForm()
    return input_search_form


posts_per_page = 20


@blog.route('/')
def home():
    return render_template('blog/index.html', input_search_form=search_form())


@blog.route('/all', methods=['GET', 'POST'])
def all_posts():
    session['url'] = url_for('blog.all_posts')
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,
                                                                  per_page=posts_per_page)

    if current_user.is_authenticated:
        rendered_html = render_template('blog/all.html',
                                        posts=posts,
                                        image_file=current_user_image_file(),
                                        input_search_form=search_form()
                                        )
        return html_minify(rendered_html)
    rendered_html = render_template('blog/all.html',
                                    posts=posts,
                                    input_search_form=search_form()
                                    )
    return html_minify(rendered_html)


@blog.route('/new', methods=['GET', 'POST'])
def new():
    form = PostForm()
    session['url'] = url_for('blog.new')
    if current_user.is_authenticated:
        if request.method == 'POST':
            content = request.form['body'].replace("<script>", "<strong class="'warning'">"
                                                               "<'Scripts tags on source Code are not allowed, "
                                                               "please use the Insert Code Snipped instead'></strong>")
            add_new_post = Post(
                post_image_file=save_picture(form.post_image_file.data),
                title=request.form['title'],
                slug=slugify(request.form['title']),
                body=content,
                # body=string.replace("geeks", "Geeks"),
                tags=request.form['tags'],
                author=current_user
            )
            db.session.add(add_new_post)
            db.session.commit()
            # flash('Post was successfully added')
            return redirect(url_for('blog.all_posts'))
    else:
        return current_app.login_manager.unauthorized()
    rendered_html = render_template('blog/new.html',
                                    form=form,
                                    image_file=current_user_image_file(),
                                    input_search_form=search_form()
                                    )
    return html_minify(rendered_html)


@blog.route("<int:id>/update", methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get(id)
    form = PostForm()
    session['url'] = url_for('blog.update_post', id=id)
    if current_user.is_authenticated:
        if post.author == current_user:
            if form.validate_on_submit():
                if form.post_image_file.data:
                    post_image_file = save_picture(form.post_image_file.data)
                    post.post_image_file = post_image_file

                post.title = form.title.data
                post.slug = slugify(form.title.data)
                post.body = form.body.data.replace("<script>", "<strong class="'warning'"> <'Scripts tags on source "
                                                               "Code are not allowed, "
                                                               "please use the Insert Code Snipped instead'></strong>")
                post.tags = form.tags.data
                db.session.commit()
                return redirect(url_for('blog.post',
                                        slug=post.slug))
            elif request.method == 'GET':
                post_image_file = post.post_image_file
                form.title.data = post.title
                form.body.data = post.body
                form.tags.data = post.tags

    else:
        return current_app.login_manager.unauthorized()
    rendered_html = render_template('blog/update.html',
                                    title='Update Post',
                                    form=form,
                                    image_file=current_user_image_file(),
                                    post_image_file=post_image_file,
                                    input_search_form=search_form())
    return html_minify(rendered_html)


@blog.route("/blog/<int:id>/delete", methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.all_posts'))


@blog.route('/<slug>', methods=['GET', 'POST'])
def post(slug):
    title_post = Post.query.filter_by(slug=slug).first_or_404()
    x = arrow.get(title_post.date_posted)
    data = {
        'title': title_post.title,
        'post_title': title_post.title,
        'date_posted': x.humanize(),
        'body': title_post.body,
        'author': title_post.author,
        'id': title_post.id,
        'post_image_file': title_post.post_image_file
    }
    if current_user.is_authenticated:
        rendered_html = render_template('blog/post.html', **data,
                                        image_file=current_user_image_file(),  # Pass image for profile
                                        input_search_form=search_form())
        return html_minify(rendered_html)
    else:
        rendered_html = render_template('blog/post.html', **data,
                                        input_search_form=search_form())
        return html_minify(rendered_html)


@blog.route('/s', methods=['GET', 'POST'])
def s():
    posts = Post.query.whoosh_search('Flask').all()
    ''''
    print(posts)
    for i in posts:
        print(i.id)
    '''
    return render_template('blog/search_results.html', posts=posts)


@blog.route('/search', methods=['GET', 'POST'])
@csrf.exempt
def search():
    session['url'] = url_for('blog.all_posts')
    search_q = request.form['search']
    page = request.args.get('page', 1, type=int)
    posts = Post.query.whoosh_search(search_q).order_by(Post.date_posted.desc()).paginate(page=page,
                                                                                          per_page=posts_per_page)
    if current_user.is_authenticated:
        rendered_html = render_template('blog/all.html',
                                        posts=posts,
                                        image_file=current_user_image_file(),
                                        input_search_form=search_form())
        return html_minify(rendered_html)
    rendered_html = render_template('blog/all.html',
                                    posts=posts,
                                    input_search_form=search_form())
    return html_minify(rendered_html)
