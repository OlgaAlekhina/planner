from django.contrib import admin
from .models import UserProfile, Group, GroupUser, SignupCode


admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(SignupCode)


@admin.register(GroupUser)
class GroupUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'group__id', 'user_name', 'user_role']
    search_fields = ['user__username']
