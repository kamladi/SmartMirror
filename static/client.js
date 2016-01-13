$(document).ready(function(){
    var URL = 'http://' + document.domain + ':' + location.port;
    var socket = io.connect(URL);
    socket.on('connect', function (err) {
        console.log('connected');
    });
    socket.on('response', function(msg) {
        console.log(msg);
        $('#log').append('<p>Received: ' + msg.data + '</p>');
    });
    $('form#emit').submit(function(event) {
        socket.emit('my event', {data: $('#emit_data').val()});
        return false;
    });
    $('form#broadcast').submit(function(event) {
        socket.emit('my broadcast event', {data: $('#broadcast_data').val()});
        return false;
    });
});
