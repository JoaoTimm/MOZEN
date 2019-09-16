from flask import Flask, render_template
from flask_assets import Environment, Bundle
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

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

from auth.routes import auth
from blog.routes import blog

app.register_blueprint(blog, url_prefix='/blog')
app.register_blueprint(auth, url_prefix='/auth')

# ######## BLUEPRINTS IMPORTS E #########
try:
    from models import Post

    print('Models imported')
except ImportError as e:
    print(e)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
