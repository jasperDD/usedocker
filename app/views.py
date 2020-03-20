# -*- encoding: utf-8 -*-
import sys
sys.path.insert(1, '/workspace/app/triplet_v2')
import os, logging, random, time, json, zipfile, shutil, glob
from flask import render_template, request, url_for, redirect, send_from_directory
from app import app
import main_functions as mf

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

@app.route('/forecastStr', methods = ['POST'])
def forecastStr():
    #clear val_data
    try:
        shutil.rmtree("/workspace/app/triplet_v2/val_data")
        os.mkdir("/workspace/app/triplet_v2/val_data")
    except:
        pass

    with open("/workspace/app/triplet_v2/val_data/output.csv", "w") as text_file:
        text_file.write(request.form.get('string'))
        text_file.close()
    
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
    res=''
    with open("/workspace/app/triplet_v2/forecasts/output.csv", "r") as text_file:
        res = text_file.read()
        text_file.close()

    return res

    # zipf = zipfile.ZipFile('/workspace/app/download.zip','w', zipfile.ZIP_DEFLATED)
    # for root,dirs, files in os.walk('/workspace/app/triplet_v2/forecasts/'):
    #     for file in files:
    #         zipf.write('/workspace/app/triplet_v2/forecasts/'+file)
    # zipf.close()
    
    # return send_from_directory('/workspace/app/', "download.zip", as_attachment=True)