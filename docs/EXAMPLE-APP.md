# Example
## The Guide
This is a guide throughout the api reference where each method and class will be explained and used in a ***interactive way*** that you can follow, and in the end you will have an app built with the Steer API.

## Dependencies
It is assumed that you already have *pip* and *python*, if not install it and comeback later :). to Install flask and requests do the following:

```
$ pip install flask
$ pip install requests
```

## The Application
The app purpose is simple: each time the user executes the app a file is written in its Drive, the user can pass arguments to revoke the access, and update a file, also the application should be refreshing the token to avoid the user do the OAuth2 screen again.

The example is used inside a project of google, and it is assumed that you already have a project and the API keys to get started.

## Create an OAuth2 URL
The first thing in our example is create the OAuth2 URL. 
```python
# app.py
from steer.oauth.api import OAuth2

oauth = OAuth2(json_path='./config.json')

def step_one(oauth): 
    oauth.create()
```

The `config.json` file contains the following properties:

```json
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scope": "https://www.googleapis.com/auth/drive",
    "response_type": "code",
    "redirect_uri": "http://localhost:5000"
}

```


## Open User's Default Browser
Open the default browser of the client in our example.

```python
def step_one(oauth): 
    oauth.create()
    oauth.open()
```

The function `step_one` is *wrapping* the first step to create the authentication, this is good because we can use the function later, the argument `oauth` is an `OAuth()` instance.

The user should authorize the application to access its drive to tell Google to send the authorization code to our `Loopback IP address`.

## Create the Loopback IP address
The redirect URI is which method the Google should use to send the authorization code. In this case is the Loopback IP address where there is a local server listening to a port.

The implementation of this in our app is a simple flask instance used with some coroutines functions.

```python
# app.py
from flask import Flask, request, redirect
from steer.oauth.api import OAuth2

from signal import SIGINT
import asyncio
import os

code_url = ''

async def server(oauth):
    app = Flask(__name__)

    @app.route('/')
    def oauth_code():
        code = request.args.get('code')
        global code_url
        code_url = oauth.accesstoken(code)
        return redirect('/exit')

    @app.route('/exit')
    def exit():
        os.kill(os.getpid(), SIGINT)
        return ""

    app.run()
    return

def step_one(oauth): 
    oauth.create()
    oauth.open()

import requests
def step_two(url):
    response = requests.post(url)

    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(response.text)

    tokens = response.json()
    return tokens

oauth = OAuth2(json_path='./config.json')

if __name__ == '__main__':
    step_one(oauth)
    asyncio.run(server(oauth))
    step_two(code_url)

```
At this stage the file should look like as above.

The first thing added to our app was the OAuth2 URL, that enables the user to login in. The second is a server implemented in Flask which is a coroutine that awaits the `code` from Google that stores the code, then the code exchange URL is made by `OAuth2.accesstoken()`. At the end the server is closed by killing the process with kill.

## Code Exchange

The step two is exchange the code to an access token and a refresh token whose enable our app to create the requests to the Google Drive.

```python
import requests

def step_two(url):
    response = requests.post(url)
```

The function also will create a `.steer/` folder which the access token will be saved in `tokens.json`. if the file already exists then the file is updated.

```python
    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(response.text)

    tokens = response.json()
    return tokens
```

The tokens where saved in `./.steer/tokens.json` in the current directory. The `tokens` variable store the response from Google as `json` and return it.

The app can create the OAuth2 authentication by itself now. To see how the app is working let's test. To see if everything is running as expected.
```python
# app.py
from flask import Flask, request, redirect
from steer.oauth.api import OAuth2

from signal import SIGINT
import asyncio
import os

code_url = ''

async def server(oauth):
    app = Flask(__name__)

    @app.route('/')
    def oauth_code():
        code = request.args.get('code')
        global code_url
        code_url = oauth.accesstoken(code)
        return redirect('/exit')

    @app.route('/exit')
    def exit():
        os.kill(os.getpid(), SIGINT)
        return ""

    app.run()
    return

def step_one(oauth): 
    oauth.create()
    oauth.open()

import requests
def step_two(url):
    response = requests.post(url)

    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(response.text)

    tokens = response.json()
    return tokens

oauth = OAuth2(json_path='./config.json')

if __name__ == '__main__':
    step_one(oauth)
    asyncio.run(server(oauth))
    step_two(code_url)
```

To execute the program run the following, remember that you need to login as a test user or a user depending on your Google project.

```
$ python app.py
```

It will open your default browser and you will notice a screen asking to choose a Google account.

After you login in, you be redirected to the `/exit` url location, and you will see the `The code was received` message. The server is automatically closed.

See if the runtime succeeds:
```
$ cat .steer/tokens.json
```
It should list a json file with contents, otherwise will be an status code error.
