import unittest

from api import signature
from datetime import datetime
import random
import app as myapp


class TestUser(unittest.TestCase):

    def setUp(self):
        myapp.app.testing = True
        self.app = myapp.app.test_client()

    def test_hotlist(self):
        import math
        nonce = math.floor(random.uniform(100000, 1000000))
        params = {'phone': '18922986865', 'userId': '100784', 'appkey': '432ABZ',
                  'token': '575f680ddbd0d494a1b5fad8497293d2',
                  'timestamp': datetime.now().timestamp(),
                  'nonce': nonce}
        sign = signature(params)
        params['sign'] = sign

        respdata = self.app.get("/api/user/hot/list", data=params)

        self.assertEqual(200, respdata.status_code)

        resp = respdata.json
        self.assertEqual(0, resp['code'], respdata.data)
        self.assertIsNotNone(resp['data'], respdata.data)

    def test_update(self):
        import math
        nonce = math.floor(random.uniform(100000, 1000000))
        params = {'token': '575f680ddbd0d494a1b5fad8497293d2', 'userId': '100784', 'appkey': '432ABZ',
                  'timestamp': datetime.now().timestamp(),
                  'nonce': nonce}
        sign = signature(params)
        params['sign'] = sign

        respdata = self.app.post("/api/user/update", data=params)
        self.assertEqual(200, respdata.status_code)

        resp = respdata.json
        self.assertEqual(0, resp['code'], respdata.data)
        self.assertIsNotNone(resp['data'], respdata.data)


if __name__ == '__main__':
    unittest.main()
