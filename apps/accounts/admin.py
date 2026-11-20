from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.accounts.roles import ROLE_DESCRIPTIONS, user_roles

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'full_name', 'roles', 'is_active', 'is_superuser', 'last_login')
    list_filter = ('is_active', 'is_superuser', 'groups')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'groups' in form.base_fields:
            form.base_fields['groups'].label = 'Rollar'
            form.base_fields['groups'].help_text = ' · '.join(
                f'{name}: {desc}' for name, desc in ROLE_DESCRIPTIONS.items()
            ) + ". Rol tanlanmasa — hamma bo'lim ochiq."
        return form

    @display(description='Ism')
    def full_name(self, obj):
        return obj.get_full_name() or '—'

    @display(description='Rollar')
    def roles(self, obj):
        if obj.is_superuser:
            return 'Superuser'
        return ', '.join(user_roles(obj)) or "Hammasi ochiq"


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    list_display = ('name', 'description')

    @display(description="Ruxsat etilgan bo'limlar")
    def description(self, obj):
        return ROLE_DESCRIPTIONS.get(obj.name, '—')
