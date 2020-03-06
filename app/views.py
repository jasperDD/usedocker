# -*- encoding: utf-8 -*-
import sys, os, logging, random, time, json, zipfile
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

from app        import app, lm, db, bc
from app.models import User
from app.forms  import LoginForm, RegisterForm
# from app.generator import Generator

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
        return render_template('layouts/auth-default.html', content=render_template( 'pages/register.html', form=form, msg=msg ) )

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

    return render_template('layouts/auth-default.html', content=render_template( 'pages/register.html', form=form, msg=msg ))

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
    return "server"
    
    


@app.route('/train', methods = ['POST'])
def train():
    for file in request.files.getlist('files'):
        print(file.filename)
        file.save("/workspace/app/triplet_v2/train_data/"+file.filename)
    sys.path.insert(1, '/workspace/app/triplet_v2')
    import main_functions as mf
    import glob
    # Data preprocession
    mf.trans_data()
    # Train DNN
    mf.train_dnn(num_epochs=1) #DEBUG 10 
    # Validation DNN
    val_files = glob.glob('/workspace/app/triplet_v2/val_data'+'/*.csv')
    train_files = glob.glob('/workspace/app/triplet_v2/train_data'+'/*.csv')
    res=mf.proc_validation(list_files=val_files+train_files)
    print("The minimum precision of one class among all files:",res[0],"%")
    # Forecast based on DNN
    mf.proc_predict(input_folder='./workspace/app/triplet_v2/train_data')
    mf.proc_predict(input_folder='/workspace/app/triplet_v2/val_data')
    print("All operations have been done!")
    return "DONE"

@app.route('/forecast', methods = ['POST'])
def forecast():
    for file in request.files.getlist('files'):
        print(file.filename)
        file.save("/workspace/app/triplet_v2/val_data/"+file.filename)
    sys.path.insert(1, '/workspace/app/triplet_v2')
    import main_functions as mf
    import glob
    # Data preprocession
    mf.trans_data()
    # Train DNN
    mf.train_dnn(num_epochs=1) #DEBUG 10 
    # Validation DNN
    val_files = glob.glob('/workspace/app/triplet_v2/val_data'+'/*.csv')
    train_files = glob.glob('/workspace/app/triplet_v2/train_data'+'/*.csv')
    res=mf.proc_validation(list_files=val_files+train_files)
    print("The minimum precision of one class among all files:",res[0],"%")
    # Forecast based on DNN
    mf.proc_predict(input_folder='./workspace/app/triplet_v2/train_data')
    mf.proc_predict(input_folder='/workspace/app/triplet_v2/val_data')
    print("All operations have been done!")
    
    zipf = zipfile.ZipFile('/workspace/app/download.zip','w', zipfile.ZIP_DEFLATED)
    for root,dirs, files in os.walk('/workspace/app/triplet_v2/forecasts/'):
        for file in files:
            zipf.write('/workspace/app/triplet_v2/forecasts/'+file)
    zipf.close()
    
    return send_from_directory('/workspace/app/', "download.zip", as_attachment=True)
