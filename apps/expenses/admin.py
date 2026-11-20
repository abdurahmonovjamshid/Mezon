from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ('category', 'amount', 'payment_type', 'date', 'created_by')
    list_filter = ('category', 'payment_type', 'date')
    search_fields = ('category__name', 'description')
    autocomplete_fields = ('category', 'created_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    ordering = ('-date', '-id')

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
