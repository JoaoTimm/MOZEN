from flask import Flask, render_template, url_for
from flask_assets import Environment, Bundle
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from htmlmin.minify import html_minify

app = Flask(__name__)

app.config.from_pyfile('config.py')

app.config['SECRET_KEY'] = app.config['SECRET_KEY']

csrf = CSRFProtect(app)
WTF_CSRF_SECRET_KEY = app.config['SECRET_KEY']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.sign_in'

# ######## FLASK ASSETS S ##############
assets = Environment(app)

css = Bundle('css/styles.css',
             'css/override_bootstrap.css',
             filters="cssmin",
             output='gen/styles.css')
assets.register('styles_css', css)

# ######## FLASK ASSETS E ##############

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


@app.route('/')
def index():
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        rendered_html = render_template('index.html', image_file=image_file)
        return html_minify(rendered_html)
    rendered_html = render_template('index.html')
    return html_minify(rendered_html)


if __name__ == '__main__':
    app.run()
