''' controller and routes for users '''
import os
from flask import request, jsonify
from app import app, mongo
import logger

from app.utils import inserting as it
from app.utils import processing 


#import utils
# import db schema and functions accordingly

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))

@app.route('/raw', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# Utilze the functions from the utils/processed.py
# utilize the functions defined inside models/manage.py
# And then send a response accordingly
def raw_all():
    if request.method == 'GET':
        coll = mongo.db.meta
        for doc in coll.find():
            channel_id = doc['channel_id']
            raw_one(channel_id)    
    return 200      

@app.route('/raw/<id>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# Utilze the functions from the utils/processed.py
# utilize the functions defined inside models/manage.py
# And then send a response accordingly
def raw_one(reference_id, limit=None):
    if request.method == 'GET':
        data = it.download_channel_db(mongo.db.raw, reference_id, limit)
    return data


@app.route('/processed', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# Utilze the functions from the utils/processed.py
# utilize the functions defined inside models/manage.py
# And then send a response accordingly
def processed_all():

    if request.method == 'GET':
        coll = mongo.db.meta
        for doc in coll.find():
            channel_id = doc['channel_id']
            processed_one(channel_id)    
    return 200

@app.route('/processed/<id>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# Utilze the functions from the utils/processed.py
# utilize the functions defined inside models/manage.py
# And then send a response accordingly
def processed_one(reference_id, limit=None):
    if request.method == 'GET':
        data = it.download_channel_db(mongo.db.processed, reference_id, limit)
    return data
