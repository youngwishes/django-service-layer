from django.contrib import admin

from apps.customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["pk", "balance"]
    list_select_related = ["user"]
