from datetime import datetime
import urllib3

urllib3.disable_warnings()
import requests
import pandas as pd
from bs4 import BeautifulSoup

from measurements.sources.base import BaseSource
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from owslib.sos import SensorObservationService
from owslib.fes import FilterCapabilities
from owslib.ows import OperationsMetadata
from owslib.crs import Crs
from owslib.swe.sensor.sml import SensorML
from owslib.etree import etree
from owslib.swe.observation.sos200 import namespaces
from owslib.util import nspath_eval
import json

SOSURL = "http://vesk.ve.ismar.cnr.it/observations/sos/kvp?"
SOSVERSION = "2.0.0"
SOS_PARAMS = {'http://vocab.nerc.ac.uk/collection/P01/current/GHMZAD01/': 'WAVEH'}


class GetitAPI(BaseSource):
    def __init__(self, tz='UTC'):
        self.baseurl = "http://vesk.ve.ismar.cnr.it/observations/sos/kvp?"
        self.tz = tz
        self._service = None
        self._sensors = None
        self._offerings = None
        self._observed_properties = None
        self.data = None

    @property
    def service(self):
        if self._service is None:
            service = SensorObservationService(SOSURL,
                                               version=SOSVERSION)
            self._service = service
        return self._service

    @property
    def sensors(self):
        if self._sensors is None:
            sensors = {}
            get_obs = self.service.get_operation_by_name('GetObservation')
            describe_sensor = self.service.get_operation_by_name('DescribeSensor')
            sensor_ids = describe_sensor.parameters['procedure']['values']
            for sensor_id in sensor_ids:
                response = self.service.describe_sensor(outputFormat='http://www.opengis.net/sensorML/1.0.1',
                                                        procedure=sensor_id)
                tr = etree.fromstring(response)
                element = tr.find('.//' + nspath_eval('sml:SensorML', namespaces))
                ds = SensorML(element)
                name = ds.members[0].name
                sensors[sensor_id] = name
            self._sensors = sensors
        return self._sensors

    @property
    def offerings(self):
        if self._offerings is None:
            self._offerings = [off.id for off in self.service.offerings]
        return self._offerings

    @property
    def observed_properties(self):
        if self._observed_properties is None:
            self._observed_properties = list(set(op for off in self.service.offerings for op in off.observed_properties))
        return self._observed_properties

    def get_df(self, code, last=20):
        if self.data is None:
            end_time = datetime.now()  # - timedelta(hours=120*10)
            start_time = end_time - timedelta(hours=last)
            temporalFilter = "om:phenomenonTime,{}/{}".format(start_time.isoformat(), end_time.isoformat())
            response_format = 'application/json'
            _namespaces = "xmlns(om,http://www.opengis.net/om/2.0)"

            _observed_properties = list(SOS_PARAMS.keys())
            print(_observed_properties)
            _response = self.service.get_observation(offerings=self.offerings,
                                                responseFormat=response_format,
                                                observedProperties=_observed_properties,
                                                namespaces=_namespaces,
                                                temporalFilter=temporalFilter)
            data = []
            print(_response)
            response = json.loads(_response)
            for obs in response['observations']:
                location = obs['featureOfInterest']['name']['value']
                _parameter = obs['observableProperty']
                parameter = SOS_PARAMS.get(_parameter)
                _datetime = obs['phenomenonTime']
                value = float(obs['result']['value'])
                rjson = {
                    'location': location,
                    'parameter': parameter,
                    "datetime": _datetime,
                    "value": value
                }
                data.append(rjson)
            if len(data) == 0:
                return None
            self.data = pd.DataFrame(data)

        _df = self.data[self.data.location == code]
        return _df.pivot(index='datetime', values='value', columns='parameter').head()

def syncvesk():
    sensors = {}
    service = SensorObservationService(SOSURL,
                                       version=SOSVERSION)
    get_obs = service.get_operation_by_name('GetObservation')
    describe_sensor = service.get_operation_by_name('DescribeSensor')
    sensor_ids = describe_sensor.parameters['procedure']['values']
    for sensor_id in sensor_ids:
        response = service.describe_sensor(outputFormat='http://www.opengis.net/sensorML/1.0.1',
                                     procedure=sensor_id)
        tr = etree.fromstring(response)
        element = tr.find('.//' + nspath_eval('sml:SensorML', namespaces))
        ds = SensorML(element)
        name = ds.members[0].name
        sensors[sensor_id] = name


    offerings = [off.id for off in service.offerings]
    _observed_properties = list(set(op for off in service.offerings for op in off.observed_properties))
    observed_properties = SOS_PARAMS.keys()
    end_time = datetime.now() # - timedelta(hours=120*10)
    start_time = end_time - timedelta(hours=12)
    temporalFilter = "om:phenomenonTime,{}/{}".format(start_time.isoformat(), end_time.isoformat())
    response_format = 'application/json'
    _namespaces = "xmlns(om,http://www.opengis.net/om/2.0)"

    _response = service.get_observation(offerings=offerings,
                                        responseFormat=response_format,
                                        observedProperties=observed_properties,
                                        namespaces=_namespaces,
                                        temporalFilter=temporalFilter)
    response = json.loads(_response)
    for obs in response['observations']:
        location = obs['featureOfInterest']['name']['value']
        _parameter = obs['observableProperty']
        parameter = SOS_PARAMS.get(_parameter)
        timestamp = obs['phenomenonTime']
        network = 'CNR'
        value = float(obs['result']['value'])
        rjson = {
            'location': location,
            'parameter': parameter,
            "timestamp": timestamp,
            'network': network,
            "value": value
        }
        _write([rjson])


        pass
    pass
