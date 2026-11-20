from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ('name', 'phone', 'opening_balance', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
