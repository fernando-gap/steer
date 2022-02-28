# Steer
<a href="https://github.com/fernando-gap/steer/blob/main/README.pt-br.md">
  <img src="https://img.shields.io/badge/lang-pt--br-green">
</a>


<!-- Description -->
The OAuth2 and Google Drive media upload made simple. The Steer API creates all the necessary OAuth2 URLs to authenticate in Google API. Steer also offers the possibility to create media upload URLs in Google Drive API that offers two types of media upload: simple and multipart.

## Installation
To install Steer it is needed python3 and pip the python package manager.

```
pip install steer
```

Follow the guides at <!-- docs/--> [docs](https://github.com/fernando-gap/steer/tree/main/docs) to get start with Steer.

## How it works

### OAuth2
The Steer creates OAuth2 URL according to the Google methods encountered [here](https://developers.google.com/identity/protocols/oauth2/native-app#programmatic-extraction) and Google Drive media upload [here](https://developers.google.com/drive/api/v3/manage-uploads#http_1). 

OAuth2 is a protocol that authorizes third-parties applications to access data from other platforms such as google. Let's suppose you want to use google drive to create an application that creates a folder to store its data in the user's Google Drive. 

To do so you need a permission given by Google that is your access token, and the user consent to let the user know that you will be using its Drive to store such data.

The Steer creates the URL to facilitate the Google OAuth2 authorization steps. Steer **does not** send a HTTP request instead it creates the URL to make the request by using you preferred http client such as <!-- link to requests --> [requests](https://docs.python-requests.org/en/master/), this enables the use of any *http client*.

### Drive upload
Steer also offers the option to create a *model* HTTP URL for Google Drive. This means that the Steer creates all the necessary headers, request body, params and URL to make a request right away with any *http client*.

Three methods are used to upload media according to Google Drive: simple, multipart, and resumable. Steer offers simple and multipart methods.

- The simple method can upload either metadata or media it cannot upload both.
- The multipart method can both upload metadata and media.

## License
This project is under the MIT License.
