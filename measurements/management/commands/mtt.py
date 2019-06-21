from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.mtt import MttAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie


PARAMETER_MAP = {"temperatura": "AtTemp",
                 "pioggia": "Precipitation",
                 # "d": "WindDirFrom",
                 "v": "WindSpeed",
                 "rh": "RelHumidity",
                 "rsg": "GlobalRad"
                 }


class Command(BaseCommand):
    help = "Command to import Meteotrentino data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='mtt')
        for s in ps.station_set.filter(status='active'):
            apiclient = MttAPI()
            df = apiclient.get_df(s.code)

            for k, v in PARAMETER_MAP.items():
                if k in df.columns:
                    serie = get_serie(s, v)
                    load_serie(df[k].copy(), serie.id)
