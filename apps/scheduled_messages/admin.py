from django.contrib import admin

from .models import ScheduledMessage, ScheduledMessageAttachment, ScheduledMessageRecipient

admin.site.register(ScheduledMessage)
admin.site.register(ScheduledMessageRecipient)
admin.site.register(ScheduledMessageAttachment)
