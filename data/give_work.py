# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:04:11 2019

@author: Eric Lehman
"""

import glob
import random
import pandas as pd
import numpy as np
import os

def more_work(n, user):
    all_txt = glob.glob("./order/*.txt")
    all_txt.remove('test_article_ids.txt')
    all_txt.remove('to_do.txt')
    all_pmc_files = set()
    # Gets all of the files that we have done into a set
    for txt in all_txt:
        file_data = np.genfromtxt(txt, dtype = int)
        for pmc_file in file_data:
            all_pmc_files.add(pmc_file)
            
    # get the ones we need to do 
    to_do = np.genfromtxt('to_do.txt', dtype = int) 
    
    # Determines which PMC files we haven't done, and creates a list of N of them
    filtered_to_do = []
    for file_num in to_do:
        if not(file_num in all_pmc_files):
            filtered_to_do.append(file_num)
            
    random.shuffle(to_do)
    to_do = to_do[:n]
    
    for i in range(len(to_do)):
        print(to_do[i])    
       
    loc = "./order//order_" + user + ".txt"
    if os.path.exists(loc):
        done = np.loadtxt(loc, dtype = int)
    else:
        done = []
    new_list = np.append(done, to_do)
    np.savetxt(loc, new_list.astype(int), fmt = '%d')