from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from tendering.models import Category, Comment, User

admin.site.unregister(Group)
admin.site.register(Comment)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    list_filter = [
        "name",
    ]
    search_fields = [
        "name",
    ]


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("phone_number", "location")
    list_filter = UserAdmin.list_filter
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("phone_number", "location")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": ("first_name", "last_name", "phone_number", "location")},
        ),
    )
