from apps.fleet.models_new import Vehicle
import django_filters


#============================
# VEHICLES
#============================

class VehicleFilter(django_filters.FilterSet):
    class Meta:
        model = Vehicle
        fields = {
            "id": ["exact","in"], #?id=ecdo-4856-rts ou id__in=edsc-4589-edolu
            "carrier": ["exact"],#?id=ecdo-4856-rts ou id__in=edsc-4589-edolu
            "display_registration" : ["exact","icontains"]    #?display_registration__icontains=ecdo-4856-rtsj-4873 
            #En cas de plusieurs filtres    #?id=ecdo-4856-rts&carrier=edsc-4589-edolu    
          
        }