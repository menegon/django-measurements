from django.urls import path, include
from .writeapi import  write, write_csv
from .views import locations_flatjson, measure_geojson

urlpatterns = [
    path('write', write),
    path('writecsv', write_csv),
    path('locations/flatjson', locations_flatjson),
    path('measures/geojson', measure_geojson),
]