import { socket, watchDog, wsData } from "/static/scripts/socket.js";

//export var customUpdateFunction = function () {}

//export var customDisplayFunction = function () {}



function simpleChecksum(data) {
    let checksum = 0;
    console.debug("Checksum data:", data);
    if (data.length) {
        for (let i = 0; i < data.length; i++) {
            checksum += data.charCodeAt(i);
        }
        return checksum % 256;
    }
    else
        return 0;
}


socket.on('stopwatchServer', function (msg, cb) {
    console.debug('StopwatchDataReceived:');
    console.debug(msg);
    if (stopwatch.masterClock) {
        if (!stopwatch.running) {
            stopwatch.data = stopwatch.convertDataFromServer(msg);
        }
    }
    else {
        stopwatch.data = stopwatch.convertDataFromServer(msg);
    }
    stopwatch.tick();
    stopwatch.customUpdateFunction();

    if (cb)
        cb();
});


export class Stopwatch {
    constructor() {
        this.data = {
            running: false,
            armed: false,
            activeLanes: 3,
            startTime: null,
            finishTime: [],
            laneFinished: []
        }
        this.duration = [0.0, 0.0, 0.0];
        this.elapsedTime = 0;
        this.masterClock = false;
        this.connectionLost = false;
        this.dataBuffer = [];
        this.customUpdateFunction = function () { }
        this.customDisplayFunction = function () { }
        this.customResetFunction = function (raceAborted) { }
        this.customStopFunction = function (lane) { }
    }

    init() {
        this.reset(false);
        console.log("Stopwatch: init finished");
    }

    start() {
        let now = new Date().valueOf();
        if (this.data.armed & !this.data.running) {
            //this.reset();
            this.data.running = true;
            this.data.startTime = now;
            this.data.armed = false;
            this.customUpdateFunction();
            this.tick();

            wsData.value = this.data.startTime + wsData.timeDif;
            wsData.action = "start";
            wsData.lane = 0;
            socket.emit('stopwatch', { data: wsData });
            console.log("Start");
            return true;
        }
        else {
            return false;
        }
    }

    stopLane(lane) {
        //console.log("Stop Lane:", lane);
        let now = new Date().valueOf();
        if (this.data.running & (this.data.laneFinished[lane] != true)) {
            this.data.finishTime[lane] = now;
            this.data.laneFinished[lane] = true;
            wsData.value = this.data.finishTime[lane] + wsData.timeDif;
            wsData.action = "stop";
            wsData.lane = lane;
            socket.emit('stopwatch', { data: wsData });
            //console.log("Stoped Lane:", lane);

            this.customStopFunction(lane);

            var tmpFinish = true;
            for (var i = 0; i < this.data.laneFinished.length; i++) {
                console.debug("Check Lane:", i)
                if (this.data.laneFinished[i] != true) {
                    tmpFinish = false;
                    console.debug("Check unfinish Lane:", i);
                }
                console.debug("tmp:", tmpFinish);
            }
            if (tmpFinish) {
                if (this.masterClock) {
                    wsData.value = this.convertDataForServer();
                    wsData.action = "masterFinish";
                    wsData.lane = 0;
                    socket.emit('stopwatch', { data: wsData });
                }
                this.data.running = false;
                this.data.armed = false;
                this.dataBuffer.push(
                    this.convertDataForServer()
                );
                this.uploadResult();
            }
            this.customUpdateFunction();
            return true;
        }
        else {
            return false;
        }
    }

    uploadResult() {
        if (this.masterClock) {
            if (this.dataBuffer.length > 0) {
                socket.emit('logResult', this.dataBuffer[0], (response) => {
                    //console.debug("logResponse: ", response);
                    //console.debug("selfCheck:", simpleChecksum(JSON.stringify(this.dataBuffer[0])));
                });

                //ToDo: upload data and wait for response
                this.dataBuffer.splice(0, 1);
                if (this.dataBuffer.length > 0) {
                    setTimeout(uploadResult, 500);
                }
                return true;
            }
            else {
                return false;
            }
        }
        else {
            return false;
        }
    }


    setActiveLanes(count) {
        if (!this.data.running & !this.data.armed) {
            this.data.activeLanes = count;
            wsData.value = this.data.activeLanes;
            wsData.action = "setLanes";
            wsData.lane = 0;
            socket.emit('stopwatch', { data: wsData });
            this.reset();
            return true;
        }
        else {
            return false;
        }
    }

    toggleArm() {
        if (!this.data.running) {
            //console.log("laneFinished.length", this.data.laneFinished.length);
            //console.log("startTime", this.data.startTime);
            if (this.data.startTime != null) {
                this.reset();
            }
            if (this.data.laneFinished.length != this.data.activeLanes) {
                this.reset();
            }
            this.data.armed = !this.data.armed;
            wsData.value = this.data.armed;
            wsData.action = "arm";
            wsData.lane = 0;
            socket.emit('stopwatch', { data: wsData }) // ok);
            this.customUpdateFunction();
            return true;
        }
        else {
            return false;
        }
    }

    // Reset the Stopwatch
    reset(resetOnline = true) {
        //console.log("Reset:")
        if (this.data.running) {
            // ToDo: handle what to do when active race is canceld
            wsData.value = true;
            this.customResetFunction(true);
        }
        else {
            wsData.value = false;
            this.customResetFunction(false);
        }

        this.data.running = false;
        this.data.armed = false;
        this.data.startTime = null;

        this.data.finishTime = [];
        this.data.laneFinished = [];
        this.duration = [];

        for (let i = 0; i < this.data.activeLanes; i++) {
            this.data.finishTime[i] = null;
            this.data.laneFinished[i] = false;
            this.duration[i] = 0;
        }

        //console.log("StopWatchData: ", stopwatch.data);
        //console.log("");

        this.customUpdateFunction();
        wsData.action = "reset";
        wsData.lane = 0;
        if (resetOnline) {
            socket.emit('stopwatch', { data: wsData });
        }
    }

    tick() {
        if (this.data.running) {
            let now = new Date();
            this.elapsedTime = now - this.data.startTime;
            for (let i = 0; i < this.data.activeLanes; i++) {
                if (this.data.laneFinished[i] != true)
                    this.duration[i] = this.elapsedTime;
                else
                    this.duration[i] = this.data.finishTime[i] - this.data.startTime;
            }
            this.customDisplayFunction();
            requestAnimationFrame(() => this.tick());
        }
    }

    convertDataForServer() {
        var tmpData = this.data;

        if (tmpData.startTime != null)
            tmpData.startTime = tmpData.startTime + wsData.timeDif;
        for (let i = 0; i < tmpData.finishTime.length; i++) {
            if (tmpData.finishTime[i] != null)
                tmpData.finishTime[i] = tmpData.finishTime[i] + wsData.timeDif;
        }

        console.debug("Convert For Server");
        console.debug("timeDif: ", wsData.timeDif);
        console.debug("StopWatchData: ", this.data);
        console.debug("ServerData: ", tmpData);
        console.debug("");

        return tmpData;
    }

    convertDataFromServer(tmpData) {
        console.debug("Convert From Server");
        console.debug("timeDif: ", wsData.timeDif);
        console.debug("ServerData: ", tmpData);
        if (tmpData.startTime != null)
            tmpData.startTime = tmpData.startTime - wsData.timeDif;
        for (let i = 0; i < tmpData.finishTime.length; i++) {
            if (tmpData.finishTime[i] != null)
                tmpData.finishTime[i] = tmpData.finishTime[i] - wsData.timeDif;
        }
        console.debug("StopWatchData: ", tmpData);
        console.debug("");
        return tmpData;
    }

}

export var stopwatch = new Stopwatch();

