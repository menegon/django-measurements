from django.http.response import JsonResponse
from measurements.models import Location


def locations_flatjson(request):
    return JsonResponse(Location.objects.get_flatjson(), safe=False)