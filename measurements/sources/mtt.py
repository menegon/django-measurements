import os
import datetime
import hmac
import hashlib
import urllib3
urllib3.disable_warnings()
import requests
import pandas as pd

import xml.etree.ElementTree as et

from measurements.sources.base import BaseSource
from measurements.utils import strong_float

class MttAPI(BaseSource):
    def __init__(self, tz='Etc/GMT-1'):
        self.baseurl = "http://dati.meteotrentino.it/service.asmx/ultimiDatiStazione?"
        self.tz = tz

    def get_df(self, code, last=1):
        url = self.baseurl + 'codice=' + code
        r = requests.get(url)
        print(url)

        self.df = self.parse_xml(r.text)

        self.df.index = pd.to_datetime(self.df.index)

        # localize datetime index
        self.df.index = self.df.index.tz_localize(self.tz)
        return self.df

    def parse_xml(self, xml):
        root = et.fromstring(xml)

        def get_data(root, parent, childs):
            data = []
            namespaces = {'mtt': 'http://www.meteotrentino.it/'}
            parent_node = root.find(parent, namespaces)
            if not parent_node:
                return None
            for r in parent_node.findall(childs, namespaces):
                row = {}
                for c in r.getchildren():
                    k = c.tag[30:]
                    v = c.text
                    if k == 'data':
                        row[k] = v
                    else:
                        row[k] = strong_float(v)
                data.append(row)
            if len(data) == 0:
                return None
            df = pd.DataFrame(data)
            df.set_index('data', inplace=True)
            return df

        data_names = (
            ('temperature', 'temperatura_aria'),
            ('precipitazioni', 'precipitazione'),
            ('venti', 'vento_al_suolo'),
            ('radiazione', 'radiazioneglobale'),
            ('umidita_relativa', 'umidita_relativa'),
        )

        dfs = []
        for name in data_names:
            df = get_data(root,
                          "mtt:{}".format(name[0]),
                          "mtt:{}".format(name[1]),)
            if df is not None:
                dfs.append(df)
        dftot = pd.concat(dfs, axis=1)

        # convert km/m to m/s (if exists)
        if 'v' in dftot.columns:
            dftot['v'] = dftot['v'] / 3.6

        return dftot
