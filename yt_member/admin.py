from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'password')  # admin table me kaunse column dikhane hain
