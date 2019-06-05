import os
import datetime
import hmac
import hashlib
import urllib3
urllib3.disable_warnings()
import requests
import pandas as pd
import csv
from dateutil import parser


import xml.etree.ElementTree as et

from measurements.sources.base import BaseSource
from measurements.utils import strong_float

class DavisAPI(BaseSource):
    def __init__(self, tz='Europe/Rome'):
        self.baseurl = "http://www.meteosystem.com/wlip/"
        self.tz = tz

    def get_df(self, code, last=1):
        url = self.baseurl + code + '.php'
        r = requests.get(url)
        decoded_content = r.content.decode('utf-8')
        reader = csv.reader(decoded_content.splitlines(),
                            delimiter='|',
                            doublequote=False,
                            quoting=csv.QUOTE_NONE)
        data = []
        for j, row in enumerate(reader):
            print(j, row)
            data_str = row[1] + ' ' + row[0].replace('ERR', '').replace('.', ':')
            _datetime = parser.parse(data_str, dayfirst=True)
            print(_datetime)
            r = {'datetime': _datetime,
                 'TempAria': strong_float(row[2]),
                 'UmidAriaRel': strong_float(row[3]),
                 'PntRugiada': strong_float(row[4]),
                 'IndCalore': strong_float(row[5]),
                 'IndRaffr': strong_float(row[6]),
                 'PressAtm': strong_float(row[7]),
                 'RadSol': strong_float(row[8]),
                 'TempAriaMin': strong_float(row[11]),
                 'TempAriaMax': strong_float(row[14]),
                 'VelVento': strong_float(row[44]),
                 'VelVentoMed10min': strong_float(row[46]),
                 'RafficaVento': strong_float(row[47]),
                 'Precip': strong_float(row[49]),
                 'PercPrecipMax': strong_float(row[50]),
                 'PrecipGiorno': strong_float(row[54]),
                 'PrecipMese': strong_float(row[56]),
                 'PrecipAnno': strong_float(row[58])
                 }
            data.append(r)

        # return True
        self.df = pd.DataFrame(data)
        self.df.set_index('datetime', inplace=True)
        self.df.index = pd.to_datetime(self.df.index)

        # localize datetime index
        self.df.index = self.df.index.tz_localize(self.tz)
        return self.df


