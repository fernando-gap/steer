# Reference
This document list all API functionality and guide on how to use the classes offered by Steer.

# Contents
- [What is Steer](#what-is-steer)
- [The guide](#the-guide)
    - [Dependencies](#dependencies)

# What is Steer
Steer is URL creator for OAuth2 and Drive for Google APIs as mentioned [here](https://github.com/fernando-gap/steer#steer). Steer **does not**: make a **HTTP request**, create other types of OAuth2 URLs other than *Desktop & Mobile Apps*. The document is where methods and classes will be teaching you in how to use them.

# The Guide
This is a guide throughout the api reference, each method and class will be explained and used in a interactive example and in the end you will have an app built with the steer API. To follow the example while reading this document it is recomended that you install the dependencies below.

## Dependencies
If you want to follow the example with steer it is needed to install some dependencies first. These are python, flask, requests and pip.

It is assumed that you already have pip and python, if not install it and comeback later :). to Install *flask* and *requests* do the following:
```
$ pip install flask
$ pip install requests
```
## The Application Example
The example that will be used in this guide **do not interfere** if you don't follow.

The app purpose is simple: each time the user executes the app a file is written in its Drive, the user can pass arguments to revoke the access, and update a file, also the application should be refreshing the token to avoid the user do the OAuth2 screen again.
