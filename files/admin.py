from django.contrib import admin
from .models import *


class ShareTimeAdmin(admin.TabularInline):
    model = ShareTime


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    inlines = [ShareTimeAdmin]


class ChatTimeAdmin(admin.TabularInline):
    model = ChatTime

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    inlines = [ChatTimeAdmin]


admin.site.register(File)
admin.site.register(Comment)

admin.site.site_title = "File Share Api"
admin.site.site_header = "File Share Api"
