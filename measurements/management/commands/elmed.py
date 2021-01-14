from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.elmed import ElmedAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie

PARAMETER_MAP = {"temp2m": "AtTemp",
                 # "nasstemp": "At_temp_WetBulb",
                 "relfeuchte": "RelHumidity",
                 "windgeschw": "WindSpeed",
                 "blattnass": "LeafWet",
                 "niederschlag": "Precipitation",
                 "bodentemp25cm": ("SoilTemp", -25),
                 "BF10": ("SoilMoisture", -10),
                 "BF30": ("SoilMoisture", -30),
                 "BF50": ("SoilMoisture", -50),
                 "BF80": ("SoilMoisture", -80),
                 }

class Command(BaseCommand):
    help = "Command for importing ELMED data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24
        )

    def handle(self, *args, **options):
        hours = options['hours']
        ps = SourceType.objects.get(code='elmed')
        for s in ps.station_set.filter(status='active'):
            self.stdout.write("Loading station {} ... ".format(s), ending='')
            keys = SOURCE_AUTH['elmed'][s.network.code]
            elmedapi = ElmedAPI(None,
                                keys['private_key'])
            df = elmedapi.get_df(s.code, hours)
            if df is not None and df.shape[0] > 0:
                for k, _v in PARAMETER_MAP.items():
                    if not isinstance(_v, str):
                        v, height = _v
                    else:
                        v = _v
                        height = None
                    if k in df.columns:
                        serie = get_serie(s, v, height=height)
                        load_serie(df[k].copy(), serie.id)
                self.stdout.write("[OK]")
            else:
                self.stdout.write("[FAILED]")
