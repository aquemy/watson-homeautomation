# IBM Watson Home Automation

This is a mockup and demonstration of an intelligent home automation system using Watson services.
Currently, the only thing it can do is to understand vocal requests in natural language to play music.

## How does it workers?

- In browser, using HTML5 + Javascript, voice is recorded and streamed to a NodeJS server.
- This NodeJS server calls Speech-To-Text to obtain a transcript of the record.
- This transcript is transmited to a Python application in theory responsible to analyze the request using AlchemyAPI and dispatch it to the application in charge performing the action. In practice, as it supports only retrieving music to play it, everything is performed there, except the downloading and playing the music.
- From the results of AlchemyAPI, artists are retrieved using SAPRQL to query a semantic database (dbpedia). Eventual albums or songs are retrieved using AudioDB API.
- When the artist and album or song is selected, Youtube is queried using Youtube API, and the URI is sent to the music component, writtent in Python.
- Finally, the audio of the content pointed by the URI is streamed (in this version downloaded) and added a MPD server (in this version played by VLC).

Every component, including the frontend, is managed by a Crossbar.io router.

## Installation

1.Get your free AlchemyAPI key here: http://www.alchemyapi.com/api/register.html

2. Put your key in ```.crossbar/api_key.txt```.

3. Create a Bluemix account. Sign up in Bluemix or use an existing account. Watson services in beta are free to use, as are GA services in the standard plan below a certain usage threshold.

4. If it is not already installed on your system, download and install the Cloud-foundry CLI tool.

5. If it is not already installed on your system, install Node.js. Installing Node.js will also install the npm command. Insure npm is at least ```v0.12``.

6 Connect to Bluemix by running the following commands in a terminal window:

$ cf api https://api.ng.bluemix.net
$ cf login -u <your-Bluemix-ID> -p <your-Bluemix-password>

Create an instance of the Speech to Text in Bluemix by running the following command:

$ cf create-service speech_to_text standard speech-to-text-service

**Note:** You will see a message that states "Attention: The plan standard of service speech_to_text is not free. The instance speech-to-text-service will incur a cost. Contact your administrator if you think this is in error.". Transcription of the first 1000 minutes of audio per month to the Speech to Text service are free under the standard plan, so there will be no charge if you remain below this limit.

7. Push the updated application live by running the following command:

$ cf push


8. Add your speech-to-text instance credentials (found on Bluemix website) to ```server/server.js```.

9. Add your Youtube API key and AudioDB API key respectively to ```actions/youtube.py``` and ```actions/artists.py```.

10.Install dependencies:

    npm install
    python setup.py install


## Running the application

Run:

    crossbar start

## Conditions on the requests

The little mockup will start working on your request only if it finds the verbe 'listen' or 'play', however is the subject or the tense used.
