from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.davis import DavisAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie

PARAMETER_MAP = {"TempAria": "At_temp",
                 # "nasstemp": "At_temp_WetBulb",
                 # "UmidAriaRel": "RelHumidity",
                 "PntRugiada": "DewPoint",
                 "PressAtm": "AtPres",
                 "RadSol": "GlobalRad",
                 "VelVento": "WindSpeed",
                 "Precip": "Precipitation"
                 }

class Command(BaseCommand):
    help = "Command to import Davis data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='davis')
        for s in ps.station_set.filter(status='active'):
            davisapi = DavisAPI()
            df = davisapi.get_df(s.code, 5)

            for k, v in PARAMETER_MAP.items():
                if k in df.columns:
                    serie = get_serie(s, v)
                    load_serie(df[k].copy(), serie.id)