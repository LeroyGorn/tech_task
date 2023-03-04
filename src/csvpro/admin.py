from django.contrib import admin

from csvpro.models import DataColumn, DataSchema

admin.site.register(DataSchema)
admin.site.register(DataColumn)
