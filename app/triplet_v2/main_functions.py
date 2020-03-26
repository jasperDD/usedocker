# -*- coding: utf-8 -*-
'''
В данном модуле собраны функции необходимые для препроцессинга данных с целью
обучения модели и прогнозирования на её основе.
'''

import pandas as pd # for data frames
import numpy as np # for arrayes
import category_encoders as ce # for categorical transformation
from sklearn import impute # for handle missing values
from sklearn import preprocessing # for preprocessiong data
import pickle # for save any models
#import sys
import dnn_class as dnn
import torch
import torch.utils.data as data_utils
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import os
from barbar import Bar
import progressbar
import glob
import sys
import time

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Train DNN
# '/workspace/app/triplet_v2/sd/train_data.npz'
def train_dnn(train_data_file='/workspace/app/triplet_v2/sd/train_data.npz', 
              val_folder='/workspace/app/triplet_v2/val_data', 
              col_name_file='/workspace/app/triplet_v2/sd/col_names.npz',
              dnn_file='/workspace/app/triplet_v2/sd/dnn_model.pth',  
              c_dnn_file='/workspace/app/triplet_v2/sd/c_dnn_model.pth', 
              out_file='/workspace/app/triplet_v2/results_cm.txt', 
              num_epochs=250,
              lr=0.00001):
    print("The training DNN has been started...")
    # load list of validation files
    list_val_files = glob.glob(val_folder+'/*.csv')    
    s_data = np.load(train_data_file, allow_pickle = True)
    # split into X and y
    X=s_data['X']
    y=s_data['y']
    # convert to tensor
    X_train=torch.tensor(X).float()
    y_train=torch.tensor(y).long().unsqueeze(1)
    # count unique values
    #unique_y_train, counts_y_train = np.unique(y_train, return_counts=True)
    # create train data set
    train_data = data_utils.TensorDataset(X_train, y_train)
    train_loader = data_utils.DataLoader(train_data, batch_size=16,shuffle=True)#, sampler=sm)
    # set model
    model =dnn.DNN_ClassifierM(X.shape[1])
    # decision of training process
    if os.path.exists(c_dnn_file):
        try:
            model.load_state_dict(torch.load(c_dnn_file))
            print("The pre-trained network has been loaded!")
        except Exception:
            os.remove(c_dnn_file)
            print("New network has been started to train (maybe something was wrong with source data set)!")
    # set optimizer
    optimizer = torch.optim.Adamax(model.parameters(), lr=lr)
    # set loss function
    #class_weights = torch.FloatTensor(np.sum(counts_y_train)/counts_y_train)
    #class_weights = torch.FloatTensor(counts_y_train)
    #class_weights = class_weights / torch.sum(class_weights)
    class_weights = dnn.get_weights(y)    
    print("The class weights:",class_weights)
    criterion = torch.nn.NLLLoss(weight=class_weights) # set weights
    #criterion = dnn.WBCELoss
    # set the train mode
    model.train()
    min_prec=0
    val_ac=0
    if os.path.exists(dnn_file):
        val_res = proc_validation(list_val_files,col_name_file,dnn_file, out_file, verb=False)
        min_prec = val_res[0]
        val_ac = val_res[1]
    print("The best (current) minimal validation precision:",min_prec,"%")
    best_epoch=1
    for i in range(num_epochs):
        #model.train()
        print('Epoch: {}'.format(i+1))  
        # set the list of true values and predictions
        all_y=np.array([])
        all_pr=np.array([])
        for k, (sX_train, sy_train) in enumerate(Bar(train_loader)):
            # Set gradients to zero
            optimizer.zero_grad()
            # Forward pass
            spr_train = model(sX_train) # get log prob
            # Compute Loss
            train_loss = criterion(spr_train,sy_train.view(-1)) # loss function   
            #print(sy_train.view(-1))            
            # Backward pass
            train_loss.backward() # estimate gradient for training loss
            # Update gradients
            optimizer.step() # parameters update
            # get classes
            spr_train = spr_train.exp().detach()
            _, spr_train = torch.max(spr_train,1)
            # Add to list true values and predictions
            all_y=np.concatenate([all_y,sy_train.detach().view(-1).numpy()])
            all_pr=np.concatenate([all_pr,spr_train.numpy()])            
            #print(sy_train.detach().view(-1).numpy().shape)            
        # Print base results
        # Create confusion matrix for training results
        cm_train=confusion_matrix(all_y, all_pr)   
        pcm_train=np.round(100*cm_train/(1e-3+np.sum(cm_train,axis=0)),2)
        #print(pcm_train)
        #print(np.diagonal(pcm_train))
        print("The minimal training precision for one class",np.min(np.diagonal(pcm_train)),"%")
        print("The training accuracy",np.round(accuracy_score(all_y, all_pr)*100,2),"%")
        # Save current model
        torch.save(obj=model.state_dict(),f=c_dnn_file)
        # Validation
        if len(list_val_files)>0:
            val_res = proc_validation(list_val_files,col_name_file,c_dnn_file, out_file, verb=False)
            c_min_prec = val_res[0]
            c_ac_val = val_res[1]
            if c_min_prec>=min_prec:
                min_prec=c_min_prec
                val_ac=c_ac_val
                torch.save(obj=model.state_dict(),f=dnn_file)
                best_epoch=i+1
        print("The best minimal validation precision for one class:",min_prec,"%; Epoch:",best_epoch)
        print("The best validation accuracy:",val_ac,"%")
    
    val_res = proc_validation(list_val_files,col_name_file,dnn_file, out_file, verb=False)
    min_prec = val_res[0]
    val_ac = val_res[1]
    print("The best minimal validation precision for one class:",min_prec,"%; Epoch:",best_epoch)
    print("The best validation accuracy:",val_ac,"%")
    print("The work has been finished! You can run again this program for continue training (press F5)")
    return True
    
    
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# extract only hours
def extr_hours(x):
    x = pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S", errors = 'coerce').copy() # add 'nan'
    x = [str(i.hour) for i in x]
    return x

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# convert to float vector
def conv_float(x):
    z = np.zeros(len(x))
    for i in range(len(x)):
        try:
            z[i] = float(x[i])
            if pd.isnull(x[i])==True or pd.isna(x[i])==True:
                z[i]=0
            continue
        except Exception:
            z[i] = 0
            continue
    return z

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# check column names x in y
def check_cn(x,y):
    res=[i in y for i in x]
    return res


# WOE-binning
'''
woe_col=['stat_order_created_ts','stat_order_processed_user_id','stat_order_confirmed_ts',
         'stat_order_confirmed_user_id','stat_order_operator_id','stat_order_country',
         'stat_order_country_ip','stat_order_country_phone','stat_order_phone_geocoder',
         'stat_order_phone_valid','stat_order_is_call_fail','stat_order_valid_error',
         'stat_order_webmaster_id','stat_order_offer_id','stat_order_landing_id',
         'stat_order_prelanding_id','stat_order_landing_currency','stat_order_account_manager_id',
         'stat_delivery_exception','stat_delivery_operator_status',
         'stat_delivery_google_and_operator_address_match']
'''
# Dummy-transformation of required columns
'''dummy_col=['stat_order_is_prepay','stat_order_unique_goods']'''


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Variable's preprocessing for new X (for training)
def preproc_new_X(X):
    if not os.path.exists('/workspace/app/triplet_v2/sd'):
        os.mkdir('/workspace/app/triplet_v2/sd')
    # fill all nan
    X=X.fillna('nan')
    # Variable preprocessing
    # extract only hours from stat_order_created_ts
    X.stat_order_created_ts=extr_hours(X.stat_order_created_ts).copy()
    #X.stat_order_created_ts.unique()
    # extract only hours from stat_order_confirmed_ts
    X.stat_order_confirmed_ts=extr_hours(X.stat_order_confirmed_ts).copy()
    #X.stat_order_confirmed_ts.unique()
    # Numeric transformation and replace nan with 0
    num_col = ['stat_order_money','stat_order_count_call',
               'stat_order_count_callback','stat_order_good_count',
               'stat_order_time_before_open_form','stat_delivery_good_count']
    X[num_col]=X[num_col].astype(float).fillna(0)
    
    # transform new variables and fill nan with 0
    new_num_col=['stat_order_money','stat_delivery_delivery_price',
             'stat_delivery_cod','stat_delivery_delivery_price_return',
             'stat_order_pay_webmaster','stat_delivery_delivery_production_costs']
    X[new_num_col]=X[new_num_col].astype(float).fillna(0)
    X['loss']=X.stat_order_pay_webmaster-X.stat_delivery_delivery_price-X.stat_delivery_delivery_price_return
    
    #print(np.unique(X.stat_order_time_before_open_form))
    #print(np.unique(X.stat_delivery_delivery_price))
    #print(np.unique(X.stat_delivery_cod))
    #print(np.unique(X.stat_delivery_delivery_price_return))
    #print(np.unique(X.stat_order_pay_webmaster))
    #print(np.unique(X.stat_delivery_delivery_production_costs))    
    #print(np.unique(X.loss))    

    bin_col=['stat_order_processed_user_id',#'stat_order_confirmed_user_id',
             'stat_order_operator_id','stat_order_phone_geocoder',
             'stat_order_webmaster_id','stat_order_landing_id',
             'stat_delivery_exception']
    # WOE-binning transformation of required columns
    #woe_model=ce.WOEEncoder(cols=woe_col,handle_unknown='value').fit(X,y)
    # Binary coding
    bin_model=ce.BinaryEncoder(cols=bin_col,handle_unknown='value').fit(X)
    X=bin_model.transform(X)
    print(X.shape)
    # Save model
    pickle.dump(bin_model, open('/workspace/app/triplet_v2/sd/bin_model.sav', 'wb'))
    
    dummy_col=['stat_order_is_prepay','stat_order_unique_goods','stat_order_created_ts',
               'stat_order_confirmed_ts','stat_order_country','stat_order_country_ip',
               'stat_order_country_phone','stat_order_phone_valid','stat_order_is_call_fail',
               'stat_order_valid_error','stat_order_offer_id','stat_order_landing_currency',
               'stat_order_account_manager_id','stat_delivery_operator_status',
               'stat_delivery_google_and_operator_address_match','stat_order_prelanding_id']
    dummy_model=ce.OneHotEncoder(cols=dummy_col,handle_unknown='value').fit(X)
    X=dummy_model.transform(X)
    print(X.shape)
    # Save model
    pickle.dump(dummy_model, open('/workspace/app/triplet_v2/sd/dummy_model.sav', 'wb'))           
    
    # Fixing all Nan and nan values in numeric format
    nan_model = impute.SimpleImputer().fit(X)
    X = nan_model.transform(X)
    # save to file this model
    pickle.dump(nan_model, open('/workspace/app/triplet_v2/sd/nan_model.sav', 'wb'))

    # Scaling
    # Now we have 212 features and try to robust normalize all of them
    nrm_model = preprocessing.RobustScaler().fit(X)
    X = nrm_model.transform(X)
    # save this model to the file
    pickle.dump(nrm_model, open('/workspace/app/triplet_v2/sd/nrm_model.sav', 'wb'))
    return X

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Variable's preprocessing for forecasting
def preproc_X(X):
    if not os.path.exists('/workspace/app/triplet_v2/sd'):
        os.mkdir('/workspace/app/triplet_v2/sd')
    # fill all nan
    X=X.fillna('nan')
    # extract only hours from stat_order_created_ts
    X.stat_order_created_ts=extr_hours(X.stat_order_created_ts).copy()
    #X.stat_order_created_ts.unique()
    # extract only hours from stat_order_confirmed_ts
    X.stat_order_confirmed_ts=extr_hours(X.stat_order_confirmed_ts).copy()
    # Numeric transformation and replace nan with 0
    num_col = ['stat_order_money','stat_order_count_call',
               'stat_order_count_callback','stat_order_good_count',
               'stat_order_time_before_open_form','stat_delivery_good_count']
    X[num_col]=X[num_col].astype(float).fillna(0)
    
    # transform new variables and fill nan with 0
    new_num_col=['stat_order_money','stat_delivery_delivery_price',
             'stat_delivery_cod','stat_delivery_delivery_price_return',
             'stat_order_pay_webmaster','stat_delivery_delivery_production_costs']
    X[new_num_col]=X[new_num_col].astype(float).fillna(0)
    X['loss']=X.stat_order_pay_webmaster-X.stat_delivery_delivery_price-X.stat_delivery_delivery_price_return    
    
    bin_model=pickle.load(open('/workspace/app/triplet_v2/sd/bin_model.sav', 'rb'))
    X=bin_model.transform(X)
    dummy_model=pickle.load(open('/workspace/app/triplet_v2/sd/dummy_model.sav', 'rb'))
    X=dummy_model.transform(X)
    si_model=pickle.load(open('/workspace/app/triplet_v2/sd/nan_model.sav', 'rb'))
    X = si_model.transform(X)
    nrm_model = pickle.load(open('/workspace/app/triplet_v2/sd/nrm_model.sav', 'rb'))
    X = nrm_model.transform(X)
    return X


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Forecast using list of files
def proc_predict(input_folder='/workspace/app/triplet_v2/train_data', 
                 col_name_file='/workspace/app/triplet_v2/sd/col_names.npz', 
                 dnn_file='/workspace/app/triplet_v2/sd/dnn_model.pth',
                 out_folder='/workspace/app/triplet_v2/forecasts'):
    print("The prediction has been started...")
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    # get all files    
    list_files = glob.glob(input_folder+'/*.csv')
    # the main cycle
    for i in range(len(list_files)):
        file_name = list_files[i]
        print("Processing file",file_name,"...")
        # load the source data set
        df=pd.read_csv(filepath_or_buffer=file_name,sep=';',header=0,dtype=str)
        y = np.zeros(df.shape[0])
        y[y==0]=np.nan        
        if 'stat_delivery_is_paid' in df.columns.values and 'stat_order_confirmed_user_id' in df.columns.values:
            y = crt_outcome(df['stat_delivery_is_paid'].values,df['stat_order_confirmed_user_id'].values)        
        X=df.copy()
        # replace all nan and null to '0'
        #col_names=pickle.load(open(col_name_file, 'rb'))
        col_names = np.load(col_name_file, allow_pickle = True)
        col_names = col_names['col_names']        
        # check required column names
        flag=np.invert(check_cn(col_names,X.columns))
        if np.sum(flag)!=0:
            print("The file:",file_name)
            print("Some required variables are absent in the data set!")
            print(col_names[flag])
            continue
        # select the required columns
        X = X[col_names]
        # transform predictor matrix
        X = preproc_X(X)
        # load DNN
        model =dnn.DNN_ClassifierM(X.shape[1])
        # Load pretrained waights
        model.load_state_dict(torch.load(dnn_file))
        # Set model to eval mode
        model.eval()
        # Transform to tensor
        X=torch.from_numpy(np.array(X))
        X=X.float()
        # Get predictions for loaded data set
        with torch.no_grad():
            pr_log_prob = model(X)
            pr_prob = pr_log_prob.exp().detach()
            pr_prob, pr = torch.max(pr_prob,1) # get classes            
            df['profitability'] = np.array(df['stat_order_money'].values,dtype=np.float)-(
                np.array(df['stat_delivery_delivery_price'].values,dtype=np.float)+
                np.array(df['stat_delivery_delivery_price_return'].values,dtype=np.float)+
                np.array(df['stat_delivery_delivery_production_costs'].values,dtype=np.float)+
                np.array(df['stat_delivery_cod'].values,dtype=np.float)+
                np.array(df['stat_order_pay_webmaster'].values,dtype=np.float))
            df['outcome']=y.astype(np.int)
            df['outcome_pred']=pr.detach().numpy().astype(np.int)
            df['outcome_prob']=np.round(pr_prob.detach().numpy(),3)
        df.to_csv(out_folder+'/'+os.path.basename(file_name), index=False)
    return True
    

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Validation using list of files
def proc_validation(list_files=[], 
                    col_name_file='/workspace/app/triplet_v2/sd/col_names.npz', 
                    dnn_file='/workspace/app/triplet_v2/sd/dnn_model.pth', 
                    out_file='/workspace/app/triplet_v2/results_cm.txt',
                    verb = True):
    print("The validation has been started...")
    if os.path.exists(out_file):
        os.remove(out_file)        
    min_prec=100
    min_ac=100
    # the main cycle
    for i in range(len(list_files)):
        file_name = list_files[i]
        if verb==True:
            print("Processing file",file_name,"...")
        # load the source data set
        df=pd.read_csv(filepath_or_buffer=file_name,sep=';',header=0,dtype=str)
        #print(df.shape)
        # split predictors and response
        #X=df.drop(['stat_delivery_is_paid'],axis=1)
        #y=df['stat_delivery_is_paid'].values
        # create responce
        y = crt_outcome(df['stat_delivery_is_paid'].values,df['stat_order_confirmed_user_id'].values)
        unique_y, counts_y = np.unique(y, return_counts=True)
        if verb == True:
            print("Class statistics:",dict(zip(unique_y.astype(int), counts_y)))        
        X=df.copy()
        del df
        # replace all nan and null to '0'
        #col_names=pickle.load(open(col_name_file, 'rb'))
        col_names = np.load(col_name_file, allow_pickle = True)
        col_names = col_names['col_names']        
        # check required column names
        flag=np.invert(check_cn(col_names,X.columns))
        if np.sum(flag)!=0:
            print("The file:",file_name)
            print("Some required variables are absent in the data set!")
            print(col_names[flag])
            continue
        # select the required columns
        X = X[col_names]
        # transform predictor matrix
        X = preproc_X(X)
        # load DNN
        model =dnn.DNN_ClassifierM(X.shape[1])
        # Load pretrained waights
        model.load_state_dict(torch.load(dnn_file))
        # Set model to eval mode
        model.eval()
        # Transform to tensor
        X=torch.from_numpy(np.array(X))
        X=X.float()
        # Get predictions for loaded data set
        with torch.no_grad():
            pr_log_prob = model(X)
            pr_prob = pr_log_prob.exp().detach()
            _, pr = torch.max(pr_prob,1) # get classes
        # Get confusion matrix
        cm=confusion_matrix(y, pr)
        pcm=np.round(100*cm/(1e-3+np.sum(cm,axis=0)),1)
        ac=np.round(100*accuracy_score(y,pr),1)
        #print(pcm)
        # print to file  
        with open(out_file, 'a') as f:
            print('File name:',list_files[i], file=f)
            print("\nConfusion matrix:", file=f)
            print(cm, file=f)
            print("\nConfusion matrix in %:", file=f)
            print(pcm, file=f)
            print("\n", file=f)
        c_min_prec=np.min(np.diag(pcm)) # current min precision
        if c_min_prec<min_prec:
            min_prec=c_min_prec
            min_ac=ac
    print("\n")
    return [min_prec,min_ac]

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# create responce
def crt_outcome(y1,y2):
    # the paid status
    y1[pd.isna(y1)]=0; y1[pd.isnull(y1)]=0
    y1=y1.astype(int)
    # the confirmed status
    y2[pd.isna(y2)]=0; y2[pd.isnull(y2)]=0
    y2=np.array(y2).astype(int)
    y2[y2!=0]=1
    # set all class = 0
    y = np.ones(y1.shape[0])
    # set 0 when stat_delivery_is_paid=0 and stat_order_confirmed_user_id=0
    y[(y1==0)&(y2==0)]=0
    # set 1 when stat_delivery_is_paid=1 and stat_order_confirmed_user_id=1
    y[(y1==1)&(y2==1)]=1
    # set 2 when stat_delivery_is_paid=0 and stat_order_confirmed_user_id=1
    y[(y1==0)&(y2==1)]=2
    # set 3 when stat_delivery_is_paid=1 and stat_order_confirmed_user_id=0
    y[(y1==1)&(y2==0)]=3
    return y
    


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Data transformation ('train.csv'), '/workspace/app/triplet_v2/sd/train_data.npz'
def trans_data(train_folder='/workspace/app/triplet_v2/train_data',
               col_name_file='/workspace/app/triplet_v2/sd/col_names.npz', 
               out_data_file='/workspace/app/triplet_v2/sd/train_data.npz'):
    print("The data transformation has been started...")
    print("Aggregation all files...")
    train_files = glob.glob(train_folder+'/*.csv')
    if len(train_files)==0:
        print("Train files have not found!")
        sys.exit()    
    time.sleep(0.1)
    df=pd.DataFrame() # все запросы здесь
    with progressbar.ProgressBar(max_value=len(train_files)) as bar:  
        for i in train_files:
            c_df = pd.read_csv(filepath_or_buffer=i,
                            sep=';',dtype=str,encoding = 'UTF-8')
            if df.shape[0]==0:
                df=c_df
            else:
                df = pd.concat([df,c_df],axis=0)
    df.reset_index(drop=True, inplace=True)
    print(df.shape)
    #print(X.columns.values)
    
    #nc=['stat_order_money_eur','stat_delivery_delivery_price',
    #    'stat_delivery_cod','stat_delivery_delivery_price_return',
    #    'stat_order_pay_webmaster','stat_delivery_delivery_production_costs']
    #res=[i in df.columns.values for i in nc]
    #print(res)    
    
    # create triplet response
    y = crt_outcome(df['stat_delivery_is_paid'].values,df['stat_order_confirmed_user_id'].values)

    #df.head()
    # save all column names for check them with new data
    # delete unuseful columns
    del_col=['stat_delivery_is_paid','stat_order_confirmed_user_id','order_id', 'stat_order_region','stat_order_callback_ts',
             'stat_order_city', 'stat_order_delivery_price', 'stat_order_payment_method', 
             'stat_delivery_delivery_status', 'stat_delivery_manager_id', 'stat_delivery_is_return',
             'stat_delivery_finance_revise_ts', 'stat_delivery_discount', 'stat_delivery_discount_eur', 
             'stat_order_landing_price','stat_delivery_in_stock_ts', 'stat_delivery_cancel_in_stock_ts',
             'stat_delivery_paid_ts','stat_delivery_return_ts','stat_order_last_call_ts',
             'stat_order_phone_id','stat_order_lead_ts','stat_order_rejection_reason','stat_order_invalid_reason',
             'stat_order_status_order','stat_order_is_valid',
             'stat_order_utm_source','stat_order_utm_medium','stat_order_utm_campaign',
             'stat_order_utm_content','stat_order_utm_term','order_client_name','order_client_surname',
             'order_client_additional_phone','order_client_age','order_client_age_unknown',
             'order_client_sex','order_address_country','order_address_region','order_address_city',
             'order_address_street','order_address_house','order_address_housing','order_address_apartment',
             'order_address_zip_code']
    X=df.drop(del_col,axis=1)
    del df
    print('Initial shape',X.shape)
    #print(X.columns.values)    
    #nc=['stat_order_money','stat_delivery_delivery_price',
    #    'stat_delivery_cod','stat_delivery_delivery_price_return',
    #    'stat_order_pay_webmaster','stat_delivery_delivery_production_costs']
    #print(X['stat_delivery_delivery_price_return'])
    #res=[i in X.columns.values for i in nc]
    #print(res)
    # save initial colnames
    col_names=X.columns.values
    X = preproc_new_X(X)
    # save the final preprocessed data set
    np.savez_compressed(out_data_file,X=X,y=y.astype(float))
    np.savez_compressed(col_name_file,col_names=col_names)
    unique_y, counts_y = np.unique(y, return_counts=True)
    print(dict(zip(unique_y, counts_y)))
    return True
