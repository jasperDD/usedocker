# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask            import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login      import LoginManager
from flask_bcrypt     import Bcrypt
from flask_socketio   import SocketIO, emit 
from flask_cors import CORS, cross_origin

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

app.config.from_object('app.configuration.Config')
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy  (app) # flask-sqlalchemy
bc = Bcrypt      (app) # flask-bcrypt

lm = LoginManager(   ) # flask-loginmanager
lm.init_app(app) # init the login manager

# socketio = SocketIO(app, async_mode='threading', message_queue='redis://127.0.0.1:6379', threaded=True, cors_allowed_origins="*") # flask_socketio # message_queue='redis://127.0.0.1:6379'

# Setup database
@app.before_first_request
def initialize_database():
    db.create_all()

# Import routing, models and Start the App
from app import views, models
