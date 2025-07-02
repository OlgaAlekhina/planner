from django.contrib import admin
from .models import UserProfile, Group, GroupUser, SignupCode


admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(SignupCode)
