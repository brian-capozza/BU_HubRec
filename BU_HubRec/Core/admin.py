from django.contrib import admin
from Core.models import Course, Hub, ClassData

# Register your models here.

class HubAdmin(admin.ModelAdmin):
    list_display = ("unit_name",)

class ClassDataAdmin(admin.ModelAdmin):
    list_display = ("college", "subject", "catalog_number")

class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "get_classdata", "get_hubs")
    search_fields = ("name", "class_data__subject", "class_data__catalog_number")

    # Show M2M nicely
    filter_horizontal = ("hubs",)

    def get_classdata(self, obj):
        return f"{obj.class_data.college} {obj.class_data.subject} {obj.class_data.catalog_number}"
    get_classdata.short_description = "Class Data"

    def get_hubs(self, obj):
        return ", ".join(h.unit_name for h in obj.hubs.all())
    get_hubs.short_description = "Hubs"


admin.site.register(Course, CourseAdmin)
admin.site.register(ClassData, ClassDataAdmin)
admin.site.register(Hub, HubAdmin)