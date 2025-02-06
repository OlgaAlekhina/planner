from django.contrib import admin
from .models import UserProfile, Group, GroupUser

admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(GroupUser)
