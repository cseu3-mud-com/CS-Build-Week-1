from random import randint, choice, uniform
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json

from adventure.models import Player, Room
from .roomGenerator import generateRoomDescription
from .serializer import RoomSerializer

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
# TODO: AUTHENTICATION
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


@csrf_exempt
@api_view(["GET"])
def generateWorld(request):
    maxRooms = 100
    allRooms = [RoomSerializer(room).data for room in Room.objects.all()]
    if len(allRooms) < maxRooms:
        Room.objects.all().delete()
        for _ in range(0, maxRooms):
            newRoomInfo = generateRoomDescription()
            newRoom = Room(title=newRoomInfo[0], description=newRoomInfo[1])
            newRoom.save()
            allRooms.append(RoomSerializer(newRoom).data)
    
    """
     0,0 |  0,1 |  0,2 |  0,3 |  0,4 |  0,5 |  0,6 |  0,7 |  0,8 |  0,9 |  0,10 |  0,11 |  0,12 | 0,13
     1,0 |  1,1 |  1,2 |  1,3 |  1,4 |  1,5 |  1,6 |  1,7 |  1,8 |  1,9 |  1,10 |  1,11 |  1,12 | 1,13
     2,0 |  2,1 |  2,2 |  2,3 |  2,4 |  2,5 |  2,6 |  2,7 |  2,8 |  2,9 |  2,10 |  2,11 |  2,12 | 2,13
     3,0 |  3,1 |  3,2 |  3,3 |  3,4 |  3,5 |  3,6 |  3,7 |  3,8 |  3,9 |  3,10 |  3,11 |  3,12 | 3,13
     4,0 |  4,1 |  4,2 |  4,3 |  4,4 |  4,5 |  4,6 |  4,7 |  4,8 |  4,9 |  4,10 |  4,11 |  4,12 | 4,13
     5,0 |  5,1 |  5,2 |  5,3 |  5,4 |  5,5 |  5,6 |  5,7 |  5,8 |  5,9 |  5,10 |  5,11 |  5,12 | 5,13
     6,0 |  6,1 |  6,2 |  6,3 |  6,4 |  6,5 |  6,6 |  6,7 |  6,8 |  6,9 |  6,10 |  6,11 |  6,12 | 6,13
     7,0 |  7,1 |  7,2 |  7,3 |  7,4 |  7,5 |  7,6 |  7,7 |  7,8 |  7,9 |  7,10 |  7,11 |  7,12 | 7,13
     8,0 |  8,1 |  8,2 |  8,3 |  8,4 |  8,5 |  8,6 |  8,7 |  8,8 |  8,9 |  8,10 |  8,11 |  8,12 | 8,13
     9,0 |  9,1 |  9,2 |  9,3 |  9,4 |  9,5 |  9,6 |  9,7 |  9,8 |  9,9 |  9,10 |  9,11 |  9,12 | 9,13
    10,0 | 10,1 | 10,2 | 10,3 | 10,4 | 10,5 | 10,6 | 10,7 | 10,8 | 10,9 | 10,10 | 10,11 | 10,12 | 10,13
    11,0 | 11,1 | 11,2 | 11,3 | 11,4 | 11,5 | 11,6 | 11,7 | 11,8 | 11,9 | 11,10 | 11,11 | 11,12 | 11,13
    12,0 | 12,1 | 12,2 | 12,3 | 12,4 | 12,5 | 12,6 | 12,7 | 12,8 | 12,9 | 12,10 | 12,11 | 12,12 | 12,13
    13,0 | 13,1 | 13,2 | 13,3 | 13,4 | 13,5 | 13,6 | 13,7 | 13,8 | 13,9 | 13,10 | 13,11 | 13,12 | 13,13
    
    """
    mapArea = 13
    mapSize = []
    mapSpots = [0, 1]
    totalRooms = len(allRooms)
    roomsInMap = 0
    while roomsInMap < maxRooms:
        for row in range(0, mapArea): # 196
            if len(mapSize) <= row:
                mapSize.append([])
            for column in range(0, mapArea):
                newChoice = choice(mapSpots)
                if roomsInMap == maxRooms: 
                    newChoice = 0
                if len(mapSize[row]) <= column:
                    mapSize[row].append(newChoice)
                else:
                    if roomsInMap < maxRooms:
                        mapSize[row][column] = 1

                roomsInMap += newChoice




    """
    totalRooms -= 1
    allRooms[:totalRooms]
    """

    return JsonResponse({ "mapSize": mapSize, "rooms": allRooms })

# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
