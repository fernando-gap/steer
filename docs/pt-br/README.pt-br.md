# Documentação
Este documento lista todas as funcionalidades e usos da API Steer. Para criar seu primeiro aplicativo feito com Steer clica [aqui](https://github.com/fernando-gap/steer/blob/main/docs/pt-br/EXAMPLE-APP.pt-br.md).

# Índice
- [O que é Steer](#o-que-é-steer)
- [Pacotes](#pacotes)
- [OAuth2](#oauth2)
    - [Classe OAuth2](#classe-oauth2)
        - [create](#oauth2createchallengenone)
        - [open](#oauth2open)
        - [accesstoken](#oauth2accesstokencode-secretnone)
        - [revokeaccess](#oauth2revokeaccesstoken)
        - [refreshtokens](#oauth2refreshtokensrefresh_token--secret)
    - [Módulo Challenge](#módulo-challenge)
    - [Classe OAuth2Response](#classe-oauth2response) 
- [Drive](#drive)
    - [Classe Upload](#classe-upload)
        - [simple](#uploadsimplemedia--none)
        - [multipart](#uploadmultipartfile--none-metadata--none)

# O que é Steer
Steer cria URL para facilitar a autenticação e manipulação de "uploads" no Drive. Steer *não faz* pedidos HTTP, Steer não consegueu fazer outros tipos de URL que não seja *Desktop & Mobile*.

# Pacotes
Steer contém dois pacotes "oauth" e "drive" na qual é provido módulos para a manipulação de URLs.

Para importar estes pacotes:

```python
import steer.oauth.api as oauth
import steer.drive.upload as drive
```

Em que "oauth" é o pacote e `api` é o módulo que contém a classe OAuth2. O pacote "drive" contém funções para usar no envio de arquivos.

Alguns módulos, além desses dois, são oferecidos por Steer.

```python
import steer.oauth.challenge as challenge
import steer.oauth.response as response
```

O módulo "challenge" faz a utilização do `code_challenge` gerado pela aplicação e enviada com o pedido para aumentar o nível de segurança.

O módulo "response" manipula a resposta do Google depois que a fase de troca de chaves é feita, essa fase é conhecida em inglês como `code exchange` e vai ser utilizada para referir-se a fase. Esse módulo armazena `refresh_token` e `access_token`, também verifica se o "access_token" está expirado, o tempo de expiração é dado pelo Google.

# OAuth2
O módulo de OAuth2 é onde acontece todo o processo de criação de URL. Esse módulo deve ser suficiente para criar uma aplicação que se autentica usando o protocolo OAuth2.

## Classe OAuth2
Antes de começar é importante saber como o Google usa isso e quais campos são necessários para criar uma URL. Os campos seguintes são notáveis:

- client_id
- scope
- response_type
- redirect_uri
- client_secret


O Google disponibiliza estes campos acima, assim que um "Google Project" é criado e uma OAuth2 chave é emitida.

A classe OAuth2 pode carregar estes campos usando *json*, um *dicionário* ou passando arguments *keywords* para a instancia.


config.json
```json
{
    "client_id": "your_client_id",
    "scope": "authorization_scope",
    "response_type": "code",
    "redirect_uri": "http://localhost:port"
}
```

`redirect_uri` é o `Loopback IP address` que é um server local em que o Google envia o `code`.
`response_type` sendo o definido como `code`, que serve para applicações *desktop*, Steer apenas suporta autenticação para desktop.


```python
# json
auth = OAuth2(json_path="./config.json")

# dictionary
config = {
    "client_id": "your_client_id",
    "scope": "authorization_scope",
    "response_type": "code",
    "redirect_uri": "http://localhost:port"
}

auth = OAuth2(dict_params="./config.json")

# keyword arguments
auth = OAuth2(client_id="your_client_id",
              scope="authorization_scope",
              response_type="code",
              redirect_uri="http://localhost:port"
              )
```

# Métodos OAuth2

### OAuth2.create(challenge=None)
O método "create" é a primeira coisa a se fazer para autenticar sua aplicação na API do Google. O método pode opcionalmente utilizar o `code_challenge`. O método retorna a URL que pode ser quardada em uma variável.

Argumentos:
- challenge - é uma chave encriptada criada para cada pedido de OAuth2 para receber o `access_token`.

```python
# app.py
from steer.oauth.api import OAuth2

oauth = OAuth2(json_path='./config.json')
oauth.create()
```


### OAuth2.open()
Google não abre o pedido de autenticação quando um cliente HTTP é utilizado. Este método abre a request no navegador padrão do usuário, essa é a única parte da API que de fato faz um pedido. 

```python
oauth.open()
```

O usuário precisa autorizar a aplicação para o Google enviar o `code` para o o server local.

### OAuth2.accesstoken(code, secret=None)
O `code` recebido no server é então usado no code exchange na qual é a segunda coisa a se fazer para obter o "access_token".

Argumentos:
- code - Código enviado pelo Google no server local
- secret - Opcional se usado como json, sendo o `client_secret`

#### Exemplo
Cria-se a URL para o code exchange.

To create a code exchange URL.
```python
code_url = oauth.accesstoken(code)
```

### OAuth2.revokeaccess(\*\*token)
Para negar os direitos de acesso de uma aplicação a algum usuário.

Argumentos:
- token - Um dicionário em que pode passar os valores de `refresh_token` ou um `access_token`.


```python
oauth.rovokeaccess(access_token='access_token')
# or
oauth.rovokeaccess(refresh_token='refresh_token')
```

### OAuth2.refreshtokens(refresh_token,  secret='')
O `refresh_token` evita o usuário ver a tela de consentimento toda vez que executa a aplicação. O método cria esta URL para refrescar estas chaves.

Argumentos:
- refresh_token
- client_secret


```python
oauth.refreshtokens('refresh_token')
```


# Módulo Challenge
O módulo "challenge" é para aqueles que desejam um nível de segurança maior no fase de code exchange. Este método utiliza [PKFC]( métodohttps://datatracker.ietf.org/doc/html/rfc7636).

Importe o módulo:
```python
from steer.oauth.challenge import S256
```

Google aceita dois métodos S256 e Plain, Steer apenas aplica S256, sendo possível criar o Plain fazendo uma herança com a classe "IMethod" do módulo.

Para utilizar, passe a classe S256 no momento de criação de uma instancia OAuth2.


```python
from steer.oauth.challenge import S256

oauth.create(S256())
```

# Classe OAuth2Response
A classe armazena as principais chaves após a fase do code exchange ou quando está a refrescar as chaves. O método verifica se estas chaves estão vencidas.

Atributos de Classe:
- access_token 
- refresh_token
- before_expires - antes da chave expirar
- expires_in - tempo em segundos para vencer
- when_expires - quando a chave vence

Argumentos de instancia:
- res - resposta dada pelo Google


## Métodos OAuth2Response
### OAuth2.is_expired()
Este método checa se a chave está expirada
```python
handle.is_expired()
```

O retorno do método é falso ou verdadeiro


# Drive
O pacote do Drive contém duas classes `Upload` e `Update` que cria a possibilidade de envio de arquivos no Google Drive.

## Classe Upload
A classe upload cria um pedido URL que pode-se utilizar de dois métodos: "simple" e "multipart".

Argumentos de Instancia:
Um argumento `data` é passado como argumento para a classe na qual é um dicionário contendo os seguintes valores:

```python
data = {
    "url": "the drive url",
    "params": {"url": "parameters"},
    "token": "access_token",
    "meta_data": "file's metadata",
    "file_path": "path/to/file"
}
```

Se ambos metadata e media do arquivo é dada **apenas** a media do arquivo é criada para o "upload", para criar a URL de metadata tenha certeza de remover o valor `file_path`


## Métodos Upload

### Upload.simple(media = None)
O método "simple" cria uma URL para enviar metadata ou os dados do arquivo.

Argumentos:
- media - Se nenhum arquivo ou metadata foi passado para a instancia, o método verifica se o argumento `media` é diferente de `None`, se não for o caso então significa que o usuário não passou nenhuma media, um erro é lançado.


```python
from steer.drive.upload import Upload
upload = Upload(data)
url = upload.simple({"name":"example.txt"})
```

Depois de executado, o método retorna um dicionário que pode ser usado para enviar um pedido para o Google Drive. Os seguintes valores são retornados:

```json
{
    "method": "POST",
    "url": "https://www.googleapis.com/drive/v3/files",
    "headers": {
        "Content-Type": "application/json",
        "Content-Lenght": "23"
    },
    "body": {
        "metadata": {
            "name": "example.txt"
        }
    },
    "full_url": "https://www.googleapis.com/drive/v3/files?uploadType=simple",
    "params": {
        "uploadType": "simple"
    }
}
```

### Upload.multipart(file = None, metadata = None)
O método "multipart" consegue enviar ambos metadata e arquivos de media. Este método utiliza de um protocolo chamado `multipart/related` especificado pela [RFC 2387](https://datatracker.ietf.org/doc/html/rfc2387), que é um pedido composto por vários objetos enviados separados que forma, no final, apenas um.

Google usa isso, os dados do arquivo e a metadata sendo objetos enviados separadamente, que, no final forma um arquivo para o Drive.

Argumentos:
- file - Lugar do arquivo no sistema operacional
- metadata - metadata do arquivo


O retorno de uma `multipart/related` se diferencia um pouco do método `simple`.


```json
{
    "method":"POST",
    "url":"https://www.googleapis.com/upload/drive/v3/files",
    "params":{
        "uploadType":"multipart"
    },
    "headers":{
        "top-level":{
            "Authorization":"Bearer access_token",
            "Content-Type":"multipart/related; boundary=file-actions",
            "Content-Length":"39"
        },
        "metadata":{
            "Content-Type":"application/json; charset=UTF-8"
        },
        "media":{
            "Content-Type":"text/plain"
        }
    },
    "body":{
        "data":"--file-actions\nContent-Type: application/json; charset=UTF-8\n\n{\"name\": \"greetings.txt\"}\n\n--file-actions\nContent-Type: text/plain\n\nHello, world!\n\n\n--file-actions--"
    },
    "full_url":"https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
}
```


Dependendo do tamanho do arquivo o retorno do método pode ser grande.

Os `headers` são divididos entre três camadas: "top-level", "metadata" e "media". Apenas descreve quais "headers" foram utilizados.
