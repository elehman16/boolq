# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 16:56:21 2019

@author: Eric Lehman
"""
import pandas as pd
import random
import json

# just extract possible articles 
with open('test-all-good-ids.json') as tmp:
    ids_1 = json.load(tmp)
    
# just extract possible articles 
with open('test-some-what-good.json') as tmp:
    ids_2 = json.load(tmp)

ids_ = ids_1 + ids_2 

all_prompts = list(range(len(ids_)))

random.shuffle(all_prompts)
all_prompts = all_prompts[:250]
with open('to_do.txt', 'w') as f:
    for item in all_prompts:
        f.write("%s\n" % item)
