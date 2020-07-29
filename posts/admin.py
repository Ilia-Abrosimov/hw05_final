from django.contrib import admin
from .models import Post, Comment, Group


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("description",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text")
    search_fields = ("text",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
