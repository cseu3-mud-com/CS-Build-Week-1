from django.conf.urls import url
from . import api

urlpatterns = [
    url('genMap', api.generateWorld),
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('rooms', api.getRooms),
]