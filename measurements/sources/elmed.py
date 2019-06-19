import os
import io
import datetime
import hmac
import hashlib
import urllib3
urllib3.disable_warnings()
import requests
import pandas as pd
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256


from measurements.sources.base import BaseSource

class ElmedAPI(BaseSource):
    def __init__(self, public_key, private_key, tz='Europe/Rome'):
        self.baseurl = "http://www.elmedweb.com/MeteoWeb/download/download.php?"
        self.public_key = public_key
        self.private_key = private_key
        self.tz = tz


    def get_df(self, code, last=1):
        end_date = datetime.datetime.today()
        start_date = end_date - datetime.timedelta(days=last)
        payload = {"stationnr[]": code,
                   "auth": self.private_key,
                   "format": "csv_large",
                   "start_date": start_date.strftime('%d-%m-%Y'),
                   "end_date": end_date.strftime('%d-%m-%Y')
                   }
        r = requests.get(self.baseurl, params=payload)
        df = pd.read_csv(io.StringIO(r.text))

        # set datetime index
        df.Datum = pd.to_datetime(df.Datum, format="%Y%m%d %H:%M:%S")
        df.set_index('Datum', inplace=True)
        self.df = df

        self.df.index = self.df.index.tz_localize(self.tz)
        return df
