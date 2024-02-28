
//         function appendAudioTag() {
//     var chatBox = document.getElementById('chat-box');

//     // Create an <audio> element
//     var audioTag = document.createElement('audio');
//     audioTag.controls = true; // Add controls to the audio player
//     audioTag.src ='uploads\output.mp3' ;

//     // Create a <p> element to contain the audio tag
//     var audioContainer = document.createElement('p');
//     audioContainer.appendChild(audioTag);

//     // Append the <p> element to the chat box
//     chatBox.appendChild(audioContainer);
// }
        function sendMessage() {
            var userInput = document.getElementById('user-input').value;
            var chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += '<p>User: ' + userInput + '</p>';

            // Send the input to Flask for processing (text input)
            fetch('/text', {
                method: 'POST',
                body: new URLSearchParams({
                    'user_input': userInput,
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            })
            .then(response => response.text())
            .then(textOutput => {
                // Display the bot response
                chatBox.innerHTML += '<p>Bot: ' + textOutput + '</p>';
            });

            // Clear the input field after sending a message
            document.getElementById('user-input').value = '';
        }

        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }

        function handleEnter(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        }
        URL = window.URL || window.webkitURL;

var gumStream;                      //stream from getUserMedia()
var rec;                            //Recorder.js object
var input;                          //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

function startRecording() {
    console.log("recordButton clicked");

    /*
        Simple constraints object, for more advanced audio features see
        https://addpipe.com/blog/audio-constraints-getusermedia/
    */

    var constraints = { audio: true, video:false }

    /*
        Disable the record button until we get a success or fail from getUserMedia() 
    */

    recordButton.disabled = true;
    stopButton.disabled = false;
    pauseButton.disabled = false

    /*
        We're using the standard promise based getUserMedia() 
        https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    */

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        /*
            create an audio context after getUserMedia is called
            sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
            the sampleRate defaults to the one set in your OS for your playback device

        */
        audioContext = new AudioContext();

        //update the format 
        document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        /* 
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */
        rec = new Recorder(input,{numChannels:1})

        //start the recording process
        rec.record()

        console.log("Recording started");

    }).catch(function(err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
        pauseButton.disabled = true
    });
}

function pauseRecording(){
    console.log("pauseButton clicked rec.recording=",rec.recording );
    if (rec.recording){
        //pause
        rec.stop();
        pauseButton.innerHTML="Resume";
    }else{
        //resume
        rec.record()
        pauseButton.innerHTML="Pause";

    }
}
// ... (previous code)

function stopRecording() {
    console.log("stopButton clicked");

    // disable the stop button, enable the record to allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;

    // reset button just in case the recording is stopped while paused
    pauseButton.innerHTML = "Pause";

    // tell the recorder to stop the recording
    rec.stop();

    // stop microphone access
    gumStream.getAudioTracks()[0].stop();

    // create the wav blob and pass it on to uploadRecording
    rec.exportWAV(uploadRecording);
}

function uploadRecording(blob) {
    var fd = new FormData();
    var filename = new Date().toISOString() + ".wav";

    // append the audio data to FormData
    fd.append("audio_data", blob, filename);

    // send a POST request to the server to save the file
    var xhr = new XMLHttpRequest();
    xhr.onload = function (e) {
        if (this.readyState === 4) {
            console.log("Server returned: ", e.target.responseText);
        }
    };
    xhr.open("POST", "/realtime", true);
    xhr.send(fd);
    window.location.href = "/play";
    
}



