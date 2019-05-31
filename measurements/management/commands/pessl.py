from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.pessl import PesslAPI
from measurements.models import SourceType
from measurements.utils import get_serie, load_serie

PARAMETER_MAP = {"Precipitation|sum": "Precip", #
                 "Leaf Wetness|time": "LeafWetness", #
                 'HC Air temperature|avg': "At_temp", # http://vocab.nerc.ac.uk/collection/P01/current/CTMPZZ01/
                 "HC Relative humidity|avg": "RelHumidity", #http://vocab.nerc.ac.uk/collection/P01/current/CHUMZZ01/
                 "Dew Point|avg": "DewPoint", # http://vocab.nerc.ac.uk/collection/P01/current/CDEWZZ01/
                 "Wind speed|avg": "WindSpd", # http://vocab.nerc.ac.uk/collection/P01/current/EWSBZZ01/
                 }


class Command(BaseCommand):
    help = "Command to import PESSL data"

    def handle(self, *args, **options):
        ps = SourceType.objects.get(code='pessl')
        for s in ps.station_set.all():
            keys = SOURCE_AUTH['pessl'][s.network.code]
            print(keys)
            pesslapi = PesslAPI(keys['public_key'],
                                keys['private_key'])
            df = pesslapi.get_df(s.code, 100)

            for k, v in PARAMETER_MAP.items():
                if k in df.columns:
                    serie = get_serie(s, k)
                    load_serie(df[k].copy(), serie.id)



    def __handle(self, *args, **options):
        # client = InfluxMeteo()
        # datanow = utcnow()
        lastvalues = []
        parameters = []
        for centralina in Centralina.objects.using('meteo').filter(status='attiva', tipo_centralina='pessl'):
            _centralina = centralina.id
            # _mz = centralina.macrozona.nome
            _mz = 'tn'
            if centralina.proprietario == 'lavis':
                df = pesslapilavis.get_df(centralina.codice, last=120)
            else:
                df = pesslapi.get_df(centralina.codice, last=120)

            load_data(df, 'Precipitation', 'sum', 'Precip', _centralina, 'Precip')
            load_data(df, 'Leaf Wetness', 'time', 'BagnaturaFogl', _centralina, 'PercBagnaturaFogl')
            load_data(df, 'HC Air temperature', 'avg', 'TempAria', _centralina, 'TempAria')
            load_data(df, 'HC Relative humidity', 'avg', 'UmidAria', _centralina, 'UmidAriaRel')
            load_data(df, 'Dew Point', 'avg', 'PntRugiada', _centralina, 'PntRugiada')
            load_data(df, 'Wind speed', 'avg', 'VelDirVento', _centralina, 'VelVento')

            # client.write('Syncdata', _centralina, 'Syncdata', datanow, 1, extratags={'tc': 'p', 'mz': _mz})
            # lastvalues.append((centralina.codice, centralina.denominazione, df.index.max()))
            # parameters.append((centralina.codice, centralina.denominazione, df.columns.levels[0].sort_values()))

            print()
            df.columns.levels[0].sort_values()
        print()
        pd.DataFrame(lastvalues)
        print()
        pd.DataFrame(parameters)