from django.test import TestCase
from django.test import Client

from apps.sharefiles.utils import random_prefix

# Create your tests here.
class LargeFileUploadTest(TestCase):
    '''
    test from the api(controller) level 
    '''
    def setup(self):
        c = Client()
        self.c = c
        self.c.login(username="da",password='123')
        data = {"name": "unit-test","password": "test_"}
        respones = self.c.post('/easyshare/folder/user',data=data)
        self.test_folder_id = respones.json()['id']

    def test_upload_chunks(self):
        
        ...
    
    def test_status_record(self):
        url = '/easyshare/large_file_upload_status'

        response = self.c.get(url)
        self.assertEqual(response.status_code,400)

        response = self.c.get(url,data={'md5':random_prefix()})
        self.assertEqual(response.status_code,404)
        
        ...

    def test_create_instance(self):
        ...