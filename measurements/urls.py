from django.urls import path, include
from .writeapi import  write
from .views import locations_flatjson

urlpatterns = [
    path('write', write),
    path('locations/flatjson', locations_flatjson)
]