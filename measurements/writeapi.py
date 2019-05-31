import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Sensor, Station, Parameter, Serie, Measure
from basicauth.decorators import basic_auth_required
from django.http import HttpResponse
from datetime import datetime

from .utils import get_serie

#
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )

TS_NS = 1000000000 # to convert from nanoseconds to seconds
SERIE_FIELDS = set(['station', 'sensor', 'parameter'])

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
    data = []
    for l in body.decode().strip().split("\n"):
        data.append(parse_line(l))
    stats = _write(data)
    return stats

def parse_line(line):
    # TODO: using regexp
    measure, others = line.split(",", 1)
    _o = others.split(" ")
    if len(_o) == 3:
        tags, fields, _timestamp = _o
        _timestamp = datetime.utcfromtimestamp(int(_timestamp)/TS_NS)
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

    return r


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
        print("TS", timestamp)
        value = fields.get('value')
        measure, created = Measure.objects.get_or_create(serie=serie,
                                                         timestamp=timestamp,
                                                         value=value)
        if created:
            stats['created'] += 1
        else:
            stats['updated'] += 1
    return stats