from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.arso import ArsoAPI, ARSO_PARAMS
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie


class Command(BaseCommand):
    help = "Command to import IOC sea level data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='arso')
        for s in ps.station_set.filter(status='active'):
            apiclient = ArsoAPI()
            df = apiclient.get_df(s.code)
            if df is None:
                continue
            for k, v in ARSO_PARAMS.items():
                if v in df.columns:
                    serie = get_serie(s, v)
                    load_serie(df[v].copy(), serie.id)
