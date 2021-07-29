import flask
from flask_cors import CORS

import os
import json
import glob
from collections import defaultdict

import annotator
import reader 
import writer 
import numpy as np
import pandas as pd
import string
import random


application = flask.Flask(__name__)
CORS(application) # TODO : Remove before deployment

anne = annotator.Annotator(reader.get_reader('xml'), writer.get_writer('csv'))

"""
Display the main page.
"""
@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

def is_new_user(userid):
    """
    Determine if this individual is a new user
    """
    path = './data/order/order_{}.txt'.format(userid)
    return not(os.path.exists(path))

def gen_new_ordering_list(doc_id, userid):
    """
    A new user has come to the field. Assign them N articles. Ensure to not pick
    articles that have/will be annotated M times. 
    """      
    path = './data/order/order_{}.txt'.format(userid)
    if is_new_user(userid):
        np.savetxt(path, [int(doc_id)], fmt = '%d')
    
"""
Go to Instructions
"""
@application.route('/start/', methods=['GET', 'POST'])
def start():
    if 'userid' in flask.request.form :
        userid = flask.request.form['userid']
    elif 'userid' in flask.request.args :
        userid = flask.request.args['userid']
        assignmentId = flask.request.args.get('assignmentId', None)
        hitId = flask.request.args.get('hitId', None)
        doc_id = flask.request.args.get('docId', None)
        userid = userid + '.' + assignmentId + '.' + hitId + '.' + str(doc_id)

    return flask.render_template('instructions.html', userid=userid, docid=doc_id)
                
"""
Start the program.
"""
@application.route('/start_annotate/', methods=['POST'])
def start_annotate():
    userid = flask.request.form['userid']
    doc_id = flask.request.form['docid']
    gen_new_ordering_list(doc_id, userid)
    id_ = anne.get_next_file(userid)

    if id_ is None:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.redirect(flask.url_for('annotate_article', 
                                            userid = userid, 
                                            id_ = id_))
        
"""
Grabs a specified article and displays the full text.
"""                             
@application.route('/annotate_article/<userid>/<id_>/', methods=['GET'])
def annotate_article(userid, id_):
    id_ = id_ or anne.get_next_file(userid)
    art = anne.get_next_article(userid, id_)
    tabs = art.text[0:1]
    
    if not art:
        return flask.redirect(flask.url_for('finish'))

    return flask.render_template('annotate_article.html',
                                 userid = userid,
                                 id = art.id_,
                                 pid = id_,
                                 #offset = art.get_extra()['offset'],
                                 title = art.title,
                                 query = art.get_extra()['question'],
                                 tabs = tabs)

"""
Submits the article id with all annotations.
"""
@application.route('/submit/', methods=['POST'])
def submit():
    form = flask.request.form
    userid = form['userid']
    anne.submit_annotation(form)

    id_ = anne.get_next_file(userid)
    if not id_:
        return flask.redirect(flask.url_for('finish'))
    else:
        return flask.redirect(flask.url_for('annotate_article',
                                          userid = userid,
                                          id_ = id_))

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

"""
Only go to this if there are no more articles to be annotated.
"""
@application.route('/finish/', methods=['GET'])
def finish():
    survey_code = id_generator(8)
    return flask.render_template('finish.html', surveycode = survey_code)

"""
Run the application.
"""
if __name__ == '__main__':
#    application.run()
    application.run(host = '0.0.0.0', port = 8001, threaded=True) 
