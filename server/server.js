var binaryServer = require('binaryjs').BinaryServer;
var wav = require('wav');
var opener = require('opener');

var watson = require('watson-developer-cloud');
var speech_to_text = watson.speech_to_text({
  username: 'your user name',
  password: 'your password',
  version: 'v1'
});

var fs = require('fs');
if(!fs.existsSync("recordings"))
    fs.mkdirSync("recordings");

var connect = require('connect');
var server = binaryServer({port: 9001});
var autobahn = require('autobahn');
var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:8080/ws',
   realm: 'realm1'}
);

var transcript = null;

connection.onopen = function(session) {
  console.log('Websocket connected.');
  setInterval(function () {
    if (transcript != null) {
      console.log('Send transcript: '+transcript);
      session.call('actionner.trigger', [transcript]).then(
      function (res) {
        console.log("result: " + res);
        transcript = null;
      },
      function (err) {
        console.log('failed: ' + err);
      });

    }
   }, 1000);
}

connection.open();

server.on('connection', function(client) {
    console.log("new connection...");
    var fileWriter = null;

    client.on('stream', function(stream, meta) {
        console.log("Audio streaming started (" + meta.sampleRate +"Hz).");
        speech_to_text.createSession({}, function(err, session) {
        if (err)
            console.log('error:', err);
        else
            //console.log(JSON.stringify(session, null, 2));
            console.log('Session established with Watson speech-to-text.')
        });

        var fileName = "recordings/"+ new Date().getTime()  + ".wav"
            fileWriter = new wav.FileWriter(fileName, {
                channels: 1,
                sampleRate: meta.sampleRate,
                bitDepth: 16
            });

            stream.pipe(fileWriter);
            var params = {
              // From file
              audio: stream,
              content_type: 'audio/l16; rate='+meta.sampleRate
            };

            transcript = null // Restart the transcript
            speech_to_text.recognize(params, function(err, res) {
              if (err)
                console.log(err);
              else {
                console.log(JSON.stringify(res, null, 2));
                if(res["results"].length > 0) {
                  transcript = res["results"][0]["alternatives"][0]["transcript"]
                  console.log(transcript)
                } else {
                  console.log("Could not identify anything.")
                }

              }
            });
    });

    client.on('close', function() {
        if (fileWriter != null) {
            fileWriter.end();
        }
        console.log("Connection Closed");
    });
});


