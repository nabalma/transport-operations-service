from django.contrib import admin

from apps.fleet.models import Carrier, CorrectiveAction, Defect, DefectReleaseValidation, Downtime, Evidence,Inspection, InspectionContextVersion, InspectionCriterion, InspectionCriterionResult, InspectionSection, Maintenance, NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason, ReturnToService, TankerCompartment, Vehicle, VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason, VehicleDocument, VehicleMembership

# Register your models here.
admin.site.register(Carrier)
admin.site.register(Vehicle)
admin.site.register(TankerCompartment)
admin.site.register(VehicleMembership)
admin.site.register(VehicleDocument)
admin.site.register(InspectionContextVersion)
admin.site.register(InspectionCriterion)
admin.site.register(Inspection)
admin.site.register(InspectionCriterionResult)
admin.site.register(Defect)
admin.site.register(CorrectiveAction)
admin.site.register(DefectReleaseValidation)
admin.site.register(Maintenance)
admin.site.register(Downtime)
admin.site.register(ReturnToService)
admin.site.register(VehicleAvailabilityEvaluation)
admin.site.register(VehicleAvailabilityEvaluationReason)
admin.site.register(NextTripEligibilityEvaluation)
admin.site.register(NextTripEligibilityEvaluationReason)
admin.site.register(Evidence)