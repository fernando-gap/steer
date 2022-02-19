import os

class Header:
    """The class creates headers to use in the Upload/Update classes.

    The class is meant to be the Parent to other headers and should
    only be used to create basic headers; it provides basic
    functionality to handle MIME and Length headers.

    Get Methods:
    get_mime(self, extension)
    Return any valid mime sent by a file extension.

    The @mime_types: dict param defines commom MIME types.
    If there are no valid values for the mime type specified
    the program returns None.

    Arguments:
    :extension: str  the param contain an extension e. g. .jpeg

    Usage:
    Pass a valid extension name to get its valide MIME type
    defined by IANA and specified by RFC 2046.
    >>> header.get_mime('.json')
    "application/json"


    get_header(self, which)
    Return a header already defined, otherwise return None

    Arguments:
    :which: str  a field name, example Content-Length

    Usage:
    Pass a field name value to get its content
    >>> header.get_header('Content-Type')
    "application/json"
    """

    def __init__(self, token):
        """Define the commom mime types and initializes the headers.

        Arguments:
        token: str -- An access_token given by google oauth2 server.
        """

        # it will always exists authorization header
        self.headers = {
            "Authorization": "Bearer " + token
        }

        self.mime_types = {
            ".txt":"text/plain",
            ".bin":"application/octet-stream",
            ".aac":"audio/aac",
            ".abw":"application/x-abiword",
            ".arc":"application/x-freearc",
            ".avif":"image/avif",
            ".avi":"video/x-msvideo",
            ".azw":"application/vnd.amazon.ebook",
            ".bmp":"image/bmp",
            ".bz":"application/x-bzip",
            ".bz2":"application/x-bzip2",
            ".cda":"application/x-cdf",
            ".csh":"application/x-csh",
            ".css":"text/css",
            ".csv":"text/csv",
            ".doc":"application/msword",
            ".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".eot":"application/vnd.ms-fontobject",
            ".epub":"application/epub+zip",
            ".gz":"application/gzip",
            ".gif":"image/gif",
            ".htm":"text/html",
            ".html":"text/html",
            ".ico":"image/vnd.microsoft.icon",
            ".ics":"text/calendar",
            ".jar":"application/java-archive",
            ".jpeg":"image/jpeg",
            ".jpg":"image/jpeg",
            ".js":"text/javascript",
            ".json":"application/json",
            ".jsonld":"application/ld+json",
            ".mid":"audio/midi",
            ".midi":"audio/x-midi",
            ".mjs":"text/javascript",
            ".mp3":"audio/mpeg",
            ".mp4":"video/mp4",
            ".mpeg":"video/mpeg",
            ".mpkg":"application/vnd.apple.installer+xml",
            ".odp":"application/vnd.oasis.opendocument.presentation",
            ".ods":"application/vnd.oasis.opendocument.spreadsheet",
            ".odt":"application/vnd.oasis.opendocument.text",
            ".oga":"audio/ogg",
            ".ogv":"video/ogg",
            ".ogx":"application/ogg",
            ".opus":"audio/opus",
            ".otf":"font/otf",
            ".png":"image/png",
            ".pdf":"application/pdf",
            ".php":"application/x-httpd-php",
            ".ppt":"application/vnd.ms-powerpoint",
            ".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".rar":"application/vnd.rar",
            ".rtf":"application/rtf",
            ".sh":"application/x-sh",
            ".svg":"image/svg+xml",
            ".swf":"application/x-shockwave-flash",
            ".tar":"application/x-tar",
            ".tif":"image/tiff",
            ".tiff":"image/tiff",
            ".ts":"video/mp2t",
            ".ttf":"font/ttf",
            ".vsd":"application/vnd.visio",
            ".wav":"audio/wav",
            ".weba":"audio/webm",
            ".webm":"video/webm",
            ".webp":"image/webp",
            ".woff":"font/woff",
            ".woff2":"font/woff2",
            ".xhtml":"application/xhtml+xml",
            ".xls":"application/vnd.ms-excel",
            ".xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xml":"application/xml",
            ".xul":"application/vnd.mozilla.xul+xml",
            ".zip":"application/zip",
            ".3gp":"audio/3gpp",
            ".3g2":"video/3gpp2",
            ".7z":"application/x-7z-compressed"}

    def add_mime(self, media_extension, type_):
        self.mime_types.update({media_extension: type_})

    def add_header(self, field, value, header = None):
        if header == None:
            self.headers.update({field: value})
        else:
            header.update({field: value})


    def get_mime(self, extension):
        try:
            return self.mime_types[extension]
        except KeyError:
            return None

    def get_header(self, which):
        try:
            return self.headers[which]
        except KeyError:
            return None


    def get_length(self, file):

        # length is either a file or a dictionary
        if type(file) == str:
            length = os.path.getsize(file)
        else:
            # UTF-8 uses a octet format for each character
            length = len(str(file).encode('utf-8'))
        Header.add_header(self, 'Content-Length', str(length))


class Simple(Header):
    def header(self, extension, file):
        self.add_header('Content-Type', self.get_mime(extension))
        self.get_length(file)
        return self.headers


class Multipart(Header):
    """Create necessary headers to make an

    HTTP multipart/related request according to RFC 2387
    """



    def __init__(self, token):
        """Initializes two essential parts of multipart/related

        requests according to Google API: metadata and media parts
        Create two distinc objects for each one.
        """


        super().__init__(token)

        self.headers_metadata = {}
        self.headers_media = {}

        self.boundary = 'file-actions'


    def metadata_header(self):
        # all metadata requests is type application/json
        self.add_header('Content-Type',
                        'application/json; charset=UTF-8',
                        self.headers_metadata)

    def media_header(self, extension):
        self.add_header('Content-Type',
                        self.get_mime(extension),
                        self.headers_media)


    def header(self, file, extension):
        self.add_header('Content-Type', f'multipart/related; boundary={self.boundary}')
        self.get_length(file)

        Multipart.metadata_header(self)
        Multipart.media_header(self, extension)

        # return an object containing all headers
        return {'top-level': self.headers,
                'metadata': self.headers_metadata,
                'media': self.headers_media}


