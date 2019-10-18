from app.controllers import *
import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask
from flask_pymongo import PyMongo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import time

from app.utils import inserting as it

class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# create the flask object
app = Flask(__name__)

# add mongo url to flask config, so that flask_pymongo can use it to make connection
app.config['MONGO_URI'] = os.environ.get('DB')
mongo = PyMongo(app)

#Scheduler to update database every twenty minutes
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=it.insert_new_data,
    trigger=IntervalTrigger(minutes=20),
    id='updating_db_job',
    name='Update db every 20 minutes',
    replace_existing=True)
    
#Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder
