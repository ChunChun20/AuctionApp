#to make changes in the db type this in terminal
#from auction import app,db
#app.app_context().push()
#db.drop_all()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SECRET_KEY'] = 'ea3dfe510eafebf0ae34717a'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'
from auction import routes
