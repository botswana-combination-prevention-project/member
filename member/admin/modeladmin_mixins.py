from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminReadOnlyMixin,
    ModelAdminAuditFieldsMixin, ModelAdminInstitutionMixin)

from edc_base.fieldsets import (
    FieldsetsModelAdminMixin as BaseFieldsetsModelAdminMixin)

from household.models import HouseholdStructure
from survey import S
from survey.admin import survey_schedule_fields

from ..models import HouseholdMember
from survey.site_surveys import site_surveys


class HouseholdMemberAdminMixin:

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_structure":
            if request.GET.get('household_structure'):
                kwargs["queryset"] = HouseholdStructure.objects.filter(
                    id__exact=request.GET.get('household_structure', 0))
            else:
                kwargs["queryset"] = HouseholdStructure.objects.none()
        if db_field.name == "household_member":
            if request.GET.get('household_member'):
                kwargs["queryset"] = HouseholdMember.objects.filter(
                    id__exact=request.GET.get('household_member', 0))
            else:
                kwargs["queryset"] = HouseholdMember.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        try:
            household_identifier = (
                obj.household_member.household_structure.household.household_identifier)
        except AttributeError:
            household_identifier = obj.household_structure.household.household_identifier
        try:
            survey_schedule = obj.household_member.household_structure.survey_schedule
        except AttributeError:
            survey_schedule = obj.household_structure.survey_schedule
        try:
            return reverse(
                'enumeration:dashboard_url', kwargs=dict(
                    household_identifier=household_identifier,
                    survey_schedule=survey_schedule))
        except NoReverseMatch:
            return super().view_on_site(obj)


class ModelAdminMixin(ModelAdminInstitutionMixin, ModelAdminFormInstructionsMixin,
                      ModelAdminNextUrlRedirectMixin, ModelAdminFormAutoNumberMixin,
                      ModelAdminRevisionMixin, ModelAdminAuditFieldsMixin,
                      ModelAdminReadOnlyMixin, HouseholdMemberAdminMixin,
                      admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + survey_schedule_fields)


class FieldsetsModelAdminMixin(BaseFieldsetsModelAdminMixin):

    def get_instance(self, request):
        return None

    def get_key(self, request, obj=None):
        """Returns the name of the household members previous
        survey schedule or None.

        If key has value, the fieldset will be added to
        modeladmin.fieldsets.
        """
        key = None
        household_member = None
        if request.GET.get('household_member'):
            try:
                household_member = HouseholdMember.objects.get(
                    pk=request.GET.get('household_member'))
            except HouseholdMember.DoesNotExist:
                pass
        else:
            household_member = obj
        if hasattr(household_member, 'previous'):
            previous = household_member.previous
            if previous:
                survey_schedule_object = site_surveys.get_survey_schedule_from_field_value(
                    request.GET.get('survey_schedule'))
                key = survey_schedule_object.name
        return key
