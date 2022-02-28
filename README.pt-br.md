# Steer
OAuth2 e Google Drive "upload" de um modo simples. A API Steer cria todas as URLs necessárias para a autenticação na API do Google. Além disso, Steer oferece a possibilidade de criar URLs para enviar arquivos ao Google Drive, steer traz dois tipos de envio de arquivos "simple" e "multipart".

## Instalação
Para instalar Steer "python3" e "pip" são necessários.

```
pip install steer
```

Leia a documentação em [docs](https://github.com/fernando-gap/steer/tree/main/docs) para começar com Steer.

## Saiba como funciona

Steer cria uma URL de acordo com os métodos definidos pelo Google, que podem ser encontrados [aqui](https://developers.google.com/identity/protocols/oauth2/native-app#programmatic-extraction), e para o Drive [aqui](https://developers.google.com/drive/api/v3/manage-uploads#http_1). 

### OAuth2
OAuth2 é um protocolo de autorização que permite o acesso de dados de plataformas como o Google a partir de aplicações de terceiros. Suponha que uma aplicação cria uma pasta no Google Drive de um usuário para armazenar seus dados.

Para fazer a autenticação OAuth2 é preciso uma permissão dada pelo Google, que é a chave de acesso, a permissão do usuário também é importante, essa é vista  pelo usuário na tela de consentimento do Google. Se a concessão for sucedida a aplicação pode utilizar o Drive para quardar seus dados.

Steer facilita o processo de criação de URL para a autenticação do protocolo OAuth2. Tenha em mente, Steer não envia pedidos HTTP, em vez disso, cria a URL para fazer o pedido, que faz possivel a utilização de qualquer cliente HTTP, assim como [requests](https://docs.python-requests.org/en/master/).


### Drive Upload
Steer apresenta uma interface para a criação de um *modelo* HTTP para o Google Drive. Isso significa que Steer desenvolve todos os "headers", "request body", "parameters", etc. para fazer o pedido HTTP de forma imediata.

Três métodos são utilizados de acordo com Google: "simple", "multipart" e "resumable". Apenas "simple" e "multipart" são oferecidos pela API.

- O método "simple" pode enviar "metadata" e dados do arquivo, mas nunca ambos.
- O método "multipart" envia ambos os dados e "metadata", porém não pode enviar um sem o outro.


# Licença
Este projeto está vínculado a "MIT License"
