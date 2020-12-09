from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'pub_date', 'author',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created',)
    search_fields = ('text',)
    list_filter = ('created',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
