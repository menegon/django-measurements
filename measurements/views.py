from django.http.response import JsonResponse
from measurements.models import Location
from django.db.models import Sum, Min, Max
from .utils import get_time, classify_fc
from django.apps import apps
from geojson import Feature, FeatureCollection, loads
from .models import Parameter, Serie, Measure, Station


def locations_flatjson(request):
    return JsonResponse(Location.objects.get_flatjson(), safe=False)



def measure_geojson(request):
    metric = request.GET.get('metric', None)
    if metric is None:
        raise Http404("Metric not found")
    return JsonResponse(get_geojsonpg(metric))


def get_geojsonpg(metric):
    par, aggregate, time, cmap = metric.split('.')
    if aggregate == 'sum':
        AggregateMode = Sum
    elif aggregate == 'min':
        AggregateMode = Min
    elif aggregate == 'max':
        AggregateMode = Max

    start_time, end_time = get_time(time)

    parameter = Parameter.objects.get(code=par)

    qs = Measure.objects
    qs = qs.filter(serie__parameter=parameter)
    qs = qs.filter(timestamp__gte=start_time, timestamp__lte=end_time)

    if aggregate == 'last':
        results = qs.order_by('serie__station', '-timestamp').distinct('serie__station').values('serie__station', 'value')
    else:
        results = qs.values('serie__station').annotate(value=AggregateMode(
            'value'))  # .order_by('parameter', 'location', '-datetime').distinct('parameter', 'location')

    items = []

    for r in results:
        s = Station.objects.get(pk=r['serie__station'])
        if s.location is None:
            continue
        geometry = loads(s.location.geo.geojson)
        properties = {'value': r['value'],
                      'location': s.label}
        items.append(Feature(geometry=geometry.copy(), properties=properties))

    fc = FeatureCollection(items)
    classify_fc(fc, cmap=cmap, zeros=True)
    return fc

