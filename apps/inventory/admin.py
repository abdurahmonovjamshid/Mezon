from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    InventoryCount, InventoryCountItem, StockMovement, StockTransfer, StockTransferItem, Warehouse,
)


@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name', 'is_default', 'active')
    list_editable = ('is_default', 'active')


class StockTransferItemInline(TabularInline):
    model = StockTransferItem
    extra = 0


@admin.register(StockTransfer)
class StockTransferAdmin(ModelAdmin):
    list_display = ('pk', 'date', 'from_warehouse', 'to_warehouse', 'status', 'created_by')
    list_filter = ('status', 'date')
    inlines = [StockTransferItemInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    list_display = ('product', 'warehouse', 'direction', 'quantity', 'pieces', 'movement_type', 'unit_cost', 'date', 'reference')
    list_filter = ('warehouse', 'direction', 'movement_type', 'date')
    search_fields = ('product__name', 'product__code', 'reference')
    autocomplete_fields = ('product', 'created_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    ordering = ('-date', '-id')


class InventoryCountItemInline(TabularInline):
    model = InventoryCountItem
    extra = 0
    readonly_fields = ('system_kg', 'system_pieces', 'diff_kg', 'diff_pieces')


@admin.register(InventoryCount)
class InventoryCountAdmin(ModelAdmin):
    list_display = ('pk', 'date', 'status', 'created_by')
    list_filter = ('status', 'date')
    inlines = [InventoryCountItemInline]
    readonly_fields = ('created_at', 'updated_at')
