# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project **do not** adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2022-02-11
### Added
- New class OAuth2 to create the URI for Google's OAuth 2.0 Server


## [0.1.1] - 2022-02-12
### Removed
- Comments and variables in improper places


## [0.2.0] - 2022-02-12
### added
- Google api code challenge generator


## [0.2.1] - 2022-02-12
### Removed
- Useless encryption on class S256, the hash256 was being encrypted twice with Base64 encode

### Changed
- Base64url was adding a trailing equals "=" in code challenge that was causing an encode error


## [0.3.0] - 2022-02-13
### Added
- Exchange code URL can be created from OAuth2 class

### Changed
- Code refactor to create a better understanding on code

### Removed
- Useless strings and code that are meaningless


## [0.4.0] - 2022-02-13
### Added
- Manipulate response from Google after the exchange operation is made
- Added the possibility to check whether the access token is expired


## [0.4.1] - 2022-02-13
### Changed
- Code refactor: pieces of code changed in oauth2.py file for a better understanding and less code


## [0.5.0] - 2022-02-14
### Added
- Refresh tokens URI can be called
- Revoke access URI can be now created

### Deprecated
- OAuth2 for Desktop Apps & Mobile supports; it should support all types of OAuth2


## [0.5.1] - 2022-02-17
### Changed
- Code is more readable when sending long strings.

### Fixed
- Code challenge was unrecognize when passed to the OAuth2CodeExchange class causing errors when the client tries use the S256 method.


## [0.6.0] - 2022-02-18
## Added
- The headers for each type of request simple and multipart/related methods are created to be handled.
