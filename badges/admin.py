from django.contrib import admin

from badges.models import Badge, BadgeToLaureate

class BadgeAdmin(admin.ModelAdmin):
    fields = ('icon',)
    list_display = ('id','level')

admin.site.register(Badge, BadgeAdmin)
admin.site.register(BadgeToLaureate)
