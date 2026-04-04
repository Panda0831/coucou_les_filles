from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ChatMessage
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('message', 'response')
    ordering = ('-created_at',)

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