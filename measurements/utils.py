from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from psqlextra.query import ConflictAction
from measurements.models import Measure, Station, Parameter, Sensor, Serie
import colorbrewer
from numpy import array



def get_serie(station, parameter, sensor='unknown', height=None):
    if not isinstance(station, Station):
        station, created = Station.objects.get_or_create(code=station)
    if not isinstance(parameter, Parameter):
        parameter, created = Parameter.objects.get_or_create(code=parameter)
    if not isinstance(sensor, Sensor):
        sensor, created = Sensor.objects.get_or_create(code=sensor)

    serie, created = Serie.objects.get_or_create(station=station,
                                                 parameter=parameter,
                                                 sensor=sensor,
                                                 height=height)
    return serie


def load_serie(data, serie_id):
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    # check for empty series
    if df.shape[0] == 0:
        return False
    df.reset_index(inplace=True)
    df.columns = ['timestamp', 'value']
    df['serie_id'] = serie_id
    conflict_columns = ['serie_id', 'timestamp']

    datadict = df.to_dict(orient='record')
    Measure.extra.on_conflict(conflict_columns,
                              ConflictAction.UPDATE).bulk_insert(datadict)
    return True


def strong_float(value):
    if value in [None, '']:
        return None
    else:
        return float(value)


def get_time(time):
    now = datetime.now()
    if time == 'today':
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)
    elif time == 'yesterday':
        yesterday = now - timedelta(days=1)
        start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)
    elif time == '12h':
        start_time = now - timedelta(hours=12)
        end_time = now
    elif time == '24h':
        start_time = now - timedelta(hours=24)
        end_time = now
    elif time == '36h':
        start_time = now - timedelta(hours=36)
        end_time = now
    elif time == '48h':
        start_time = now - timedelta(hours=48)
        end_time = now
    elif time == '72h':
        start_time = now - timedelta(hours=72)
        end_time = now
    elif time == 'week':
        start_time = now - timedelta(weeks=1)
        end_time = now
    elif time == '30g':
        start_time = now - timedelta(days=30)
        end_time = now

    return start_time, end_time


def classify_fc(fc, k=8, zeros=True, cmap='Blues'):
    """Classify in place a FeatureCollection object.

    Arguments:
    fc -- FeatureCollection object
    k -- number of classes
    """
    items = fc['features']
    values = array([float(i['properties']['value']) for i in items])
    if not zeros:
        _values = values[values != 0]
    else:
        _values = values
    #
    if _values[_values != 0].size == 0:
        _values = array([0, 1])
    counts, bins = np.histogram(_values, bins=k)
    # classes = Equal_Interval(_values, k)

    # cmap = get_cmap(cmap, k)
    cmap = getattr(colorbrewer, cmap)[k]

    for i in items:
        value = float(i['properties']['value'])
        bin = np.fmin(np.digitize(value, bins), k)
        # color = cmap(_class)
        color = cmap[bin -1]
        i['properties']['class'] = str(bin -1)
        # i['properties']['color'] = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), color[3]
        i['properties']['color'] = color + (1.0,)
        i['properties']['color'] = [str(c) for c in i['properties']['color']]
        i['properties']['value'] = str(round(value, 2))
