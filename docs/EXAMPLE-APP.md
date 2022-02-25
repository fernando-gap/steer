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

### Testing
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
The function refresh a token each time is called, which is bad, it is needed that the function only request a new token when the other one is *expired* and when the tokens *actually* has a refresh token, which is issued when the user makes its **first** authentication.

```python
import json

def refresh(oauth, is_expired):
    data = json.loads(open('./.steer/tokens.json').read())
    if 'refresh_token' in date and is_expired:
        token = oauth.refreshtoken(data['refresh_token'])
        tokens_new = requests.post(token)
        check_dir(tokens_new)
        create_expires_date(tokens_new.json())
        return True
    else:
        return False
```
This modification returns either false or true depending whether the token is expired and has a `refresh_token` to renew. As you noticed the function `refresh` requires a `is_expired` argument which will be covered below.

## Handle Response Code
How to know if the access token is expired? A new module is introduced that is the `OAuth2Response` Class which you can check if a token was expired. 

The interesting thing is that it provides a method that checks if a token was expired, it provides the `before_expires` attribute that is when the instance was created.

With this in mind it is possible do the following:
```python
from steer.oauth.response import OAuth2Response

def create_expires_date(tokens):
    tokens_new = OAuth2Response(tokens)

    with open('.steer/expires_token_date.txt', 'w') as expires:
        expires.write(str(response.before_expires))
```
This saves the date when the token was issued by the exchange code response.

The next thing is to verify if the token is in fact expired, it should returns True or False. If the files necessary does not exist the function returns false, meaning that the user does not have an access token.

```python
from datetime import, datetime
def is_token_expired():
    if (os.path.exists('.steer/tokens.json') and 
        os.path.exists('.steer/expires_token_date.txt')):

        with open('.steer/tokens.json', 'r') as tokens_old:
            tokens = json.loads(tokens_old.read())

        with open('.steer/expires_token_date.txt') as before:
            expires = datetime.fromisoformat(before.read())

    else:
        return False

    date = OAuth2Response(tokens)
    date.before_expires = expires

    return date.is_expired()
```

To apply these functions in our app put the `create_expires_date` inside the `step_two` function (i. e. at the end), and `refresh`, which arguments is the return of `is_token_expired`, before the `step_one` as follows:
```python
def step_two(url):
    response = requests.post(url)
    check_dir(response.text)
    tokens = response.json()
    create_expires_date(tokens) # here
    return tokens


if __name__ == '__main__':
    refresh(oauth, is_token_expired()) # here
    step_one(oauth)
    asyncio.run(server(oauth))
    step_two(code_url)
```
To test the app follow these steps as mentioned [here](#testing) You can try to modify the files inside `.steer` to see what happens.

## Revoke the app access
Apps can access the user's drive when using the API, but applications can also revoke the access rights to stop using the user's drive. To revoke the access in our application is to pass a command line option `--revoke`.

```python
def revoke_access(oauth):
    try:
        with open('./.steer/tokens.json') as tokens:
            token = json.loads(tokens.read())

        deny = oauth.revokeaccess(access_token=token['access_token'])
        requests.post(deny)
        os._exit(0)
    except FileNotFoundError:
        return
```

The function `revoke_access` tries to open the `tokens.json` to read the access_token, this is needed to revoke the access rights, if no files found the function return `None` which means that the user still do not have an authentication.

If the user has one, then the request is made to revoke the access, and the app closes.

```python
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--revoke':
        revoke_access(oauth)
        
    refresh(oauth, is_token_expired())
    step_one(oauth)
    asyncio.run(server(oauth))
    step_two(code_url)
```

In the top of `main` it is checked whether the `sys.argv` is greater than one, and if the index one is equals to `--revoke` if it is the revoke is made, if not the lines below is executed.
