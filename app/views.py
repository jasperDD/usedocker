# -*- encoding: utf-8 -*-
import os, logging, random, time, json
import numpy as np

from flask               import render_template, request, url_for, redirect, send_from_directory, send_file, session
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from datetime import datetime, date

from app        import app, lm, db, bc, socketio
from app.models import User
from app.forms  import LoginForm, RegisterForm
from app.generator import Generator


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None

    if request.method == 'GET': 
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/register.html', form=form, msg=msg ) )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = password #bc.generate_password_hash(password)

            user = User(username, email, pw_hash)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     

    else:
        msg = 'Input error'     

    return render_template('layouts/auth-default.html',
                            content=render_template( 'pages/register.html', form=form, msg=msg ) )

# Authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    # Declare the login form
    form = LoginForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        if user:
            #if bc.check_password_hash(user.password, password):
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unkkown user"
    return render_template('layouts/auth-default.html', content=render_template( 'pages/login.html', form=form, msg=msg ) )

# App main route + generic routing
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('layouts/default.html', content=render_template('pages/index.html'))
    #return render_template('layouts/auth-default.html',content=render_template( 'pages/404.html' ))

@app.route('/output/<path:path>')
def send_video(path):
    return send_from_directory('/workspace/output', path)
    
@app.route('/download/<path:path>')
def download_video(path):
    return send_from_directory('/workspace/output', path, as_attachment=True)
    
@app.route('/player', methods = ['GET'])
def player():
    return render_template('layouts/default.html', content=render_template('pages/player.html', link_download="/download/output_video.mp4", link = "/output/output_video.mp4"))
    # return render_template('layouts/default.html', content=render_template('pages/player.html', link_download= request.args.get('link_download'), link = request.args.get('link')))

# HOOK TO SHOW PROGRESS WITH SOCKETIO FROM OTHER MODULE PROCESS
import multiprocessing
def start(filename_out, text):
    generator = Generator(phrase=text, videoname=filename_out)
    generator.generate_video()
    
@app.route('/generate', methods = ['POST'])
def generate():
    if request.method == 'POST':
        filename_out = request.get_json()['filename']
        text = request.get_json()['text']
        
        thread = multiprocessing.Process(target=start, args=(filename_out, text))
        thread.start()
        
        # generator = Generator(phrase=text, videoname=filename_out)
        # output_filename = generator.generate_video()
        
    return "NEW"
    

@app.route('/upload', methods = ['GET', 'POST'])
def upload_generated_videos():
    if request.method == 'POST':
        filename_out = ""
        # CREATE FOLDER IF NOT EXIST
        try:
            os.makedirs(app.config['APP_ROOT']+"videos/") #+request.form.get('videoText')
        except OSError as e:
            pass
        
        # SAVE UPLOADED VIDEO
        for f in request.files.getlist('videoFile'):
            filename_out = "video_input.mp4"#str(random.randrange(10,10000))+"_"+f.filename
            f.save(app.config['APP_ROOT']+"videos/"+filename_out) #+request.form.get('videoText')
            
        text = "TEXT"
        if (request.form.get('videoText')!=""):
            text = request.form.get('videoText')
        
        return render_template('layouts/default.html', content=render_template('pages/progress.html', filename=filename_out, text=text))
        
        # # GENERATE
        # 
        # # REDIRECT TO VIDEOPLAYER PAGE
        # return redirect(url_for('player', link_download=request.host_url+"download/"+output_filename, link=request.host_url+"output/"+output_filename, **request.args))

