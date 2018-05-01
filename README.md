# geotwitterstream
geotwitterstream is a python 2.7 backend and Html5/ES6 frontend application which consumes and visualizes tweets from the Twitter stream API. The application allows the user to specify a 4-sided geographic area to match tweets that fall within that area. The area may span up to a maximum of 25 miles (40.2336 km) in length.
## Limitations
The application currently only partly handles invalid coordinates, i.e. minimum / maximum numeric latitude / longitude format is checked on the frontend but, invalid latitude / longitude pairs (e.g. spanning more than 25 miles) will cause undefined behaviour (A 406 status code will be returned by the twitter stream API). Also it must be noted that in practice, not checking the user-input (which can be passed through the url) on the backend side, would form a security risk which must be avoided for an actual production application.
## Requirements
Python 2.7.x (tested with Python 2.7.10)
Browser which supports Html5 and ES6 (tested with chrome 66.0.3359.117)

**Python Dependencies**
```sh
$ pip install requests requests_oauthlib websocket-server enum34
```
## Configuration
**Backend**
In */backend/geotwitterstream/config.py* the twitter application credentials and websocket server address need to be configured. The twitter application credentials can be obtained be registering an application at https://developer.twitter.com/apps. NB: For security reasons I have not made my personal twitter application credentials available in this repository.

**Frontend**
In */frontend/web/app.js* the websocket server address need to be configured. NB: This must be the same address as configured in */backend/geotwitterstream/config.py*.
## Installation
Installation is not needed, the application can be run directly from the cloned repository.
## Contents

**backend/geotwitterstream:** Python backend API. It's core consists of a websocketserver for communication with the frontend layer and, the necessary OAuth1 authorization handling and encapsulation of the twitter stream API.
**backend-app:** Minimal application for working with the backend API.
**backend-test:** Some very basic testing which was performed during development in order to test different parts of the backend API.
**frontend-app/web** Web application which displays tweets for given coordinates.
