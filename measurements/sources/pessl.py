import os
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

class PesslAPI(BaseSource):
    def __init__(self, public_key, private_key, tz='Etc/GMT-1'):
        self.baseurl = "https://api.fieldclimate.com"
        self.public_key = public_key
        self.private_key = private_key
        self.tz = tz

    def get_auth_headers(self, request, method="GET"):
        d = datetime.datetime.utcnow()
        timestamp = d.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Creating content to sign with private key
        msg = "{}{}{}{}".format(method, request,
                                        timestamp, self.public_key).encode(encoding='utf-8')

        # msg = (self._method + self._apiRoute + dateStamp + self._publicKey).encode(encoding='utf-8')
        h = HMAC.new(self.private_key.encode(encoding='utf-8'), msg, SHA256)
        signature = h.hexdigest()

        # Hash content to sign into HMAC signature
        # signing = hmac.new(self.private_key,
        #                   content_to_sign,
        #                   hashlib.sha256)

        headers = {
            "Accept": "application/json",
            "Authorization": "hmac {}:{}".format(self.public_key,
                                                 signature),
            "Date": "{}".format(timestamp)
        }
        return headers

    def _todf(self, data):
        _colindex = []
        columns = []
        _data = {}
        for sk, s in data['data'].items():
            for aggk, agg in s['aggr'].items():
                _key = "{}_{}".format(sk, aggk)
                columns.append(_key)
                _data[_key] = agg
                _colindex.append((s['name'], aggk))
        colindex = pd.MultiIndex.from_tuples(_colindex, names=['datetime', 'agg'])
        # gmt1 to utc
        # print data['dates']
        # ATTENZIONE: provvisoriamente bisogna forzare un shift di 1 ora per un problema alle API di pessl
        # index = pd.to_datetime(data['dates'])
        # Ora il bug e' stato sistemato lato Pessl
        index = pd.to_datetime(data['dates']) # + pd.to_timedelta(1, 'h')
        # print index
        # index = pd.to_datetime(index, unit='ms')
        df = pd.DataFrame(_data, columns=columns, index=index, dtype='float')
        df.columns = colindex
        return df


    def _get_data(self, code, route='pretty', last=1):
        """
        route: pretty, data, ...
        """

        request = "/{}/{}/raw/last/{}".format(route, code, last)
        headers = self.get_auth_headers(request)
        url = "{}{}".format(self.baseurl, request)
        # print url
        try:
            r = requests.get(url, headers=headers, verify=False)
        except:
            print('ERRORE COMUNICAZIONE')
            return False
        else:
            if r.status_code == 200:
                return r.json()
            return False

    def get_df(self, code, last=1):
        d = self._get_data(code, route='pretty', last=last)
        if d is False:
            return d
        self.df = self._todf(d)

        # merge level names: e.g. variable|aggregate
        self.df.columns = self.df.columns.map('|'.join).str.strip('|')

        # localize datetime index
        self.df.index = self.df.index.tz_localize(self.tz)
        return self.df

