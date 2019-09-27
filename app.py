import arrow
from flask import Flask, render_template, url_for, request, session
from flask_assets import Environment, Bundle
from flask_ckeditor import CKEditor
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from htmlmin.minify import html_minify
import flask_whooshalchemy as wa  # pip3 install git+git://github.com/gyllstromk/Flask-WhooshAlchemy.git
from flask_gzip import Gzip

from blog.blog_forms import SearchForm
from config import DevelopmentConfig, ProductionConfig

app = Flask(__name__)

app.config.from_object(DevelopmentConfig())
# app.config.from_object(ProductionConfig())


app.config['SECRET_KEY'] = app.config['SECRET_KEY']

csrf = CSRFProtect(app)
WTF_CSRF_SECRET_KEY = app.config['SECRET_KEY']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.sign_in'

app.config['PERMANENT_SESSION_LIFETIME'] = app.config['PERMANENT_SESSION_LIFETIME']
REMEMBER_COOKIE_DURATION = app.config['REMEMBER_COOKIE_DURATION']

app.config['CKEDITOR_PKG_TYPE'] = 'standard'  # CKEditor provide three type of presets (i.e. basic, standard and full)
ckeditor = CKEditor(app)
app.config['CKEDITOR_ENABLE_CSRF'] = True

# ######## FLASK ASSETS S ##############
assets = Environment(app)

css = Bundle('css/styles.css',
             'css/override_bootstrap.css',
             'css/ir_black.css',
             filters="cssmin",
             output='gen/styles.css')
assets.register('styles_css', css)

# ######## FLASK ASSETS E ##############


gzip = Gzip(app)


def current_user_image_file():
    if current_user.is_authenticated:
        image_file = url_for('static', filename=app.config['PROFILE_PICTURE_PATH'] + current_user.image_file)
        return image_file


# ######## BLUEPRINTS IMPORTS S ########
from account.routes import account
from auth.routes import auth
from blog.routes import blog, search_form

app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(blog, url_prefix='/blog')

try:
    from models import Post, User
except ImportError as e:
    print(e)

app.config['WHOOSH_BASE'] = app.config['WHOOSH_BASE']
wa.whoosh_index(app, User)
wa.whoosh_index(app, Post)


# ######## BLUEPRINTS IMPORTS E #########

# ############################
def acc_profile_link(self):
    """
    Instead of hard coding the Url to the User acc
    I use a custom Jinja2 function that if in the future I change
    the Profile view, I will not have to change all the hard coded ulr in all the files.

    Instead of the following:
        <a class="name" href="{{ url_for('account.profile', user= i.author.username )}}">{{ i.author.username }}</a>

    We do this:
        <a class="name" href="{{  i.author.username | acc_profile_link() }}">{{ i.author.username }}</a>

    """
    x = url_for('account.profile', user=self)
    return x


app.jinja_env.filters['acc_profile_link'] = acc_profile_link


def time_since(self):
    x = arrow.get(self)
    return x.humanize()


app.jinja_env.filters['time_since'] = time_since


def img_placeholder(a, z):
    x = f"https://via.placeholder.com/{a}x{z}"
    return x


app.jinja_env.filters['img_placeholder'] = img_placeholder


# ###########################


@app.before_request
def make_session_permanent():
    session.permanent = True


holders = {
    "img1": img_placeholder(1800, 400)
}


@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).limit(15).all()
    if current_user.is_authenticated:
        rendered_html = render_template('index.html',
                                        posts=posts,
                                        image_file=current_user_image_file(),
                                        input_search_form=search_form()
                                        )
        return html_minify(rendered_html)
    rendered_html = render_template('index.html',
                                    **holders,
                                    posts=posts,
                                    input_search_form=search_form())
    return html_minify(rendered_html)


if __name__ == '__main__':
    app.run()
