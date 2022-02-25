
from steer.drive.headers import _Simple
from steer.drive.headers import _Multipart


class Upload:
    """Create a HTTP request to upload files in Google Drive."""


    def __init__(self, data):
        """The HTTP request creates a URL using a dictionary.

        Arguments:
        data: dict -- The following properties must be or may be
        included:

        :url: str,        (Google drives url)
        :params: dict,    (params passed to the url)
        :token: str,      (access_token given by google)
        :meta_data: dict, (*warn)
        :file_path: str,

        *warn -- Meta data is only uploaded when the file_path is
        empty if the simple method is to be used.
        """

        if 'params' not in data:
            data['params'] = {}

        # check required params
        for keys in ['url', 'token']:
            if keys not in data:
                raise KeyError

        self.method = 'POST'
        self.data = data


    def _ext(self, fname):
        """Return the extension of a file name whether an invalid or empty

        name is provided it should return '' an empty string.


        If the argmuent is a dictionary the returning value is '.json'

        Arguments:
        fname: str -- The name of the file

        Usage:
        >>> Update._ext(self, 'file.txt')
        ".txt"

        >>> Update._ext(self)
        None
        """

        if type(fname) == dict:
            return '.json'


        from re import compile
        ext = compile('\.[a-z]*').search(fname)

        try:
            return ext[0]
        except TypeError:
            return None


    def _params(self, query):
        """Build query params for the URL in the form of:

         >>> '?param_1=data_1&param_2=data_2'
           
        Arguments:
        query: dict -- User's chosen params = 'name': 'value'

        Return:

        :queries: str
        """

        # is the param, the first? '?param='
        is_first_param = 0
        queries = ''

        for param, value in query.items():
            if is_first_param == 0:
                queries += f'?{param}={value}'
                is_first_param += 1
            else:
                queries += f'&{param}={value}'

        return queries


    def _create_multipart(self, headers_type, file, metadata):
        request = {
            'method': self.method,
            'url': self.data['url'],
            'params': self.data['params']
        }

        if file != None and metadata != None:

            # multipart request both sizes of metadata and media
            headers = headers_type.header(file, self._ext(file), metadata)

            request.update({
                'headers': headers
            })

            # create body request
            self.data['params'].update({'uploadType': 'multipart'})
            with open(file) as file:
                request.update({
                    'body': {
                        'data': _MultipartRequest.create(
                            metadata,
                            file.read(),
                            headers_type
                        )
                    }
                })
            request.update({
                'full_url': self.data['url'] + self._params(self.data['params'])
            })

            return request
        else:
            # in case there is no metadata or file
            raise NameError


    def _create_simple(self, headers_type, media):
        request = {
            'method': self.method,
            'url': self.data['url'],
            'params': self.data['params']
        }

        headers = headers_type.header(media, Update._ext(self, media))
        request.update({'headers': headers})

        self.data['params'].update({'uploadType': 'simple'})

        # create body request
        if type(media) == str:
            with open(media) as file:
                request.update({
                    'body': {
                        'file': file.read()
                    }
                })
        else:
            request.update({
                'body': {
                    'metadata': media
            }})


        # create full url
        request.update({
            'full_url': self.data['url'] + self._params(self.data['params'])
        })
        return request


    def simple(self, media = None):

        """Media Simple Upload URL to create a HTTP request model.

        It cannot upload both file or metadata.

        Summary:
            - Arguments
            - Usage
            - Return


        Arguments:
        media: str/dict -- 'path/to/file', or a metadata dictionary


        Usage:
        Without pass any argument:
        >>> instance = drive.Upload(request)
        >>> instance.simple()

        Passing an argument either a file or a metadata.
        >>> instance.simple(media='path/to/file')
        >>> instance.simple(media={data})

        Return:
        A dictionary containing the necessary information to create
        a request.

        The dict contain the following properties:

        :method: str   -- specify which method to use
        :url: str      -- url which the user choose to post to
        :headers: dict -- headers *specific* to the uploadType
        :body: dict    -- request body where the data is stored.

        it contains the following properties:
            - :file: str      -- file data if provided
            - :metadata: dict -- meta data if provided

        :full_url: str   -- the url with all params
        :params: dict    -- all params stored in a dict type
        """

        simple = _Simple(self.data['token'])

        # try use the function parameters
        try:
            return Update._create_simple(self, simple, media)
        except TypeError:

            # try to use the given instance properties.
            # python do not let access the property 
            # before it is defined, otherwise python returns 
            # AttributeError.

            try:
                return Update._create_simple(self, simple, self.data['file_path'])

            except KeyError:
                return Update._create_simple(self, simple, self.data['meta_data'])


    def multipart(self, file = None, metadata = None):
        """Create a HTTP multipart/related POST request model.

        According to RFC 2387 the multipart request is needed when
        the upload is part of a compound object. In this case, the
        object is the file, it is composed of a metadata and its
        content.

        Arguments:
        file: str -- a path to a file in the user system
        metadata: dict -- a data containing the metadata to the file


        Usage:
        It cannot upload a file without a metadata, and vice versa.
        >>> drive.multipart(file=None, metadata={ "name": "test.txt" })
        Traceback (most recent call last):
            AttributeError

        An AttributeError raises when neither a metadata nor a file is
        found. Before any error the function looks at the given instance
        data to find any other values defined by the user, if those is
        non-existent then the function raises an AttributeError.


        Return:

        A dictionary containing the necessary information to create
        a request.

        The dict contain the following properties:

        :method: str   -- specify which method to use
        :url: str      -- url which the user choose to post to
        :headers: dict -- headers *specific* to the uploadType
        :body: dict    -- request body where the data is stored.
        it contains the following properties:
            - :data: str -- the multipart/request body

        :full_url: str   -- the url with all params
        :params: dict    -- all params stored in a dict type
        """

        multipart_ = _Multipart(self.data['token'])

        try:
            return Update._create_multipart(self, multipart_, file, metadata)
        except NameError:
            return Update._create_multipart(self, multipart_,
                                   self.data['file_path'],
                                   self.data['meta_data'])


class Update(Upload):
    pass


class _MultipartRequest:

    def content(self, header):
        """Transform a dict of headers into a string with a newline."""

        header_str = ''
        for key in header:
            header_str += f'{key}: {header[key]}\n'

        return header_str


    @classmethod
    def create(cls, metadata, media, h):
        import json
        #header = h
        return (f'--{h.boundary}\n'
                f'{cls.content(cls, h.headers_metadata)}\n'
                f'{json.dumps(metadata)}\n\n'
                f'--{h.boundary}\n'
                f'{cls.content(cls, h.headers_media)}\n'
                f'{media}\n\n'
                f'--{h.boundary}--')

