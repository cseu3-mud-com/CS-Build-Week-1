from django.contrib import admin
from .models import Player, Room, Character

# Register your models here.
admin.site.register(Room)
admin.site.register(Player)
admin.site.register(Character)