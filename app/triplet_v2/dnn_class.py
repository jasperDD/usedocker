# -*- coding: utf-8 -*-
"""
Данный модуль определяет структуру нейронной сети, 
прямое распространение сигнала,
оптимизируемую функцию


"""

import torch
import  torch.nn.functional as F
import torch.nn as nn
import numpy as np

def get_weights(y):
    # count unique values
    _, counts_y = np.unique(y, return_counts=True)
    class_weights = torch.FloatTensor(1.0 - counts_y/np.sum(counts_y))
    return class_weights
    


class DNN_ClassifierM(torch.nn.Module):
    def __init__(self,inp):
        super(DNN_ClassifierM, self).__init__()
        self.layer1 = nn.Sequential(
                nn.Linear(inp,132),
                nn.SELU(True))
        self.layer2 = nn.Sequential(
                nn.Linear(132,66),
                nn.SELU(True))
        self.layer3 = nn.Sequential(
                nn.Linear(66,66),
                nn.SELU(True))
        self.layer4 = nn.Sequential(
                nn.Linear(66,30),
                nn.SELU(True))
        self.layer5 = nn.Sequential(
                nn.Linear(30,15),
                nn.SELU(True),
                nn.AlphaDropout(p=0.3))
        self.layer6 = nn.Sequential(
                nn.Linear(15,4),
                nn.LogSoftmax(dim=1))
    # foward function    
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = x+self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        x = self.layer6(x)
        return x
