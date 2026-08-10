from django.contrib import admin

from .models import Message, WhatsAppGroup

admin.site.register(Message)
admin.site.register(WhatsAppGroup)
