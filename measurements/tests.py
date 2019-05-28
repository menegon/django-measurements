from django.test import RequestFactory, TestCase, Client
from django.contrib.auth.models import AnonymousUser, User

from measurements.writeapi import write
from measurements.models import Measure

LP_INVALID = """mymeas,mytag1=1 value=21 1463689680000000000"""

LP_VALID = """waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=21 1463689680000000000
waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=22 1463689690000000000
waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=23 1463689700000000000
"""

class WriteAPITest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_invalid_serie(self):
        request = self.factory.post('/measurements/api',
                                    data=LP_INVALID,
                                    content_type='application/octet-stream'
                                    )
        request.user = AnonymousUser()
        self.assertRaises(ValueError, write, request)

    def test_write(self):
        request = self.factory.post('/measurements/api',
                                    data=LP_VALID,
                                    content_type='application/octet-stream'
                                    )
        # TODO:
        request.user = AnonymousUser()
        write(request)
        self.assertTrue(Measure.objects.exists())

