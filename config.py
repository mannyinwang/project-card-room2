from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, or_, and_ # for NOW() timestamp function
from flask_migrate import Migrate
import re  # the regex module    
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO 
app = Flask(__name__)

# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///card-room2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# an instance of the ORM
db = SQLAlchemy(app)
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
PWD_REGEX = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!*#?&])[A-Za-z\d@$!#*?&]{6,20}$")
app.secret_key = "bbbafdskiezxfjopterwggggfdsafdsafsdawiofxxgf"
# we are creating an object called bcrypt,
# which is made by invoking the function Bcrypt with our app as an argume
bcrypt = Bcrypt(app)  
socketio = SocketIO(app)
