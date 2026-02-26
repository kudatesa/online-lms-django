from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type']
    
    def get_user_type(self, obj):
        return obj.profile.user_type
    get_user_type.short_description = 'User Type'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)