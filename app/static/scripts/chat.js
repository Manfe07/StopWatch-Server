import { socket, watchDog, wsData } from "/static/scripts/socket.js";
import { stopwatch } from "/static/scripts/stopwatch.js";

// Button to toggle chat window
$('#toggleChat').click(function (event) {
    $('#chatWindow').toggle();
})

// function to send message
function chatSendMessage() {
    messageInput = $("#messageInput").val();
    if (messageInput != "") {
        socket.emit('chatMessage',
            {
                message: $("#messageInput").val(),
                device: wsData.device,
                timestamp: new Date().valueOf()
            }
        );
    }
    $("#messageInput").val("");
}

// When chat is open, send message with "ENTER"
$(document).keyup(function (event) {
    if ($("#messageInput").is(":focus") && event.key == "Enter") {
        chatSendMessage();
    }
});

// send message with Button
$('#sendMessage').click(function (event) {
    chatSendMessage();
})


// handle received message
socket.on('chatMessage', function (msg, cb) {
    let message = msg.message;
    let device = msg.device;
    var cssClass = "textSelf";
    if(device != wsData.device)
        cssClass = "textOther";

    console.debug(wsData);
    console.debug(msg);
    $('.chatMessages').append($("<p class='" + cssClass + "'></p>").text(msg.device + ': ' + msg.message))
    console.debug({ "ChatMsg": msg });
    if (!stopwatch.armed && $('#chatWindow').css("display") == "none") {
        $('#chatWindow').show();
    }

    if (device != wsData.device) {
        let buttonID = "#toggleChat";
        let midFade = 0.1;
        let fadeA = 200;
        let fadeB = 200;
        for (let index = 0; index < 5; index++) {
            $(buttonID).fadeTo(fadeA, midFade);
            $(buttonID).fadeTo(fadeB, 1);
        }
    }
});