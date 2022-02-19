import unittest as ut
import steer

class TestHeaders(ut.TestCase):

    def setUp(self):
        self.header = steer.Header('access_token')


    def test_add_mime(self):
        self.header.add_mime('.efi', 'application/efi')
        self.assertEqual(self.header.mime_types['.efi'], 'application/efi')

    def test_add_header(self):
        self.header.add_header('Content-Type', 'text/plain')
        self.assertEqual(self.header.headers['Content-Type'], 'text/plain')
        header_dict = {}
        self.header.add_header('Content-Type', 'text/html', header_dict)
        self.assertTrue('Content-Type' in header_dict)


    def test_get_mime(self):
        mimetype_one = self.header.get_mime('.zip')
        self.assertEqual(mimetype_one, 'application/zip')

        mimetype_two = self.header.get_mime('.noexist')
        self.assertEqual(mimetype_two, None)

    def test_get_header(self):
        header_got = self.header.get_header('Authorization')
        self.assertEqual(header_got, 'Bearer access_token')

        header_got = self.header.get_header('Nonexistent')
        self.assertEqual(header_got, None)
    
    def test_get_length(self):
        self.header.get_length('./test_data/bytes.txt')
        self.assertEqual(self.header.headers['Content-Length'], '99')


class TestSimple(ut.TestCase):
    
    def setUp(self):
        self.simple = steer.Simple('access_token')


    def test_header(self):
        headers_simple = self.simple.header('.txt', './test_data/bytes.txt')
        self.assertEqual(headers_simple, {'Authorization': 'Bearer access_token',
                                          'Content-Type': 'text/plain',
                                          'Content-Length': '99'})



class TestMultipart(ut.TestCase):

    def setUp(self):
        self.multipart = steer.Multipart('access_token')


    def test_metadata_header(self):
        self.multipart.metadata_header()
        self.assertEqual(self.multipart.headers_metadata['Content-Type'], 
                                        'application/json; charset=UTF-8')


    def test_media_header(self):
        self.multipart.media_header('.gif')
        self.assertEqual(self.multipart.headers_media['Content-Type'], 'image/gif')

    def test_header(self):
        headers = self.multipart.header('./test_data/bytes.txt', '.txt')
        headers_all = {
            'top-level': {
                'Authorization': 'Bearer access_token',
                'Content-Type': 'multipart/related; boundary=file-actions',
                'Content-Length': '99'
            },
            'metadata': {
                'Content-Type': 'application/json; charset=UTF-8'
            },
            'media': {
                'Content-Type': 'text/plain'
            }
        }

        self.assertEqual(headers, headers_all)

if __name__ == '__main__':
    ut.main()

