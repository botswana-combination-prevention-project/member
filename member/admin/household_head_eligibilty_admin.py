from django.contrib import admin

from ..admin_site import member_admin
from ..constants import HEAD_OF_HOUSEHOLD
from ..forms import HouseholdHeadEligibilityForm
from ..models import HouseholdHeadEligibility, HouseholdMember

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdHeadEligibility, site=member_admin)
class HouseholdHeadEligibilityAdmin(ModelAdminMixin, admin.ModelAdmin):

    instructions = ['Important: The household member must verbally consent before completing this questionnaire.']

    form = HouseholdHeadEligibilityForm
    fields = (
        "household_member",
        "report_datetime",
        "aged_over_18",
        'household_residency',
        "verbal_script")

    radio_fields = {
        "aged_over_18": admin.VERTICAL,
        "household_residency": admin.VERTICAL,
        "verbal_script": admin.VERTICAL}

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey',
        'household_member__household_structure__household__plot__map_area')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "household_member":
            if request.GET.get('household_member'):
                kwargs["queryset"] = HouseholdMember.objects.filter(
                    relation=HEAD_OF_HOUSEHOLD,
                    id__exact=request.GET.get('household_member', 0))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
