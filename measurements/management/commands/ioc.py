from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.ioc import IocAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie


class Command(BaseCommand):
    help = "Command to import IOC sea level data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='ioc')
        for s in ps.station_set.filter(status='active'):
            apiclient = IocAPI()
            df = apiclient.get_df(s.code)

            if df is not None:
                serie = get_serie(s, 'SLEV')
                load_serie(df['SLEV'].copy(), serie.id)
