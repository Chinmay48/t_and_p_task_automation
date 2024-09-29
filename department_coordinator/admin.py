from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import DepartmentCoordinator
from .resources import DepartmentCoordinatorResource
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import (
    ExportForm,
    ImportForm,
)
# Register your models here.

@register(DepartmentCoordinator)
class StudentAdmin(ImportExportModelAdmin, ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = [
        "officer_id",
        "get_coordinator_name",
        "get_coordinator_email",
        "department",
    ]
    def get_coordinator_name(self, obj):
        return obj.user.full_name if obj.user else ''
    def get_coordinator_email(self, obj):
        return obj.user.email if obj.user else ''
    get_coordinator_name.short_description = 'Name'
    get_coordinator_email.short_description = 'Email'
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "user",
                    "officer_id",
                    "department",
                ),
            },
        ),
    )
    resource_class = DepartmentCoordinatorResource
