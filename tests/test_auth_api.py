import unittest

from api import signature
from datetime import datetime
import random
import app as myapp


class TestAuth(unittest.TestCase):

    def setUp(self):
        myapp.app.testing = True
        self.app = myapp.app.test_client()

    def test_sendsms(self):
        import math
        nonce = math.floor(random.uniform(100000, 1000000))
        params = {'phone': '18922986865', 'appkey': '432ABZ', 'timestamp': datetime.now().timestamp(),
                  'nonce': nonce}
        sign = signature(params)
        params['sign'] = sign

        respdata = self.app.post("/api/auth/sendsms", data=params)
        resp = respdata.json
        self.assertEqual(resp['code'], 0, respdata.data)

    def test_login(self):
        import math
        nonce = math.floor(random.uniform(100000, 1000000))
        params = {'phone': '18922986865', 'appkey': '432ABZ', 'timestamp': datetime.now().timestamp(),
                  'nonce': nonce, 'code': '97532'}
        sign = signature(params)
        params['sign'] = sign
        respdata = self.app.post("/api/auth/login", data=params)
        resp = respdata.json
        self.assertEqual(resp['code'], 0, respdata.data)


if __name__ == '__main__':
    unittest.main()
