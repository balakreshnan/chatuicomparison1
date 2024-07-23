const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const output = document.getElementById('output');

let recognition;
if (!('webkitSpeechRecognition' in window)) {
  output.textContent = 'Your browser does not support the Web Speech API';
} else {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event) => {
    let interimTranscript = '';
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }
    output.textContent = finalTranscript + '\n' + interimTranscript;
  };

  recognition.onerror = (event) => {
    output.textContent = 'Error occurred in recognition: ' + event.error;
  };

  startButton.onclick = () => {
    recognition.start();
    output.textContent = 'Listening...';
  };

  stopButton.onclick = () => {
    recognition.stop();
    output.textContent = 'Stopped listening.';
  };
}
