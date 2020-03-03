from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'n_to', 's_to', 'e_to', 'w_to']