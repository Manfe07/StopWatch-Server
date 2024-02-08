from flask import Flask, send_file, render_template, redirect
from flask_socketio import SocketIO, send, emit
from flask_migrate import Migrate
from tools import * 

import module_teams.teams as teams
import module_users.users as users
import module_sales.sales as sales

from database import db
import logging

import datetime
import time
import os
import configparser
import json

os.environ['TZ'] = "Europe/Berlin"
time.tzset()

config = configparser.ConfigParser()
config.read('config.ini')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)



app = Flask(__name__) 

app.config['SECRET_KEY'] = config['Flask']['SECRET_KEY']
socketio = SocketIO(app, cors_allowed_origins='*')

app.register_blueprint(teams.teams_Blueprint, url_prefix="/teams")
app.register_blueprint(users.users_Blueprint, url_prefix="/users")
app.register_blueprint(sales.sales_Blueprint, url_prefix="/sales")

app.config['SQLALCHEMY_DATABASE_URI'] = config['Flask']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

migrate = Migrate(app, db)

with app.app_context():
    db.init_app(app)
    db.create_all()
    teams.init()
    users.init()
    sales.init()
    db.session.commit()


@app.route('/',methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/startpanel',methods = ['GET'])
def startPanel():
    return render_template('startPanel.html')

@app.route('/finishpanel',methods = ['GET'])
def finishPanel():
    return render_template('finishPanel.html')

@app.route('/stoppanel',methods = ['GET'])
def stopPanel():
    return render_template('stopPanel.html')

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('ping')
def handle_ping(data):
    data["pong"] = datetime.datetime.now().timestamp()
    emit('pong', data, broadcast=False)


stopwatchData = {
    'running': False,
    'armed': False,
    'activeLanes': 3,
    'startTime' : None,
    'finishTime' : [],
    'laneFinished' : []
}

@socketio.on('stopwatch')
def handle_stopwatch(data):
    print('received stopwatch message:')
    logger.debug(data["data"])
    action = data["data"]["action"]
    lane = data["data"]["lane"]
    value = data["data"]["value"]

    if action == "start":
        if ((not stopwatchData['running']) and stopwatchData['armed']):
            stopwatchData['running'] = True
            stopwatchData['armed'] = False
            stopwatchData['startTime'] = value
            stopwatchData['finishTime'] = [None] * stopwatchData['activeLanes']
            stopwatchData['laneFinished'] = [False] * stopwatchData['activeLanes']
        else:
            logger.error("unable to start race")

    if action == "stop":
        if (stopwatchData['running'] and stopwatchData['laneFinished'][lane] == False):
            stopwatchData['finishTime'][lane] = value
            stopwatchData['laneFinished'][lane] = True
        else:
            logger.error("unable to finish Lane ", lane)
        
        tmpFinish = True
        for laneFinished in stopwatchData['laneFinished']:
            if laneFinished == False:
                tmpFinish = False
        
        if tmpFinish:
            stopwatchData["running"] = False
            stopwatchData["armed"] = False

    if action == "reset":
        #if (stopwatchData['running'] == False):
        stopwatchData['running'] = False
        stopwatchData['armed'] = False
        stopwatchData['startTime'] = None
        stopwatchData['finishTime'] = [None] * stopwatchData['activeLanes']
        stopwatchData['laneFinished'] = [False] * stopwatchData['activeLanes']
        
    if action == "arm":
        if (not stopwatchData['running']):
            stopwatchData['armed'] = value

    if action == "setLanes":
        if (not stopwatchData['running'] and not stopwatchData["armed"]):
            stopwatchData['activeLanes'] = int(value)

    data["data"]["serverTime"] = datetime.datetime.now().timestamp()
    logger.debug(stopwatchData)
    emit('stopwatchServer', stopwatchData, broadcast=True)

@socketio.on('logResult')
def handle_logResult(data):
    #emit('stopwatchServer', stopwatchData, broadcast=True)
    logger.info(data)
    return simpleChecksum(json.dumps(data))

@socketio.on('get_stopwatch')
def handle_getStopwatch(data):
    emit('stopwatchServer', stopwatchData, broadcast=True)

@socketio.on('chatMessage')
def handle_chatMessage(data):
    emit('chatMessage', data, broadcast=True)

@socketio.on('connect')
def test_connect(auth):
    emit('my_response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# main driver function
if __name__ == '__main__':
    app.run()

