# -*- coding: utf-8 -*-
"""
Данный модуль делает прогнозы на основе новых данных и пред-обученной 
нейронной сети. Если данные имеют истинный ответ stat_delivery_is_paid он
помещается рядом с прогнозом класса и его вероятностью в конце таблицы.

Для примера тренировочный набор данных также включен как файл данных для 
прогнозирования.


"""

import main_functions as mf

mf.proc_predict(input_folder='/workspace/app/triplet_v2/train_data')
mf.proc_predict(input_folder='/workspace/app/triplet_v2/val_data')

