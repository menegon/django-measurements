import pandas as pd

from psqlextra.query import ConflictAction
from measurements.models import Measure, Station, Parameter, Sensor, Serie


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


    df.reset_index(inplace=True)
    df.columns = ['timestamp', 'value']
    df['serie_id'] = serie_id

    datadict = df.to_dict(orient='record')
    Measure.extra.on_conflict(df.columns.to_list(),
                              ConflictAction.UPDATE).bulk_insert(datadict)
    return


def strong_float(value):
    if value in [None, '']:
        return None
    else:
        return float(value)