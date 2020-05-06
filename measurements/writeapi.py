import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Sensor, Station, Parameter, Serie, Measure
from psqlextra.query import ConflictAction
from basicauth.decorators import basic_auth_required
from django.http import HttpResponse
from datetime import datetime
import pytz
import numpy as np
import pandas as pd
import io

from .utils import get_serie

#
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )

TS_NS = 1000000000 # to convert from nanoseconds to seconds
SERIE_FIELDS = set(['station', 'sensor', 'parameter'])
SERIES_CACHE = {}


@csrf_exempt
def write_csv(request):
    data = request.body.decode().strip()
    df = pd.read_csv(io.StringIO(data),
                     index_col=None,
                     sep=',', header=1,
                     dtype={'station': object})
    df['timestamp'] = pd.to_datetime(df.timestamp)
    if df.timestamp.dt.tz is None:
        df.timestamp = df.timestamp.dt.tz_localize('UTC')
    df.sensor = df.sensor.fillna('unknown')
    # create missing series
    _df = df[['parameter', 'sensor', 'station']].drop_duplicates()
    for r in _df.to_dict(orient='record'):
        get_serie(**r)
    sdf = pd.DataFrame(Serie.objects.values('id', 'parameter__code', 'station__code', 'sensor__code'))
    sdf.rename(columns={'id': 'serie_id',
                        'parameter__code': 'parameter',
                        'station__code': 'station',
                        'sensor__code': 'sensor'}, inplace=True)
    dfm = df.merge(sdf,
                   left_on=['parameter', 'station', 'sensor'],
                   right_on=['parameter', 'station', 'sensor'])
    cnames = ['serie_id', 'timestamp', 'value']
    _df = dfm[cnames].copy()
    for chunk in np.array_split(_df, _df.shape[0] // 1000 + 1):
        datadict = chunk.to_dict(orient='record')
        Measure.extra.on_conflict(cnames,
                                  ConflictAction.UPDATE).bulk_insert(datadict)
    return JsonResponse({"success": True})


@csrf_exempt
def write(request):
    # rjson = json.loads(request.body)
    # _write(rjson)
    # return JsonResponse(rjson, safe=False)
    # return HttpResponse(request.body)
    res = write_data(request.body)
    # split res


    return JsonResponse(res)

def write_data(body):
    datadict = []
    for l in body.decode().strip().split("\n"):
        datadict.append(parse_line(l))
    # stats = _write(data)
    Measure.extra.on_conflict(['timestamp', 'value', 'serie_id'],
                              ConflictAction.UPDATE).bulk_insert(datadict)
    stats = {'updated': -1,
             'created': -1}
    return stats

def parse_line(line):
    # TODO: using regexp
    measure, others = line.split(",", 1)
    _o = others.split(" ")
    if len(_o) == 3:
        tags, fields, _timestamp = _o
        _timestamp = datetime.fromtimestamp(int(_timestamp)/TS_NS, pytz.utc)
    elif len(_o) == 2:
        tags, fields = _o
        _timestamp = datetime.utcnow()
    r = {'m': measure,
            'ts': _timestamp,
            't': dict(x.split('=') for x in tags.split(',')),
            'f': dict(x.split('=') for x in fields.split(','))
            }

    # check for valid serie
    keys = set(r['t'].keys())
    if not 'serie' in keys and not SERIE_FIELDS <= keys:
        raise ValueError("Incomplete serie definition")

    tags = r['t']
    fields = r['f']
    _station = tags['station']
    _parameter = tags['parameter']
    _sensor = tags.get('sensor', 'unknown')
    skey = frozenset([_station, _parameter, _sensor])
    if skey in SERIES_CACHE.keys():
        serie = SERIES_CACHE[skey]
    else:
        serie = get_serie(_station, _parameter, _sensor)
        SERIES_CACHE[skey] = serie

    _r = {'timestamp': _timestamp,
          'value': fields.get('value'),
          'serie_id': serie.id
    }



    return _r


def _write(rjson):
    stats = {'updated': 0,
             'created': 0}
    for r in rjson:
        tags = r['t']
        fields = r['f']


        _station = tags['station']
        _parameter = tags['parameter']
        _sensor = tags.get('sensor', 'unknown')

        serie = get_serie(_station, _parameter, _sensor)

        timestamp = r.get('ts')
        value = fields.get('value')
        measure, created = Measure.objects.get_or_create(serie=serie,
                                                         timestamp=timestamp,
                                                         value=value)
        if created:
            stats['created'] += 1
        else:
            stats['updated'] += 1
    return stats
