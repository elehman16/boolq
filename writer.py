import abc
import json
import csv
from pathlib import Path
import pandas as pd
import numpy as np
import os

convert = lambda row:  './text_files/' + (row['location'].split('text/')[-1] + '_' + str(row['idx'])).replace('/', '_')

class Writer(object, metaclass=abc.ABCMeta):
    """Write annotation information.

    A base class for writing annotation information
    out after the article has been annotated by
    the user.
    """

    @abc.abstractmethod
    def submit_annotation(self, id_, annotations):
        """Submits an annotation."""
        raise NotImplementedError('Method `submit_annotation` must be defined')

    @abc.abstractmethod
    def get_results(self):
        """Returns results of project."""
        raise NotImplementedError('Method `get_results` must be defined')


class CSVWriter(Writer):
    """Write to CSV files.

    A `Writer` implementation that writes annotation
    information out to a CSV file. If multiple annotations
    for a single article are provided, they are entered
    in separate columns.

    Writes to CSV in form:
    article_id, annotation1, annotation2, ...
    """

    def __init__(self, write_file):
        self.write_file = write_file
        
    def invalid(self, user, id_, pmcid, reason):
        to_add = [[ id_, pmcid, 'N/A', reason, -1, -1, False]]
        df_add = pd.DataFrame(to_add, columns = ['PMCID', 'ID', 'Label', 'Selected Text', 'Start', 'End', 'Valid Prompt'])
        
        path = './/all_outputs//out_{}.csv'.format(user)
        df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame([], columns = ['PMCID', 'ID', 'Label', 'Selected Text', 'Start', 'End', 'Valid Prompt'])
        df_final = df.append(df_add, ignore_index=True)     
        df_final.to_csv(path, index = False)

    def submit_annotation(self, data):                               
        id_ = data['id']
        if 'type' in data and data['type'] == 'Invalid Prompt':
            name_ = data['pid']
            with open('./data/v6_test.json') as tmp:
                test = json.load(tmp)
            
            loc = convert(test[int(name_)])
            self.invalid(self, data['userid'], loc, id_, data['reason'])
            self.update_user_progress(self, data['userid'])
            return None
        
        to_save = json.loads(data['corefs'])['i']
        label   = data['label']
        to_add = []
        name_ = data['pid']
        title = data['title'].strip()
        with open('./data/v6_test.json') as tmp:
            test = json.load(tmp)

        loc = convert(test[int(name_)])
        for key in to_save.keys():
            for s in to_save[key]['spans']:
                start = int(s['i']) 
                end   = int(s['f'])

                to_add.append([loc, name_, label, s['txt'], int(start) - len(title), int(end) - len(title), True])
                
        df_add = pd.DataFrame(to_add, columns = ['PMCID', 'ID', 'Label', 'Selected Text', 'Start', 'End', 'Valid Prompt'])
        
        path = './/all_outputs//out_{}.csv'.format(data['userid'])
        df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame([], columns = ['PMCID', 'ID', 'Label', 'Selected Text', 'Start', 'End', 'Valid Prompt'])
        df_final = df.append(df_add, ignore_index=True)     
        df_final.to_csv(path, index = False)
        self.update_user_progress(self, data['userid'])
       
    """
    Call this method when the user has finished annotating something. This 
    incriments the persons progress on work!
    """
    def update_user_progress(self, user):
      fname = 'data/progress/{}.progress'.format(user)
      n = int(open(fname).read())
      with open(fname, 'w') as fout:
        fout.write(str(n+1))



class SQLiteWriter(Writer):
    """Write to a SQLite database.

    A `Writer` implementation to support writing
    annotation data out to a database. If multiple
    annotations exist for one Article, they will
    be entered as separate rows in the database.

    Expects columns of form:
    article_id, annotation
    """

    def __init__(self, db_file, table):
        self.db_file = db_file
        self.table = table
        self.conn = sqlite3.connect(self.db_file)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.current_pos = 0

    def submit_annotation(self, id_, annotations):
        for annotation in annotations:
            self.cursor.execute('INSERT INTO {0} VALUES({1}, {2})' \
                                .format(self.table, id_, annotation))
        self.cursor.commit()

    def get_results(self):
        self.cursor.execute('SELECT * FROM {0}'.format(self.table))
        rows = self.cursor.fetchall()
        return json.dumps(rows)


def get_writer(writer):
    options = {
        'csv': CSVWriter,
        'sql': SQLiteWriter,
    }
    if writer in options:
        return options[writer]
    raise Exception('{0} not a valid writer.'.format(writer))
