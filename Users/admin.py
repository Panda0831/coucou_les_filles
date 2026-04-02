from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'is_admin_user', 'is_customer', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Pro', {'fields': ('is_admin_user', 'is_customer', 'photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Pro', {'fields': ('is_admin_user', 'is_customer', 'photo')}),
    )

admin.site.register(User, CustomUserAdmin)