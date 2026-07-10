from django.contrib import admin

from apps.fleet.models import Carrier, FleetMembership, TankerCompartment, Vehicle, VehicleDocument

# Register your models here.
admin.site.register(Carrier)
admin.site.register(Vehicle)
admin.site.register(TankerCompartment)
admin.site.register(FleetMembership)
admin.site.register(VehicleDocument)