from django.contrib import admin

from .models import Parameter, Sensor, Location, Serie, Measure, Network, SourceType, Station


class ParameterAdmin(admin.ModelAdmin):
    pass


class SensorAdmin(admin.ModelAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    pass


class NetworkAdmin(admin.ModelAdmin):
    pass


class SerieAdmin(admin.ModelAdmin):
    list_display = ('station', 'sensor', 'parameter', 'height')
    list_filter = ('station', 'sensor', 'parameter')


class StationAdmin(admin.ModelAdmin):
    pass


class SourceTypeAdmin(admin.ModelAdmin):
    pass


class MeasureAdmin(admin.ModelAdmin):
    list_display = ('serie', 'timestamp', 'value')


admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Serie, SerieAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Measure, MeasureAdmin)
