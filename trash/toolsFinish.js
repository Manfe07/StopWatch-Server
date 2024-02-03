
var socket = io();
socket.on('connect', function() {
  socket.emit('get_stopwatch', {data: 'Hello'});
  socket.emit('my event', {data: 'I\'m connected!'});
});

socket.on("connect_error", (err) => {
  console.log(`connect_error due to ${err.message}`);
  setConnectionState(false);
});

wsData = {
  device : NaN,
  latency : NaN,
  timeDif : NaN,
  action : NaN,
  lane : NaN,
  value : NaN
}

var ping_time = NaN;
var pong_time = NaN;
var PingInterval = 5000;

calcLatency();
function calcLatency(){
    ping_time = new Date().valueOf();
    socket.emit('ping', {
        data:{
          ping_time: ping_time
          }
        });
    setTimeout(calcLatency, PingInterval);
}


socket.on('pong', function(msg, cb) {
    setConnectionState(true);
    pong_time = new Date().valueOf();
    //console.log(msg);
    wsData.latency = (pong_time - ping_time);
    //console.log(wsData.latency);
    wsData.timeDif =  (ping_time + wsData.latency) - (msg.pong * 1000);
    //console.log(wsData.timeDif);
    setTimeout(setConnectionState, (PingInterval + 1000), false);
    console.log({"wsData_Latency":wsData});
});


socket.on('stopwatchServer', function(msg, cb) {
    $('#log').append('<br>' + $('<div/>').text('Received #' + JSON.stringify(msg)).html());
    console.log({'StopwatchDataReceived':msg});
    stopwatch.isRunning = msg.running;
    stopwatch.startTime = msg.start_ts + wsData.latency;
    if (stopwatch.isRunning){
      stopwatch.tick();
    }
    /*
    switch (msg.data.action) {
        case "start":
            stopwatch.isRunning = true;
            stopwatch.startTime = new Date(msg.data.value + wsData.timeDif);
            stopwatch.tick();
            break;
        case "stop":
            stopwatch.isRunning = false;
            stopwatch.stopTime = new Date(msg.data.value + wsData.timeDif);
            break;
        default:
            break;
    }
    */
    if (cb)
      cb();
  });
  
  $(document).keypress(function(event) {
    var keyPressed = String.fromCharCode(event.which);
    switch (keyPressed) {
      case '1':
        wsData.value = new Date().valueOf() - wsData.timeDif;
        wsData.action = "start";
        wsData.lane = 0;
        socket.emit('stopwatch', {data : wsData});
        break;
      case '2':
        wsData.value = new Date().valueOf() - wsData.timeDif;
        wsData.action = "stop";
        wsData.lane = 0;
        socket.emit('stopwatch', {data : wsData});
        break;
      case '3':
        wsData.action = "reset";
        wsData.lane = 0;
        socket.emit('stopwatch', {data : wsData});
        break;
      default:
        break;
    }
    //console.log(keyPressed);
    console.log({"wsData_Send":wsData});
    $("#target").append(keyPressed);
  });
  
  class Stopwatch {
    constructor() {
      this.isRunning = false;
      this.startTime = null;
      this.endTime = null;
      this.elapsedTime = 0;
    }
  
    start() {
      if (!this.isRunning) {
        this.isRunning = true;
        this.startTime = new Date();
        socket.emit('stopwatch', {
          data:{
            action: 'start',
            startTime: this.startTime.valueOf()
            }
          });
          this.tick();
      }
    }
  
    stop() {
      if (this.isRunning) {
        this.isRunning = false;
        this.endTime = new Date();
        this.elapsedTime += this.endTime - this.startTime;
      }
    }
  
    reset() {
      this.isRunning = false;
      this.startTime = null;
      this.endTime = null;
      this.elapsedTime = 0;
      this.updateDisplay();
    }
  
    tick() {
      if (this.isRunning) {
        //this.startTime = this.endTime;
        this.endTime = new Date();
        this.elapsedTime = this.endTime - this.startTime;
        this.updateDisplay();
        requestAnimationFrame(() => this.tick());
      }
    }
  
    updateDisplay() {
      const milliseconds = Math.floor(this.elapsedTime);
      const seconds = Math.floor(milliseconds / 1000);
      const minutes = Math.floor(seconds / 60);
  
      const formattedTime = `${String(seconds).padStart(2, '0')}.${String((Math.round((milliseconds % 999) / 10))).padStart(2, '0')}`;
  
      $("#time").text(formattedTime);
      //$("#time").text(this.endTime.valueOf());
    }
  }
  const stopwatch = new Stopwatch();
      