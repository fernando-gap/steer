# Example
## The Guide
This is a guide throughout the api reference where each method and class will be explained and used in a ***interactive way*** that you can follow, and in the end you will have an app built with the Steer API. To see the API reference click [here](https://github.com/fernando-gap/steer/blob/main/docs/README.md).

## Dependencies
It is assumed that you already have *pip* and *python*, if not install it and comeback later :). to Install flask and requests do the following:

```
$ pip install flask
$ pip install requests
```

## The Application
The app purpose is simple: each time the user executes the app a file is written in its Drive, the user can pass arguments to revoke the access, and update a file, also the application should be refreshing the token to avoid the user do the OAuth2 screen again. Steer does not make the request then it is needed to implement it by ourselves.

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


```
At this stage the file should look like as above.

The first thing added to our app was the OAuth2 URL, that enables the user to login in. The second is a server implemented in Flask which is a coroutine that awaits the `code` from Google to store it, then the code exchange URL is made by `OAuth2.accesstoken()`. At the end the server is closed by killing the process with kill.

## Code Exchange

The step two is exchange the code to an access token and a refresh token that permits the app access the user's drive.

The `check_dir` function creates a `.steer/` folder which the access token will be saved in `tokens.json`. if the file already exists then the file is updated.

```python
def check_dir(data):
    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(data)
```

The tokens were saved at `./.steer/tokens.json` in the current directory. The variable `tokens` store the response from Google as `json`, and returns it.

```python
import requests

def step_two(url):
    response = requests.post(url)
    check_dir(response.text)
    tokens = response.json()
    return tokens
```
The app can create the OAuth2 authentication by itself now. Let's test the app to see if everything is running as expected.

```python
# app.py
from flask import Flask, request, redirect
from steer.oauth.api import OAuth2
import requests

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
        return "The code was received"

    app.run()
    return

def check_dir(data):
    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(data)

def step_one(oauth): 
    oauth.create()
    oauth.open()

def step_two(url):
    response = requests.post(url)
    check_dir(response.text)
    tokens = response.json()
    return tokens

oauth = OAuth2(json_path='./config.json')

if __name__ == '__main__':
    step_one(oauth)
    asyncio.run(server(oauth))
    step_two(code_url)
```
At this stage the server should look as above.

To execute the program run the following, remember that you need to login as a test user or a user depending on your Google project.

```
$ python app.py
```

It will open your default browser and you will notice a screen asking to choose a Google account.

After you loged in, you will be redirected to the `/exit` url location, and you will see a message (`The code was received`).

See if the runtime succeeds:
```
$ cat .steer/tokens.json
```
It should list a json file with contents, otherwise a status code error.

## Refreshing the Access token

This next step may can change a little bit our `app.py`, because we need to check whether the refresh token is expired each time the user runs the app.

The code loads the data from `tokens.json`, makes a `POST` request to get the new access tokens, and update the file at `.steer/tokens.json` with the new ones.

```python
import json

def refresh(oauth):
    data = json.loads(open('./.steer/tokens.json').read())
    token = oauth.refreshtoken(data['refresh_token'])

    tokens_new = requests.post(token)
    check_dir(tokens_new)
```
The function refresh a token each time is called, which is bad, it is needed that the function only request a new token when the other one is *expired*.
```python
import json

def refresh(oauth, is_expired):
    if is_expired:
        data = json.loads(open('./.steer/tokens.json').read())
        token = oauth.refreshtoken(data['refresh_token'])
    else:
        return False

    tokens_new = requests.post(token)
    check_dir(tokens_new)
    create_expires_date(tokens_new.json())
    return True

```
This modification returns false or true depending whether the token is expired. As you noticed the application requires a `is_expired` argument which will be covered below.
