from django.contrib import admin

from .models import *


@admin.register(BoardState)
class BoardStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'preview_html_tag']


admin.site.register(StateTransition)

admin.site.register(Comment)

admin.site.register(Tag)
