# Exemplo

## Sobre o tutorial
O tutorial é uma passagem através das classes e métodos, que irão ser explicados de uma **forma interativa** que se pode seguir. No final deste guia um aplicativo será construido com a API Steer. A documentação da API pode ser encontrada [aqui](https://github.com/fernando-gap/steer/blob/main/docs/pt-br/README.pt-br.md).


## Índice

- [Dependencies](#dependencies)
- [The Application](#the-application)
- [Create an OAuth2 URL](#create-an-oauth2-url)
- [Open User's Default Browser](#open-users-default-browser)
- [Create the Loopback IP Address](#create-the-loopback-ip-address)
- [Code Exchange](#code-exchange)
- [Testing](#testing)
- [Refreshing the Access Token](#refreshing-the-access-token)
- [Handle Response Code](#handle-response-code)
- [Revoking the App Access](#revoking-the-app-access)
- [Creating a File to Upload in user's Drive](#creating-a-file-to-upload-in-users-drive)

## Dependências
É assumido que *pip* e *python* já estão instalados, se não instale-as e volte depois :). Faça o seguinte para instalar flask e requests:

```
$ pip install flask
$ pip install requests
```

## A aplicação
O objetivo da aplicação é simples: toda vez que o usuário executa o app um arquivo é escrito em seu Drive, o usuário pode revogar o acesso e a aplicação pode refrescar a chave, que faz com que o usuário não faça a autenticação novamente. Steer não faz o pedido HTTP, por essa razão é necessário implementar.

O exemplo é usado dentro de um "Google project" é deduzido que as chaves de acesso já existam.

## Criando a OAuth2 URL

A primeira coisa de nosso exemplo é criar a URL OAuth2.
```python
# app.py
from steer.oauth.api import OAuth2

oauth = OAuth2(json_path='./config.json')

def step_one(oauth): 
    oauth.create()
```

O arquivo `config.json` contém as seguintes propriedades:
```json
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scope": "https://www.googleapis.com/auth/drive",
    "response_type": "code",
    "redirect_uri": "http://localhost:5000"
}
```


## Abra o Navegador do Usuário
A função `step_one` está *embrulhando* a criação da URL para utilizar depois. 
O argumento `oauth` é uma instancia de `OAuth2`.

```python
def step_one(oauth): 
    oauth.create()
    oauth.open()
```
O usuário deve autorizar a aplicação para acessar o Drive e dizer ao Google para enviar a chave no `Loopback IP address`

## Como Criar o Loopback IP Address
A `redirect_uri` é o método em que o Google deve usar para enviar o código de autorização. Neste caso é o endereço de um servidor local.

A implementação deste servidor é uma simples instancia do framework Flask usada com uma função de co-rotina, que faz com que o servidor desliga para executar outras funções.

```python
from flask import Flask, request, redirect
from signal import SIGINT
import asyncio
import os
```
Importe estes módulos acima no topo de `app.py`.
```python
# ...
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
Nesta fase o arquivo `app.py` deve se paracer como o de cima. Os três pontos no topo escondem dados, apenas para destacar.


A primeira coisa adicionada foi a URL OAuth2. A segunda é um servidor implementado em Flask em que uma co-rotina espera um pedido do Google ser feito para armazenar o `code`.

## Code Exchange
O passo dois é a fase de code exchange que faz a troca de chaves por uma que pode ser usada pela aplicação. 

A função`check_dir` cria uma pasta em `.steer/` em que os dados sobre as chaves são armazenadas e salvas em `.steer/tokens.json`. Se o arquivo já existe ele é atualizado.

```python
#...
def check_dir(data):
    if not os.path.isdir('./.steer'):
        os.mkdir('./.steer')

    with open('./.steer/tokens.json', 'w') as tokens_save:
        tokens_save.write(data)
```

A função `step_two` cria um pedido HTTP `POST` para a fase de code exchange. A variável `tokens` armazena a resposta e retorna do Google como `json`.


```python
# ...
import requests

def step_two(url):
    response = requests.post(url)
    check_dir(response.text)
    tokens = response.json()
    return tokens
```
A aplicação consegue criar de forma automática o processo de autenticação OAuth2 para o Google.

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

O arquivo `app.py` deve se parecer com o de cima.

## Teste a aplicação
Para testar a aplicação execute os seguintes comandos, lembre-se que é preciso se autenticar com uma conta Google ou uma conta de teste.

```
$ python app.py
```

Irá abrir seu navegador padrão e a tela de login do Google será mostrada, chamada de "content screen".

Veja se a aplicação fez o que devia.
```
$ cat .steer/tokens.json
```
É esperado dados em formato json sem estar vazio ou com erro.


## Refrescando o access_token
O proximo passo talvez modifique um pouco `app.py` porque é preciso verificar se o token foi expirado toda vez que o aplicativo roda, pois evita o usuário se autenticar novamente. 

A primeira vez que `has_refresh` é invocado, a função tenta ler os dados de `tokens.json`, se o arquivo não é encontrado um erro é lançado e falso é retornado, isso mostra que o usuário ainda não emitiu uma autenticação.

```python
import json

def has_refresh(oauth):
    try: 
        data = json.loads(open('./.steer/tokens.json').read())
    except FileNotFoundError:
        return False
```

Google envia um novo `refresh_token` toda vez que o usuário passa da "consent screen", contudo o `refresh_token` as vezes pode não aparecer em `tokens.json` quando a chave já foi renovada. Isso significa que `tokens.json` pode e não pode armazenar um `refresh_token`.

```python
import json
#...
def has_refresh(oauth, is_expired):
    try: 
        data = json.loads(open('./.steer/tokens.json').read())
    except FileNotFoundError:
        return False
        
    if 'refresh_token' in data:
        if is_expired:
            token = oauth.refreshtokens(data['refresh_token'])
            tokens_new = requests.post(token)
            
            check_dir(tokens_new.text)
            create_expires_date(tokens_new.json())
            return True
        return True
    else:
        return False

```

Esta modificação pode retornar falso ou verdadeira dependendo se o token está vencido e se tem um `refresh_token` para renovar. Da pra notar que a função `refresh` precisa do argumento `is_expired` que será descrito abaixo.

## Resposta do Google
Como você sabe se um token foi vencido? Um novo módulo foi introduzido que é a classe `OAuth2Response`. Essa classe oferece a possibilidade de verificar se um token foi ou não vencido. O atributo desta classe `before_expires` é o momento em que o token foi passado para a instancia.

Com isso em mente temos o seguinte:
```python
from steer.oauth.response import OAuth2Response

def create_expires_date(tokens):
    tokens_new = OAuth2Response(tokens)

    with open('.steer/expires_token_date.txt', 'w') as expires:
        expires.write(str(response.before_expires))
```
Isto salva a data de quando o token foi emitido pela fase de code exchange.

A proxima coisa a se fazer é verificar se o token está de fato expirado, deve-se retornar falso ou verdadeiro. Se a pasta ou os arquivos não existir, isso significa que o usuário não tem um `access_token`.

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

Para aplicar estas funções em nosso app coloque a função `create_expires_date` dentro da função (no final) `step_two` e `has_refresh` que verifica os  `refresh_tokens` no começo do "main". Como mostrado abaixo.



```python
def step_two(url):
    response = requests.post(url)
    check_dir(response.text)
    tokens = response.json()
    create_expires_date(tokens) # here
    return tokens


if __name__ == '__main__':

    if not has_refresh(oauth, is_token_expired()):
        step_one(oauth)
        asyncio.run(server(oauth))
        token = step_two(code_url)
```
Para testar o app siga as instruções como mencionados [aqui](#teste-a-aplicação).

## Revogando o acesso da aplicação
Para revogar o acesso da aplicação no Drive do usuário, deve-se passar a opção `--revoke` como argumento na command-line, que irá remover a pasta `./steer` e seus conteúdos.

```python
def revoke_access(oauth):
    try:
        with open('./.steer/tokens.json') as tokens:
            token = json.loads(tokens.read())

        deny = oauth.revokeaccess(access_token=token['access_token'])
        requests.post(deny)

        import shutil
        shutil.rmtree('./.steer')
        os._exit(0)

    except FileNotFoundError:
        print('There is nothing to do...')
        os._exit(0)
```
Se a pasta estiver vazia ou não conter os dados necessários o applicativo finaliza o programa.

```python
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--revoke':
        revoke_access(oauth)
         
    if not has_refresh(oauth, is_token_expired()):
        step_one(oauth)
        asyncio.run(server(oauth))
        token = step_two(code_url)   
```

No topo de "main" é checado se `sys.argv` é maior do que um e se o índice um é igual a `--revoke`.

A função `step_three` faz o upload de um arquivo no Google Drive do usuário.
```python
def step_three(token, metadata, file):
    data = {
        "url": "https://www.googleapis.com/upload/drive/v3/files",
        "token": token,
        "meta_data": metadata,
        "file_path": file
    }

    print(token)
    upload = Upload(data)
    url = upload.multipart()
    response = requests.post(url['full_url'], 
                  headers=url['headers']['top-level'], 
                  data=url['body']['data'])

    print(f'status: {response.text}')
    return response.json()
```
A função cria um dicionário `data` para criar um upload do tipo multipart para o Google Drive.

```python
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--revoke':
        revoke_access(oauth)
    
    if not has_refresh(oauth, is_token_expired()):
        step_one(oauth)
        asyncio.run(server(oauth))
        token = step_two(code_url)
    else:
        with open('.steer/tokens.json') as t:
            token = json.loads(t.read())

    step_three(token['access_token'], {"name": "greetings.txt"}, 'greetings.txt')
```

A variável `token` armazena os tokens atuais em que podem ser um novo ou antigo que está no arquivo `tokens.json`.

Este é o fim de nosso exemplo, lembre-se que a documentação pode ser encontrada [aqui](https://github.com/fernando-gap/steer/blob/main/docs/pt-br/README.pt-br.md).
