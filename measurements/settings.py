import os

from django.conf import settings

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_SOURCE_AUTH = (
)

SOURCE_AUTH = getattr(settings, 'MEASUREMENTS_SOURCE_AUTH', DEFAULT_SOURCE_AUTH)
