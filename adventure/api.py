import json
from decouple import config
from django.http import JsonResponse
from django.contrib.auth.models import User
from adventure.models import Player, Room
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import permissions
from random import randint, choice
# from pusher import Pusher
from .models import *
from .roomGenerator import generateRoomDescription
from .serializer import RoomSerializer

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'room': RoomSerializer(room).data, 'players': players }, safe=True)

mapSize = 15 # needs to be adjusted based on max rooms
maxRooms = 100

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def generateWorld(request):
    # delete all room data
    Room.objects.all().delete()
    # store all rooms
    gameMap = []
    # gameMapLog = []
    roomsAddedToMap = 0

    for y in range(0, mapSize):
        # store previously passed room
        prevRoomLeft = None
        prevRoomLeftX = None
        if len(gameMap) <= y:
            gameMap.append([])
            # gameMapLog.append([])
        for x in range(0, mapSize):
            if roomsAddedToMap >= maxRooms:
                gameMap[y].append(0)
                # gameMapLog[y].append('____')
            else:
                newRoom = None
                isRoom = randint(0, 1)

                if isRoom == 1:
                    roomsAddedToMap += 1
                    newRoom = addRoom(x, y)
                    # generate horizontal connections
                    if prevRoomLeft is not None:
                        # find room to the west / left
                        newRoom.connectRooms(prevRoomLeft, 'w')
                        # find room to the east / right
                        prevRoomLeft.connectRooms(newRoom, 'e')
                        # update game map with new connection
                        gameMap[y][prevRoomLeftX] = prevRoomLeft
                    # set this room to be the previous room for the next loops
                    prevRoomLeft = newRoom
                    prevRoomLeftX = x
                    
                    
                    # after the first row is done
                    # generate vertical connections
                    if y > 0:
                        # hold on to the room above
                        prevRoomAbove = None
                        prevRoomAboveY = None
                        tmpY = y
                        # keep going up until we find a room
                        while tmpY > 0 and prevRoomAbove is None:
                            # go one row above
                            tmpY -= 1
                            # on the same column, check if there is a room there
                            if gameMap[tmpY][x] is not 0:
                                # update the new room above
                                prevRoomAbove = gameMap[tmpY][x]
                                prevRoomAboveY = tmpY
                        
                        # if we've found a possible connection
                        if prevRoomAbove is not None:
                            # find room to the north / up
                            newRoom.connectRooms(prevRoomAbove, 'n')
                            # find room to the south / down
                            prevRoomAbove.connectRooms(newRoom, 's')
                            # update game map with new connection
                            gameMap[prevRoomAboveY][x] = prevRoomAbove

                    # update isRoom from 1 to the new room object 
                    isRoom = newRoom

                # update the game map
                gameMap[y].append(isRoom)
                # if isRoom == 0:
                #     gameMapLog[y].append('____')
                # else:
                #     gameMapLog[y].append(isRoom.id)

    # serialize all rooms before return
    for y in range(0, mapSize):
        for x in range(0, mapSize):
            if gameMap[y][x] is not 0:
                gameMap[y][x] = RoomSerializer(gameMap[y][x]).data

    output = { "gameMap": gameMap, "mapSize": mapSize } # "gameMapLog": gameMapLog 
    return JsonResponse(output)

def addRoom(x, y):
    # generate random title and description
    (title, description) = generateRoomDescription()
    # create room in database
    newRoom = Room(title=title, description=description, x=x, y=y)
    # store it
    newRoom.save()
    # return it
    return newRoom

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def getRooms(request):
    return JsonResponse({ "rooms": RoomSerializer(Room.objects.all(), many=True).data, "mapSize": mapSize })

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def move(request):
    dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
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
        player.currentRoom = nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({
          'name': player.user.username,
          'room': RoomSerializer(nextRoom).data,
          'players': players,
          'error_msg': ""
        }, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({
          'name':player.user.username,
          'room': RoomSerializer(room).data,
          'players': players,
          'error_msg': "You cannot move that way."
        }, safe=True)


@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
