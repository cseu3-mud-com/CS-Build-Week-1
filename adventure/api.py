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
    
    
    mapArea = 14 # 196 max grid
    mapSize = []
    roomsInMap = 0
    roomObjsInMap = [room for room in allRooms]
    
    def getRandomRoom():
        nonlocal roomObjsInMap
        if len(roomObjsInMap) > 0:
            rRoomIndex = choice([n for n in range(0, len(roomObjsInMap))])
            randomRoom = roomObjsInMap[rRoomIndex]
            roomObjsInMap.pop(rRoomIndex)
            print(f'random room chosen: {rRoomIndex} {randomRoom in roomObjsInMap}')
            return randomRoom
        return 1

    mapSpots = [0, getRandomRoom()]

    while roomsInMap < maxRooms:
        for row in range(0, mapArea):
            # if we've not hit max map size for this row
            if len(mapSize) <= row:
                # add new row
                mapSize.append([])
            for column in range(0, mapArea):
                # check if we've hit max number of rooms
                if roomsInMap == maxRooms: 
                    if len(mapSize[row]) <= column:
                        mapSize[row].append(0)
                else:
                    # choose between 0 or a Room
                    newChoice = choice(mapSpots)
                    # if we've not hit max map size for this column
                    if len(mapSize[row]) <= column:
                        # add new column based on choice
                        mapSize[row].append(newChoice)
                        # if the choice was a Room
                        if newChoice != 0:
                            # get new Room to choose from 
                            mapSpots = [0, getRandomRoom()]
                    # we've already hit max map size for this column
                    else:
                        # so if the rooms in map are less than max rooms
                        if roomsInMap < maxRooms:
                            # add new room
                            newChoice = getRandomRoom()
                            mapSize[row][column] = newChoice

                    # if final choice was a Room, add 1 to rooms in map
                    if newChoice != 0:
                        roomsInMap += 1

    """
    totalRooms -= 1
    allRooms[:totalRooms]
    """

    return JsonResponse({ "mapSize": mapSize }) # , "rooms": allRooms

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
