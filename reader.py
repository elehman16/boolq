import abc
import csv
import os
import random
import sqlite3
import xml.etree.ElementTree as ET
import json
from get_file_description import get_file_description
from data.by_row_description import by_row_description
import numpy as np
from functools import reduce
import pandas as pd
from itertools import chain
import article
from bs4 import BeautifulSoup, NavigableString
import html

def load_text_doc(f):
        """ Load the train/dev/test file """
        with open(f) as tmp:
            data = tmp.read()
    
        return data

class Reader(object, metaclass=abc.ABCMeta):
    """Read article information.

    A base class for providing article information
    to be annotated by the user.
    """

    @abc.abstractmethod
    def get_next_article(self):
        """Gets the next article to be annotated."""
        raise NotImplementedError('Method `get_next_article` must be defined')

class XMLReader(Reader):
    """Read from XML files.

    A `Reader` implementation to read articles from XML files
    that are stored in a given path. Currently expects files to
    be of the form of an NLM article.
    """

    def __init__(self, path):
        self.path = path
        self.file_description   = get_file_description()
        self.by_row_description = by_row_description()

    """
    Given the path that leads to a folder of ONLY XML files, the function
    will pick one and then return the name of it.
    """
    def _get_next_file(self, user):
        fname = 'data/progress/{}.progress'.format(user)
        if not os.path.isfile(fname):
          with open(fname, 'w') as fout:
            fout.write('0')
        
        n = int(open(fname).read())
        ids = [l.strip() for l in open('data/order/order_{}.txt'.format(user)).readlines()]
        if n < len(ids):
          return ids[n]
    
        return None
    
    def _prepare_text_(self, node):
        cur_i = 0
        raw_text = ''
        def get_wrapped_string(s, extra_wrapper = None):
          nonlocal cur_i
          nonlocal raw_text
          raw_text += s
          i = cur_i
          f = cur_i + len(s)
          cur_i = f
          new_s = '<offsets txt_i="{}" txt_f="{}" xml_i="{}" xml_f="{}">{}</offsets>'.format( \
              i, f, i, f, s)
          if extra_wrapper:
            new_s = '<{}>{}</{}>'.format(extra_wrapper, new_s, extra_wrapper)
            
          return new_s

        def wrap_strings(node):
            node[0] = {
                'text': node[0],
                'html': get_wrapped_string(node[0])
                }
            if type(node[1]) == str:
                node[1] = get_wrapped_string(node[1], 'p')
            else:
                for sub_i, sub_node in enumerate(node[1]):
                    if type(sub_node) == str:
                        node[1][sub_i] = get_wrapped_string(sub_node, 'p')
                    elif type(sub_node) == list:
                        wrap_strings(sub_node)
        
        for n in node:
            wrap_strings(n)
            
        return node
        
    """
    Grabs a random XML article and displays it.
    If the next_file is not equal to 'None', then it will grab the full article.
    Otherwise, it will only display the abstract.
    """
    def get_next_article(self, user, next_file=None):
        next_file = next_file or self._get_next_file(self, user)
        if not next_file:
            return None
        
        # next_file will be a number which is equal to the idx of the test.json
        with open('./data/v6_test.json') as tmp:
            test = json.load(tmp)
            
        row = test[int(next_file)]
        
        title = row['title']
        # pull out the row
        path_to_file = './text_files/' + (row['location'].split('text/')[-1] + '_' + str(row['idx'])).replace('/', '_')
        text = load_text_doc(path_to_file)
        title = row['title']
        content = {'title': title, 'sections': [[title, []]] }
                   
        main_section = content['sections'][0]
        main_section_content = main_section[1]
        # split s into content. 
        split_s = [x + " " for x in text.split("\n")]
        for splitted in split_s:
            main_section_content.append(splitted)

        self._prepare_text_(self, content['sections'])
        art =  article.Article(next_file, title, content['sections'])
        art.get_extra()['question'] = row['question']
        return art
        
"""
Builder pattern for readers.
"""
def get_reader(reader):
    options = {
        'xml': XMLReader,
    }
    if reader in options:
        return options[reader]
    raise Exception('{0} not a valid reader.'.format(reader))
