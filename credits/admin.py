from django.contrib import admin
from .models import Agreement, Portfolio, Creditor

# ваш класс PortfolioInline и AgreementAdmin
class PortfolioInline(admin.TabularInline):
    model = Portfolio
    extra = 1


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = [
        "id", "agreement_code", "agreement_date", "agreement_type",
        "creditor", "creditor_first", "total_sum", "total_amount",
        "date_add", "date_update",
    ]
    ordering = ["id"]
    inlines = [PortfolioInline]

admin.site.register(Portfolio) 

@admin.register(Creditor)
class CreditorAdmin(admin.ModelAdmin):
    list_display = [
        "id", 
        "type", "name",
        "date_add", "date_update",
    ]
    ordering = ["id"]
 
