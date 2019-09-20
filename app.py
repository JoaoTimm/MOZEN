import datetime

from flask import Flask, render_template, url_for, request, session
from flask_assets import Environment, Bundle
from flask_ckeditor import CKEditor
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from htmlmin.minify import html_minify
from flask_gzip import Gzip
from config import DevelopmentConfig, ProductionConfig

app = Flask(__name__)

app.config.from_object(DevelopmentConfig())
# app.config.from_object(ProductionConfig())


app.config['SECRET_KEY'] = app.config['SECRET_KEY']

csrf = CSRFProtect(app)
WTF_CSRF_SECRET_KEY = app.config['SECRET_KEY']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

app.config['PERMANENT_SESSION_LIFETIME'] = app.config['PERMANENT_SESSION_LIFETIME']
REMEMBER_COOKIE_DURATION = app.config['REMEMBER_COOKIE_DURATION']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.sign_in'

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

# ######## BLUEPRINTS IMPORTS S ########

from account.routes import account
from auth.routes import auth
from blog.routes import blog

app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(blog, url_prefix='/blog')

# ######## BLUEPRINTS IMPORTS E #########
try:
    from models import Post

    print('Models imported')
except ImportError as e:
    print(e)


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def index():
    if current_user.is_authenticated:
        image_file = url_for('static', filename=app.config['PROFILE_PICTURE_PATH'] + current_user.image_file)
        rendered_html = render_template('index.html', image_file=image_file)
        return html_minify(rendered_html)
    rendered_html = render_template('index.html')
    return html_minify(rendered_html)


if __name__ == '__main__':
    app.run()
