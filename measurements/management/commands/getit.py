from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.getit import GetitAPI, SOS_PARAMS
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie


class Command(BaseCommand):
    help = "Command to import GETIT-VESK sea level data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='cnr')
        for s in ps.station_set.filter(status='active'):
            apiclient = GetitAPI()
            df = apiclient.get_df(s.code, 24)
            if df is None:
                continue
            for k, v in SOS_PARAMS.items():
                print(df.head())
                if v in df.columns:
                    serie = get_serie(s, v)
                    print(df[v])
                    load_serie(df[v].copy(), serie.id)
