from django.contrib import admin
from .models import TravelTip, ItineraryDay, ItineraryImage

class ItineraryImageInline(admin.TabularInline):
    model = ItineraryImage
    extra = 1

class ItineraryDayInline(admin.StackedInline):
    model = ItineraryDay
    extra = 1

class TravelTipAdmin(admin.ModelAdmin):
    inlines = [ItineraryDayInline]
    list_display = ['title', 'tenure']

class ItineraryDayAdmin(admin.ModelAdmin):
    inlines = [ItineraryImageInline]

admin.site.register(TravelTip, TravelTipAdmin)
admin.site.register(ItineraryDay, ItineraryDayAdmin)
admin.site.register(ItineraryImage)