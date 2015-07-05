from django.contrib import admin
from .models import *

selected_models = [
    Spot,
    OwnershipDeed,
    OwnershipReceipt,
    Owner,
    ConstructionAuthorization,
    ConstructionCompany,
    Construction,
    Operation,
    MaintenanceLevel,
    ContributionReceipt,
    YearlyPayment,
]

for model in selected_models:
    admin.site.register(model)

