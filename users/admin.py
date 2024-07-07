from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Organisation


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['userId', 'firstName', 'lastName', 'email', 'phone', 'password']
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("firstName", "lastName", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields":("firstName", "lastName", "phone")}),)

class OrganisationAdmin(admin.ModelAdmin):
    model = Organisation
    list_display = ['orgId', 'name', 'description', 'get_users']
    search_fields = ['orgId', 'name', 'description']
    readonly_fields = ['orgId']
    
    def get_users(self, obj):
        return ", ".join([user.email for user in obj.users.all()])
    get_users.short_description = 'Users'



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organisation, OrganisationAdmin)