from flask import Flask, send_file, render_template
from flask_socketio import SocketIO, send, emit
from tools import * 

import logging

import datetime
import time
import os
import yaml
import json

os.environ['TZ'] = "Europe/Berlin"
time.tzset()


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/logs/app.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Flask(__name__) 

app.config['SECRET_KEY'] = 'o6HZY5rU2DsDYjkxcULztAaFm9gANikLdkFrDGmP57UgKctUMGmPjSFoD2h4re8UeaDq4gn85yUTKaR6KRf3jXHUhnFyEyc4UWG5WR!'
socketio = SocketIO(app, cors_allowed_origins='*')

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

