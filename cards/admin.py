from django.contrib import admin
from .models import Stock, StockCard, Tag, SavedFilter, PriceSnapshot


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'company_name', 'exchange', 'created_at']
    search_fields = ['ticker', 'company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['user']
    search_fields = ['name', 'user__username']


@admin.register(StockCard)
class StockCardAdmin(admin.ModelAdmin):
    list_display = ['stock', 'user', 'priority', 'target_price', 'is_archived', 'updated_at']
    list_filter = ['priority', 'is_archived', 'user']
    search_fields = ['stock__ticker', 'stock__company_name', 'user__username', 'notes']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Stock Information', {
            'fields': ('user', 'stock')
        }),
        ('Card Details', {
            'fields': ('notes', 'priority', 'target_price', 'tags', 'is_archived')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ['stock_card', 'price', 'volume', 'source', 'timestamp']
    list_filter = ['source', 'timestamp']
    search_fields = ['stock_card__stock__ticker']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'priority', 'sort_by', 'is_default', 'created_at']
    list_filter = ['priority', 'is_default', 'user']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['tags']

