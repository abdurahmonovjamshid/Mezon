from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Foydalanuvchilar'

    def ready(self):
        # Admin panel to'liq o'zbekcha ko'rinishi uchun (Django'ning o'z
        # tarjimasida bu nomlar yo'q). Migratsiya talab qilmaydi.
        from django.conf import settings
        from django.contrib import admin
        from django.contrib.auth.models import Group, User

        User._meta.verbose_name = 'Foydalanuvchi'
        User._meta.verbose_name_plural = 'Foydalanuvchilar'
        Group._meta.verbose_name = 'Rol'
        Group._meta.verbose_name_plural = 'Rollar'

        admin.site.site_header = settings.APP_NAME
        admin.site.site_title = f'{settings.APP_NAME} admin'
        admin.site.index_title = 'Boshqaruv paneli'
