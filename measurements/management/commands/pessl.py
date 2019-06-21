from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.pessl import PesslAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie

PARAMETER_MAP = {"Precipitation|sum": "Precipitation", #
                 "Leaf Wetness|time": "LeafWet", #
                 'HC Air temperature|avg': "AtTemp", # http://vocab.nerc.ac.uk/collection/P01/current/CTMPZZ01/
                 "HC Relative humidity|avg": "RelHumidity", #http://vocab.nerc.ac.uk/collection/P01/current/CHUMZZ01/
                 "Dew Point|avg": "DewPoint", # http://vocab.nerc.ac.uk/collection/P01/current/CDEWZZ01/
                 "Wind speed|avg": "WindSpeed", # http://vocab.nerc.ac.uk/collection/P01/current/EWSBZZ01/
                 }


class Command(BaseCommand):
    help = "Command to import PESSL data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='pessl')
        for s in ps.station_set.filter(status='active'):
            keys = SOURCE_AUTH['pessl'][s.network.code]
            print(keys)
            pesslapi = PesslAPI(keys['public_key'],
                                keys['private_key'])
            df = pesslapi.get_df(s.code, 100)

            for k, v in PARAMETER_MAP.items():
                if k in df.columns:
                    serie = get_serie(s, v)
                    load_serie(df[k].copy(), serie.id)
