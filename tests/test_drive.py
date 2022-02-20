import unittest as ut

# it tests all imports
from steer.drive.upload import *
import steer.drive.upload as p
import steer.drive.headers as h


#@ut.skip("Do not use, test raises first")
class TestUploadPrivateFunctions(ut.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.client_data = {
            "url": "https://example.com",
            "params": {
                "this": "must",
                "be": "there"
            },
            "token": "access_token"
        }

        self.media_file = 'test_data/test.txt'
        self.media_metadata = {"name": "test.txt"}
        self.result_full = {
            "method": "POST",
            "url": "https://example.com",
            "params": {
                "this": "must",
                "be": "there",
                "uploadType": "simple"
            },
            "headers": {
                "Authorization": "Bearer access_token",
                "Content-Length": "10",
                "Content-Type": "text/plain"
            },
            "body": {
                "file": "Hi there!\n"
            },
            "full_url": "https://example.com?this=must&be=there&uploadType=simple"
        }

        self.upload = Upload(self.client_data)

    def test_ext(self):
        extension = self.upload._ext('test.txt')
        self.assertEqual(extension, '.txt')

        # multiple dots can have side effects
        extension = self.upload._ext('it.cannot.contain.dots.html')
        self.assertEqual(extension, '.cannot')

        extension = self.upload._ext({})
        self.assertEqual(extension, '.json')


    def test_params(self):
        query = self.upload._params(self.client_data['params'])
        self.assertEqual(query, '?this=must&be=there')


    def test_create_simple(self):
        simple = h._Simple(self.client_data['token'])

        request = self.upload._create_simple(simple, self.media_file)
        self.assertEqual(request, self.result_full)

        del self.result_full['body']['file']
        self.result_full['headers']['Content-Length'] = "20"
        self.result_full['headers']['Content-Type'] = "application/json"
        self.result_full['body'].update({'metadata': self.media_metadata})

        request = self.upload._create_simple(simple, self.media_metadata)
        self.assertEqual(request, self.result_full)



    def test_create_multipart(self):
        multipart = h._Multipart(self.client_data['token'])

        self.result_full['params']['uploadType'] = 'multipart'
        self.result_full['headers'] = {
            'top-level': {
                'Authorization': 'Bearer access_token',
                'Content-Type': 'multipart/related; boundary=file-actions',
                'Content-Length': "30"
            },
            'metadata': {
                'Content-Type': 'application/json; charset=UTF-8'
            },
            'media': {
                'Content-Type': 'text/plain'
            }
        }

        result = '--file-actions\n' \
                 'Content-Type: application/json; charset=UTF-8\n\n' \
                 '{"name": "test.txt"}\n\n' \
                 '--file-actions\n' \
                 'Content-Type: text/plain\n\n' \
                 'Hi there!\n\n\n' \
                 '--file-actions--'

        self.result_full['params']['uploadType'] = 'multipart'
        del self.result_full['body']['file']

        self.result_full['full_url'] = "https://example.com?this=must&be=there&uploadType=multipart"


        self.result_full['body'].update({'data': result})
        request = self.upload._create_multipart(multipart, self.media_file, self.media_metadata)
        self.assertEqual(request, self.result_full)


class TestMultipartRequest(ut.TestCase):
    def setUp(self):
        self.mpreq = p._MultipartRequest()


    def test_content(self):
        req = self.mpreq.content({
            "Content-Type": "text/plain",
            "Content-Length": "30"
        })

        result = 'Content-Type: text/plain\nContent-Length: 30\n'
        self.assertEqual(req, result)

    def test_create(self):
        metadata = {"name": "test.txt"}
        multipart = h._Multipart('access_token')
        multipart.header('test_data/test.txt', '.txt', {"name": "test.txt"})
        reqbody = p._MultipartRequest.create(metadata, 'Hi there!\n', multipart)
        result = '--file-actions\n' \
                 'Content-Type: application/json; charset=UTF-8\n\n' \
                 '{"name": "test.txt"}\n\n' \
                 '--file-actions\n' \
                 'Content-Type: text/plain\n\n' \
                 'Hi there!\n\n\n' \
                 '--file-actions--'

        self.assertEqual(reqbody, result)


class TestUpload(ut.TestCase):
    def setUp(self):
        self.data_details = {
            "url": "https://example.com",
            'params': {
                "field": "value"
            },
            "token": "access_token",
            "file_path": "test_data/test.txt",
            "meta_data": {"name": "test.txt"}
        }


        self.upload_details = Upload(self.data_details)


    def test_simple(self):

        result = {
            "method": "POST",
            "url": "https://example.com",
            "headers": {
                "Authorization": "Bearer access_token",
                "Content-Length": "10",
                "Content-Type": "text/plain"
            },
            "params": {
                "field": "value",
                "uploadType": "simple"
            },
            "body": {
                "file": "Hi there!\n"
            },
            "full_url": "https://example.com?field=value&uploadType=simple"
        }

        request = self.upload_details.simple()
        self.assertEqual(request, result)


        request = self.upload_details.simple('test_data/test.txt')
        self.assertEqual(request, result)


        del self.data_details['file_path']
        del result['body']['file']

        upload_metadata = Upload(self.data_details)

        result['headers']['Content-Length'] = "20"
        result['headers']['Content-Type'] = "application/json"
        result['body'].update({"metadata": {"name": "test.txt"}})

        request = upload_metadata.simple()
        self.assertEqual(request, result)

        request = upload_metadata.simple({"name": "test.txt"})
        self.assertEqual(request, result)


    def test_multipart(self):
        data = '--file-actions\n' \
                 'Content-Type: application/json; charset=UTF-8\n\n' \
                 '{"name": "test.txt"}\n\n' \
                 '--file-actions\n' \
                 'Content-Type: text/plain\n\n' \
                 'Hi there!\n\n\n' \
                 '--file-actions--'

        result = {
            "method": "POST",
            "url": "https://example.com",
            "headers": {
                "top-level": {
                    "Authorization": "Bearer access_token",
                    "Content-Length": "30",
                    "Content-Type": "multipart/related; boundary=file-actions"
                },
                "metadata": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "media": {
                    "Content-Type": "text/plain"
                }
            },
            "params": {
                "field": "value",
                "uploadType": "multipart"
            },
            "body": {
                "data": data
            },
            "full_url": "https://example.com?field=value&uploadType=multipart"
        }

        self.maxDiff = None
        request = self.upload_details.multipart()
        self.assertEqual(request, result)

        del self.data_details['file_path']
        del self.data_details['meta_data']
        request = self.upload_details.multipart(file='test_data/test.txt',
                                                metadata={"name": "test.txt"})


class TestUploadRaises(ut.TestCase):
    def test_init_key_error(self):

        with self.assertRaises(KeyError):
            data = {}
            upload = Upload(data)

        with self.assertRaises(KeyError):
            data = {"url": "url"}
            upload = Upload(data)

        with self.assertRaises(KeyError):
            data = {"url": "url", "params": {}}
            upload = Upload(data)


if __name__ == '__main__':
    ut.main()
