from django.contrib import admin
from .models import User_info, ChatMessages, Chat
from rest_framework.authtoken.admin import TokenAdmin
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import Chat, ChatMessages

TokenAdmin.raw_id_fields = ['user']
admin.site.register(User_info)
class ChatAdmin(admin.ModelAdmin):
    list_filter = ['id', 'chat_name']
    search_field = ['id', 'chat_name']
    list_display = ['id']

    class Meta:
        model = Chat

class Caching(Paginator):
    def _get_count(self):
        if not hasattr(self, "_count"):
            self._count = None
        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list_query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)
            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)

class ChatMessagesAdmin(admin.ModelAdmin):
    list_filter = ['room', 'participant', 'timestamp']
    list_display = ['room', 'participant', 'timestamp', 'messages']
    search_fields = ['room__name', 'participant__username', 'timestamp', 'messages']
    readonly_fields = ['room', 'participant', 'timestamp', 'id']

    show_full_result_count = False
    paginator = Caching

    class Meta:
        model = ChatMessages

admin.site.register(Chat, ChatAdmin)

admin.site.register(ChatMessages, ChatMessagesAdmin)
