from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings()
import requests
import pandas as pd
from bs4 import BeautifulSoup

from measurements.sources.base import BaseSource


ARSO_PARAMS = {'znacilna_visina_valov': 'WAVEH',
               'smer_valovanja': 'WAVED',
               'vodostaj': 'SLEV'
               }


class ArsoAPI(BaseSource):
    def __init__(self, tz='UTC'):
        self.baseurl = 'http://www.arso.gov.si/xml/vode/hidro_podatki_zadnji.xml'
        self.tz = tz
        self.data = None
        self.stations = None

    def get_data(self, force=False):
        if self.data is not None and not force:
            return self.data
        else:
            r = requests.get(self.baseurl)
            self.data = BeautifulSoup(r.text, 'xml')
            return self.data

    def get_stations(self):
        if self.stations is not None:
            return self.stations
        else:
            self.stations = {}
            self.get_data()
            for s in self.data.find_all('postaja'):
                code = s.attrs['sifra']
                label = s.merilno_mesto.string
                self.stations[code] = label
            return self.stations

    def get_df(self, code, last=1):
        parameter = 'SLEV'

        stations = self.get_data()

        data = []
        for p in stations.find_all('postaja', sifra=code):
            _time = datetime.strptime(p.datum.string, "%Y-%m-%d %H:%M")
            time = _time - timedelta(hours=1)
            for tag, parameter in ARSO_PARAMS.items():
                # parameter = 'SLEV'
                t = p.find(tag)
                if t is not None and t.string is not None:
                    _value = float(t.string)
                    if parameter == 'SLEV':
                        _value = _value / 100.
                        baselevel = float(p.attrs['kota_0'])
                        value = baselevel + _value
                    else:
                        value = _value
                    try:
                        data.append({
                            "datetime": time,
                            "value": float(value),
                            'parameter': parameter,
                        })
                    except TypeError as e:
                        print(str(e))
        if len(data) == 0:
            self.df = None
            return self.df
        df = pd.DataFrame(data)
        print(df)
        df.set_index('datetime', inplace=True)
        self.df = df.pivot(values='value', columns='parameter')
        self.df.index = self.df.index.tz_localize(self.tz)
        return self.df

