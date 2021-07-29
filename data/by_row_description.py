# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 20:14:47 2018

@author: Eric
"""
import pandas as pd
import numpy as np
import csv

def by_row_description():
    data = {}
    all_rows = pd.read_csv(csv_file_loc)
    all_rows = np.asarray(all_rows)
    
    labels = get_labels()
    #labels[0] = "id"
    for i in range(1, len(all_rows)):
        row = all_rows[i]
        name = row[labels.index('Unnamed: 0')] # the name of the PMC file
        if (name == 'Unnamed: 0'):
            continue
        if name in data:
            data[int(name)].append(gen_row_dictionary(labels, row))
        else:
            data[int(name)] = [gen_row_dictionary(labels, row)]
    
    return data
    

#csv_file_loc = './/data//for-full-text-annotation.csv'
csv_file_loc = './/data//prompt_gen.csv'


"""
Read in the CSV file and get the required data from it. Format the data.
"""

"""
Get the lables/headers for each column.
""" 
def get_labels():
    with open(csv_file_loc, newline = '') as csvfile:
        for row in csv.reader(csvfile, delimiter = ",", quotechar='|'):
            return row
        
        
    
"""
Take a row and put all the data into a dictionary.

@param labels represents the name of that column and what type of data it is.
@param row represents all the data in that row.
"""
def gen_row_dictionary(labels, row):
    data = {}
    for i in range(len(labels)):
        data[labels[i]] = row[i]
    return data
    
