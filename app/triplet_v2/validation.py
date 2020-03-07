# -*- coding: utf-8 -*-
"""
Осуществляет валидацию по заданным файлам с расчетом Confusion matrix для
каждого файла. Информация заносится в файл results_cm.txt.

Для примера, обучающие данные также включены в набор файлов.

"""
import main_functions as mf

# list validation files
list_files=['/workspace/app/triplet_v2/val_data/real_2019-10-03-2019-10-03_not-system-wm_5dee1d0c5dc0e.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-04-2019-10-04_not-system-wm_5dee1d16b2cb7.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-05-2019-10-05_not-system-wm_5dee1d1d9e8ac.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-06-2019-10-06_not-system-wm_5dee1d2646b77.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-07-2019-10-07_not-system-wm_5dee1d30144e6.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-08-2019-10-08_not-system-wm_5dee1d38b66bd.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-09-2019-10-09_not-system-wm_5dee1d3fb625a.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-10-2019-10-10_not-system-wm_5dee1d471b45d.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-11-2019-10-11_not-system-wm_5dee1d4e1508e.csv',
            '/workspace/app/triplet_v2/val_data/real_2019-10-12-2019-10-12_not-system-wm_5dee1d542ae07.csv',
            '/workspace/app/triplet_v2/train_data/real_2018-01-01-2019-09-30_confirmed_not-system-wm_5de4f9c13d9fe.csv']

res=mf.proc_validation(list_files=list_files)
print("The minimum precision of one class among all files:",res[0],"%")
print("The relative accuracy:",res[1],"%")
