from random import randint, choice, uniform
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view,permission_classes
import json
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import permissions
from adventure.models import Player, Room
from .roomGenerator import generateRoomDescription
from .serializer import RoomSerializer

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@api_view(["GET"])
@csrf_exempt

def initialize(request):
    permission_classes = (IsAuthenticated)
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)

@api_view(["GET"])
@csrf_exempt
def generateWorld(request):
    permission_classes = (IsAuthenticated)
    maxRooms = 100
    # delete all room data
    Room.objects.all().delete()
    # store all rooms
    allRooms = []
    if len(allRooms) < maxRooms:
        # generate x rooms
        for _ in range(0, maxRooms):
            # generate rooms title and description
            (title, description) = generateRoomDescription()
            # create room in database
            newRoom = Room(title=title, description=description)
            newRoom.save()
            # store it
            allRooms.append(newRoom)
    
    # set map square area of 196 squares in map/grid
    mapArea = 14 
    # store map
    worldMap = [] 
    # amount rooms used in map
    roomsInMap = 0 
    # copy rooms to prevent repeated rooms added to map
    roomObjsInMap = [room for room in allRooms]
    
    # this function returns a random room and guarantees an unique room every time
    def getRandomRoom():
        nonlocal roomObjsInMap
        if len(roomObjsInMap) > 0:
            rRoomIndex = choice([n for n in range(0, len(roomObjsInMap))])
            randomRoom = roomObjsInMap[rRoomIndex]
            roomObjsInMap.pop(rRoomIndex)
            return randomRoom
        return 1

    # there are two possibilities: 0 rooms or 1 room in each square of the map grid
    mapSpots = [0, getRandomRoom()]

    # generate map
    while roomsInMap < maxRooms:
        for row in range(0, mapArea):
            # if we've not hit max map size for this row
            if len(worldMap) <= row:
                # add new row
                worldMap.append([])
            for column in range(0, mapArea):
                # check if we've hit max number of rooms
                if roomsInMap == maxRooms: 
                    if len(worldMap[row]) <= column:
                        worldMap[row].append(0)
                else:
                    # choose between 0 or a Room
                    newChoice = choice(mapSpots)
                    # if we've not hit max map size for this column
                    if len(worldMap[row]) <= column:
                        # add new column based on choice
                        worldMap[row].append(newChoice)
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
                            worldMap[row][column] = newChoice

                    # if final choice was a Room, add 1 to rooms in map
                    if newChoice != 0:
                        roomsInMap += 1

    # connect all rooms horizontally/vertically
    totalRows = len(worldMap)
    for row in range(0, totalRows):
        # store previously passed room
        prevRoomLeft = None
        for column in range(0, len(worldMap[row])):
            room = worldMap[row][column]
            # if its actually a room object
            if room != 0 and room != 1:
                if prevRoomLeft:
                    # find room to the west / left
                    # find room to the east / right
                    room.connectRooms(prevRoomLeft, 'w')
                    prevRoomLeft.connectRooms(room, 'e')
                # set this room to be the previous room for the next loops
                prevRoomLeft = room
                
                # if we're on the 2nd row or below
                if row > 0:
                    prevRoomAbove = None
                    # go up and find a room
                    tmpRow = row
                    while tmpRow > 0:
                        # go one row above
                        tmpRow -= 1
                        # on the same column
                        roomAbove = worldMap[tmpRow][column]
                        # check if there is a room there
                        if roomAbove != 0 and roomAbove != 1:
                            # set the new room above
                            prevRoomAbove = roomAbove
                            break
                    
                    # find room to the north / top
                    if prevRoomAbove:
                        room.connectRooms(prevRoomAbove, 'n')
                        prevRoomAbove.connectRooms(room, 's')

    # serialize all rooms before return
    allRooms = RoomSerializer(Room.objects.all(), many=True).data
    
    # serialize all rooms in map
    for row in range(0, totalRows):
        for column in range(0, len(worldMap[row])):
            room = worldMap[row][column]
            if room != 0 and room != 1:
                worldMap[row][column] = RoomSerializer(room).data

    return JsonResponse({ "worldMap": worldMap })

@api_view(["GET"])
@csrf_exempt
def getRooms(request):
    permission_classes = (IsAuthenticated)
    return JsonResponse({ "rooms": RoomSerializer(Room.objects.all(), many=True).data})

@api_view(["POST"])
@csrf_exempt
def move(request):
    permission_classes = (IsAuthenticated)
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


@api_view(["POST"])
@csrf_exempt
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
