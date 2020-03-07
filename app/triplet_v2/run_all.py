# -*- coding: utf-8 -*-
"""
Данный модуль запускает последовательно все необходимые скрипты для:
    
    1) препроцессинга данных
    2) обучения нейронной сети
    3) прогнозирования

@author: luzgin
"""

import main_functions as mf
import glob

# Data preprocession
mf.trans_data()
# Train DNN
mf.train_dnn(num_epochs=10) #DEBUG 10 
# Validation DNN
val_files = glob.glob('/workspace/app/triplet_v2/val_data'+'/*.csv')
train_files = glob.glob('/workspace/app/triplet_v2/train_data'+'/*.csv')
res=mf.proc_validation(list_files=val_files+train_files)
print("The minimum precision of one class among all files:",res[0],"%")
# Forecast based on DNN
mf.proc_predict(input_folder='/workspace/app/triplet_v2/train_data')
mf.proc_predict(input_folder='/workspace/app/triplet_v2/val_data')
print("All operations have been done!")


