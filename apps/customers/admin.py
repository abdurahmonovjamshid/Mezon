from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ('name', 'phone', 'credit_limit', 'opening_balance', 'is_supplier', 'active', 'created_at')
    list_filter = ('active', 'is_supplier')
    search_fields = ('name', 'phone', 'address')
    autocomplete_fields = ('linked_supplier',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
