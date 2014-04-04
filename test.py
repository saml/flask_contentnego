from flask import url_for

from app import create_app

import unittest

def content_type(resp):
    return resp.headers['Content-Type'].split(';')[0]

class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.test.cfg')
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        if self.ctx is not None:
            self.ctx.pop()


    def test_list(self):
        resp = self.client.get(url_for('classes.list'))
        self.assertEqual(content_type(resp), 'application/json')

        resp = self.client.get(url_for('classes.list'), headers={'Accept': 'text/html;q=0.2,application/json;q=0.3'})
        self.assertEqual(content_type(resp), 'application/json')

        resp = self.client.get(url_for('classes.list'), headers={'Accept': 'text/html;q=0.5,application/json;q=0.3'})
        self.assertEqual(content_type(resp), 'text/html')

if __name__ == '__main__':
    unittest.main()
