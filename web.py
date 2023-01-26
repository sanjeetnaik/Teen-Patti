from aiohttp import web
import socketio
import random
from helper_functions import get_random_string  ## Getting random string
from generating_winning_seq import check_winner  ## This function will help us determine the winner of the round

activeMembers = []
roomDetails = []
playerQueue = []
roundDetails = []

## creates a new Async Socket IO Server
sio = socketio.AsyncServer(cors_allowed_origins='*')
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)

## we can define aiohttp endpoints just as we normally
## would with no change
async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

## If we wanted to create a new websocket endpoint,
## use this decorator, passing in the name of the
## event we wish to listen out for
@sio.on('message')
async def print_message(sid, message):
    ## When we receive a new event of type
    ## 'message' through a socket.io connection
    ## we print the socket ID and the message
    print("Socket ID: " , sid)
    print(message)
    return "message received"

@sio.event
async def connect(sid, environ, auth):
    print('connect member ', sid)
    # await sio.emit("updatemembers", {"data": "update"})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.on("status")
def get_status():
    return {"status": "running"}


# API endpoint : getRoomscoys :: getting all rooms ids

@sio.on("getRoomscoys")
def get_rooms():
    ls_roomsId = list(set([room['roomId'] for room in roomDetails]))
    return ({"Status": "Success", "data":ls_roomsId})

@sio.on("getMembers")
def get_members(sid, data):
    roomId = data["roomId"]
    members = {}
    for member in activeMembers:
        if member["roomId"] == roomId:
            members[member["playerSeatNum"]] = {"name": member['playerName'], "stack": member["playerStack"]}
    return {"data" : members}

# API endpoint : createMember&Room :: creating new player and room along with rest of details required in the database

@sio.on("createMember&Room")
async def create_member_room(sid, message):
    name = message['user_name']
    stack = message['stack']
    ls_roomsId = get_rooms()['data']
    room_id = ""
    counter = 0
    while(room_id in ls_roomsId == False or counter ==0):
        first = get_random_string(15)  ## first string of length 15
        second = get_random_string(15)  ## second string of length 15
        room_id = first+"-"+second  ## final room id
        print(room_id)
        counter+=1

    mydict = {"members":[name], "roomId": room_id, "roomLeader": name}
    roomDetails.append(mydict)

    mydict = {"playerName": name,"roomId": room_id,"playerStatus": "Online", "playerRole":"Owner", "playerStack": stack,  "playerMove": "", "playerSeatNum": 1, "playerApproval": "True",  "playerCards": "", "playerPack": "False" }
    activeMembers.append(mydict)

    sio.enter_room(sid, room_id)

    return({"Status":"Success", "Message":"New room and player has been created", "data":room_id})



# API endpoint : createmember :: creating new player, this is the player joining preexisting room

@sio.on("createMember")
async def create_member(sid, data):

    name = data["name"]
    stack = data["stack"]
    roomId = data["roomId"]

    playerRoomNames = []  ## collecting names of the players present in the room
    
    for room in roomDetails:
        if roomId == room['roomId']:
            document = room
            break
            
    
    if(len(document)!=0):
        playerRoomNames = document['members']
    
    playerQueueNames = []  ## collecting names of the players present in the queue for that room
    
    for room in playerQueue:
        if roomId == room['roomId']:
            playerQueueNames = room
            break

    if(len(playerQueueNames) !=0 ):
        temp = []
        for i in range(len(playerQueueNames['queue'])):
            if(playerQueueNames['queue'][i] is None):
                pass
            else:
                temp.append(playerQueueNames['queue'][i]["name"])
        playerQueueNames = temp
    
    if(len(playerRoomNames)!=0 ):  ## Used to check if the room exists
        if(len(playerQueueNames) != 0): ## Used to check if the player queue for that room exists
            if(not(name in playerQueueNames) and not(name in playerRoomNames)):
                for i, room in enumerate(playerQueue):
                    if roomId == room['roomId']:
                        index = i
                        break
                
                playerQueue[index]["queue"].append({"name" : name, "stack": stack,"roomId": roomId, "seatNum":-1})
                sio.enter_room(sid, roomId)
                await sio.emit("updatemembers", {"message":playerQueue[index]}, room=roomId)
                return ({"Status":"Success", "Message": "New member has been added to the playerqueue"})

            elif(name in playerQueueNames):
                return({"Status":"Fail", "Message": "Name exists in queue, pick a different name"})

            elif(name in playerRoomNames):
                return({"Status":"Fail", "Message": "Name exists in room, pick a different name"})

            else:
                return({"Status":"Fail", "Message": "Something wrong happened"})
        
        else:

            for i, room in enumerate(playerQueue):
                if roomId == room['roomId']:
                    index = i
                    break
            
            queue = {"queue" : [{"name" : name, "stack": stack,"roomId": roomId, "seatNum":-1}], "roomId":roomId}
            playerQueue.append(queue)
            sio.enter_room(sid, roomId)
            await sio.emit("updatemembers", {"message":queue}, room=roomId)
            return ({"Status":"Success", "Message":"New player has been created and new queue has been added to the playerqueue"})
    else:
        return({"Status":"Fail", "Message": "Room doesn't exist"})


# API endpoint : checkQueue :: Only owner can use this to check the queue 

def getQueue(roomId):
    for queue in playerQueue:
        if queue["roomId"] == roomId:
            return queue["queue"]

@sio.on("checkQueue")
def check_Queue(sid, data):
    roomId = data["roomId"]
    for queue in playerQueue:
        if queue["roomId"] == roomId:
            return {"data" : queue["queue"]}


@sio.on("isRoomLead")
def is_room_lead(name, roomId):
    for room in roomDetails:
        if room["roomId"] == roomId:
            if room["roomLeader"] == name:
                return True
            return False

@sio.on("requestSeat")
async def request_seat(sid, data):
    name = data["name"]
    seatNum = data["seatNum"]
    roomId = data["roomId"]
    print(data)
    p_queue = []
    for j, queue in enumerate(playerQueue):
        if queue['roomId'] == roomId:
            p_queue = queue['queue']
            room_index = j
            break
    
    if p_queue:
        update_index = None
        for i, player in enumerate(p_queue):
            if player["name"] == name:
                update_index = i
                break

        print("update index", update_index)
        # print(playerQueue)
        playerQueue[room_index]["queue"][update_index]["seatNum"] = seatNum
        # print(playerQueue)
        queue = getQueue(roomId)
        await sio.emit("updatequeue", {"data": queue}, room=roomId)
        return {"message": "seat number updated", "data": queue}


# API endpoint : allowPlayer :: Only owner can use this to allow players into table

@sio.on("allowPlayer")
async def allowPlayer(sid, data):
    # print(data)
    name, stack, decision, roomId, seatnum = data["name"], data["stack"], data["decision"], data["roomId"], data["seatnum"]
    queueIndex = None
    for index, q in enumerate(playerQueue):
        if q["roomId"] == roomId:
            queueIndex = index
            break

    roomIndex = None
    for index, r in enumerate(roomDetails):
        if r["roomId"] == roomId:
            roomIndex = index
            break
    
    if decision == "Allow":
        try:
            playerQueue[queueIndex]["queue"] = [n for n in playerQueue[queueIndex]["queue"] if n["name"] != name]
            # print(playerQueue)
            activeMembers.append({"playerName": name,"roomId": roomId,"playerStatus": "Online", "playerRole":"Player", "playerStack": stack,  "playerMove": "", "playerSeatNum": -1, "playerApproval": "True",  "playerCards": "", "playerPack": "False" })
            roomDetails[roomIndex]["members"].append(name)
            assignSeat(name, seatnum, roomId)
            await sio.emit("updateMembers", {}, room=roomId)
            return ({"Status":"Success", "Message": "Player has been added to activeMembers"})
        except Exception as e:
            print(e)
    else:
        # print(playerQueue[queueIndex], name)
        playerQueue[queueIndex]["queue"] = [n for n in playerQueue[queueIndex]["queue"] if n["name"] != name]
        await sio.emit("denySeat", {"name": name}, room=roomId)
        return ({"Status":"Fail", "Message": "Player doesn't exist in the queue"})


# API endpoint : assignSeat :: This api will assign the seat to the player just added to the room

# @sio.on("assignSeat")
def assignSeat(name, seatnum, roomId):
    for i, member in enumerate(activeMembers):
        if member["roomId"] == roomId and member["playerName"] == name:
            activeMembers[i]["playerSeatNum"] = int(seatnum)
            return ({"Status":"Success", "Message": "Player seat number has been changed"})

    return ({"Status":"Fail", "Message": "Player not found"})


# API endpoint : playerExit :: This api will remove player from the room and activemember

@sio.on("playerExit")
async def playerExit(sid, data):
    name, roomId = data["name"], data["roomId"] 
    room_index = ""
    for i, member in enumerate(activeMembers):
        if member["roomId"] == roomId and member["playerName"] == name:
            room_index = i
            break
    
    # print("before",activeMembers)
    activeMembers.pop(room_index)
    # print("after",activeMembers)

    for i, room in enumerate(roomDetails):
        if room["roomId"] == roomId:
            room["members"].remove(name)
            break
    
    await sio.emit("player_left", {"Status":"Success", "Message": "Player has been exited"}, room=roomId)
    return ({"Status":"Success", "Message": "Player has been exited"})


# API endpoint : playerAway :: This api will change player's status to Away

@sio.on("playerAway")
def playerAway(sid, data):
    name, roomId = data["name"], data["roomId"]
    room_index = ""
    for i, member in enumerate(activeMembers):
        if member["roomId"] == roomId and member["playerName"] == name:
            room_index = i
            break
    
    activeMembers[room_index]["playerStatus"] = "Away"
    activeMembers[room_index]["playerSeatNum"] = -1

    for i, room in enumerate(playerQueue):
        if room["roomId"] == roomId:
            playerQueue[i]["queue"].append({"name" : name, "stack": 0,"roomId": roomId})
            break


    return ({"Status":"Success", "Message": "Player status has been changed to Away and returned to player queue"})
    

# API endpoint : playerBack :: This api will change player's status to Online

@sio.on("playerBack")
def playerBack(sid, data):
    name, roomId = data["name"], data["roomId"]
    room_index = ""
    for i, member in enumerate(activeMembers):
        if member["roomId"] == roomId and member["playerName"] == name:
            room_index = i
            break
    
    activeMembers[room_index]["playerStatus"] = "Online"
    return ({"Status":"Success", "Message": "Player status has been changed to Online"})


# API endpoint : startRound :: This api will start a new round for the players to play

@sio.on("startFirstRound")
async def startFirstRound(sid, data):  ## starts round and assigns card to players who are online and their seat number is assigned 
    roomId, starting_board = data["roomId"], 10
    try:
        print("point 0")
        #ls_curr_id = []  ## contains id of all the players who are online and their seat number is assigned 
        ls_curr_names = []  ## contains names of the players who are online and their seat is assigned
        ls_curr_cards = []  ## contains cards of the players who are online and their seat is assigned
        #ls_total_id = []  ## contains id of the all players
        ls_total_seatnum = []  ##contains seat number of the all players
        ls_total_names = []  ## contains names of all players
        ls_curr_stack = []  ## contains stack of players who are online and their seat is assigned
        ls_curr_seatnum = []  ## contains seat number of players who are online and their seat is assigned
        current_dealer_name = ""  ## contains name of the player with lowest seat number
        current_player = ""  ## will contain the number of player seating next to dealer, will start the game.
        current_player_seatnum = 11
        document = []
        # print(activeMembers)
        index = None
        # for i in range(len(activeMembers)):
        #     if(activeMembers[i]['roomId'] == roomId):
        #         document.append(activeMembers)
        for i, room in enumerate(activeMembers):
            if room["roomId"] == roomId:
                index = i
                document = room
                print("point 0.1")
                # print(document)
                if(document["playerStatus"] == "Online" and document["playerSeatNum"] != -1):
                    #ls_curr_id.append(document["_id"])
                    ls_curr_names.append(document["playerName"])
                    ls_curr_stack.append(document["playerStack"])
                    ls_curr_seatnum.append(document["playerSeatNum"])
                print("point 0.2")
                ls_total_seatnum.append(document["playerSeatNum"])
                ls_total_names.append(document["playerName"])
                #ls_total_id.append(document["_id"])
                print(0.3)
        if(len(ls_curr_names) == 0):
            print("point 1")
            return({"Status":"Fail", "Message": "Noone is playing"})
        elif(len(ls_curr_names) == 1):
            print("point 2")
            return({"Status":"Fail", "Message": "Only one player is playing"})
        else:
            print("point 3")
            temp = ls_curr_seatnum.copy()
            temp.sort()
            current_dealer_name = ls_curr_names[ls_curr_seatnum.index(temp[0])]
            current_player = ls_curr_names[ls_curr_seatnum.index(temp[1])]
            current_player_seatnum = temp[1]

            print("point 4")
            # for i in ls_curr_id:
            #     pass
            ls = []
            card_names = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]  ## All card names in a list
            card_types = ["Sp","He","Di","Cl"]  ## All card types in a list

            for i in range(len(card_names)):  ## Creating all card permutations
                for j in range(len(card_types)):
                    ls.append(card_names[i]+"-"+card_types[j])  ## List ls has all cards in it

            print("point 5")
            random.shuffle(ls)  ## Shuffling the deck of cards
            for i in range(len(ls_curr_names)):  ## Number of cards for each player
                temp_str = ""
                for j in range(0,3):  ## One by one card for each player as done by dealer in real life
                    if(j == 0 or j ==1):
                        temp_str = temp_str+ls[0]+" "
                    else:
                        temp_str+= ls[0] 
                    ls.pop(0)
                ls_curr_cards.append(temp_str)

        print("point 6")
        temp_array = []
        temp_array1 = []
        temp_array2 = []
        temp = ls_curr_seatnum.copy()
        temp.sort()
        seatnum_index = temp.index(current_player_seatnum)
        temp_array2 = temp[seatnum_index:]
        print("point 7")
        for i in range(len(temp[:seatnum_index])):
            temp_array2.append(temp[i])
        for i in range(len(ls_curr_names)):
            temp_array1.append(starting_board)
            temp_array.append("No")
            ls_curr_stack[i] = float(ls_curr_stack[i])-float(starting_board)


        mydict = {"roomId":roomId,  ##  Data Schema for the round details
        "currentPlayerDecision":"-", "currentBoard":starting_board, "currentDealer": current_dealer_name, "currentGameType":"Normal", "current_player":current_player,"current_player_seatnum":current_player_seatnum,
        "currentPlayerCardSeen": list(temp_array), "currentPlayerCards": ls_curr_cards, "currentPlayerNames":ls_curr_names, "currentPlayerPack": temp_array, "currentPlayerSeatNum":ls_curr_seatnum,
        "currentPot":float(starting_board)*len(ls_curr_names), "roundStarted": "Yes","currentPlayerRotation":list(temp_array2), "totalPlayerNames": ls_total_names, "totalPlayerSeatNum":ls_total_seatnum, "fullShowPossible": False,
        "sideShowPossible":False, "currentPlayerBoard": list(temp_array1), "currentPlayerStack": ls_curr_stack, "game_board": starting_board, "player_won":""}

        roundDetails.append(mydict)

        print("point 8")  
        print(roundDetails)
        await sio.emit("gameStarted", {}, room=roomId)
        return({"Status":"Success", "Message": "Players have been assigned their cards"})
    except Exception as e:
        print(e)
        print("Some error")

# API endpoint : getRoundInfo :: This api will get the getRoundInfo move for frontend

@sio.on("getRoundInfo")  
def getRoundInfo(sid, data):
    roomId = data["roomId"]
    mydict = None

    for room in roundDetails:
        if room["roomId"] == roomId:
            mydict = room
            break

    if not mydict:
        return {}

    # del mydict['_id']
    # del mydict['currentPlayerId']
    # del mydict['totalPlayerId']
    # print(mydict)
    return mydict  ## returns all the data from roundDetails for that room


# API endpoint : updateMove :: This api will update the database depending on the currentPlayer's move

@sio.on("updateMove")
async def updateMove(sid, data):
    roomId, name, move = data["roomId"], data["name"], data["move"]
    amount = data["amount"]
    playerseat = -22
    print("update move called")
    room_index = None

    for i, room in enumerate(roundDetails):
        if room['roomId'] == roomId:
            room_index = i
            document = room
            break

    index = -1
    current_board = -1
    players_card_seen = []
    side_show = False
    full_show = False
    current_player = ""
    current_player_rotation = []
    current_player_seat_num = -1
    players_seat_num = []
    players_stack = []
    current_pot = -1
    players_cards = []

    
    current_player = document['current_player']
    current_pot = document['currentPot']
    current_player_seat_num = document['current_player_seatnum']
    current_player_rotation = document['currentPlayerRotation']
    player_names = document['currentPlayerNames'] 
    index = player_names.index(name)
    player_Cards = document['currentPlayerCards']
    current_board = document['currentBoard']
    players_card_seen = document['currentPlayerCardSeen']
    side_show = document['sideShowPossible']
    full_show = document['fullShowPossible']
    players_seat_num = document['currentPlayerSeatNum']
    players_stack = document['currentPlayerStack']
    player_cards = document['currentPlayerCards']
    current_player_pack = document['currentPlayerPack']
    current_player_name = document['currentPlayerNames']
    print("document",document)
    print("current_player_pack",current_player_pack)

    ## Checking for full show possibility
    if(full_show == False):
        if(len(current_player_rotation) == 2):
            roundDetails[room_index]["fullShowPossible"] = True  
            roundDetails[room_index]["sideShowPossible"] = False
            full_show = True  

    ## Will Contain the code for all the moves played by the current user
    if(move == "SeeCards"):
        print("SEE CARD")
        print("before",roundDetails)
        print("room index",room_index)
        roundDetails[room_index]["currentPlayerCardSeen"][index] = "Yes" 
        roundDetails[room_index]["currentPlayerBoard"][index] = current_board * 2
        print(current_board * 2)
        print("before2",roundDetails)
        # current_player_pack = roundDetails[room_index]["currentPlayerPack"]
        if(side_show == False):
            c = 1
            print("before3",roundDetails)
            print(current_player_pack, players_card_seen)
            for i in range(len(players_card_seen)):
                if(current_player_pack[i] == "No" and players_card_seen[i] == "Yes"):
                    c+=1          
            print("card seen",c, len(current_player_rotation))
            if(c >= len(current_player_rotation)):
                roundDetails[room_index]['sideShowPossible'] = True  
        
        await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": player_Cards[index],
                "move": move
                }, room=roomId)
        print("after",roundDetails)    
        return(player_Cards[index])
    
    elif(move == "Pack" ):
        print("PACK CALLED")
        if(len(current_player_rotation)<=2):
            # print(current_player_rotation)
            current_player_rotation.remove(current_player_seat_num)
            winner_seatnum = current_player_rotation[0]
            winner  = player_names[players_seat_num.index(winner_seatnum)]
            # Changing player_won name 
            roundDetails[room_index]["player_won"] = winner
            roundDetails[room_index]["current_player_seatnum"] = -1
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{winner} is the winner",
                "move": move
                }, room=roomId)
            return({"Status":"Success", "Message": f"{winner} is the winner"})

        elif(current_player == player_names[room_index] and len(current_player_rotation)>1):
            roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
            roundDetails[room_index]["currentPlayerRotation"].remove(current_player_seat_num)
            roundDetails[room_index]["currentPlayerPack"][index] = "Yes"
            index1 = players_seat_num.index(current_player_rotation[1])
            roundDetails[room_index]["current_player"] = player_names[index1]
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{current_player} has been packed",
                "move": move
                }, room=roomId)
            return({"Status":"Success", "Message": f"{current_player} has been packed"})
        elif(current_player != player_names[room_index] and len(current_player_rotation)>1):
            # index1 = players_seat_num[player_names.index(name)]
            roundDetails[room_index]["currentPlayerRotation"].remove(players_seat_num[player_names.index(name)])
            roundDetails[room_index]["currentPlayerPack"][player_names.index(name)] = "Yes"
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{player_names[room_index]} has been packed",
                "move": move
                }, room=roomId)
            return({"Status":"Success", "Message": f"{player_names[room_index]} has been packed"})
        

        if(len(current_player_rotation)-1 == 2):
            roundDetails[room_index]["fullShowPossible"] = True

    elif(move == "Check" and current_player == name):
        if((float(players_stack[index]) - 2*float(current_board) < 0 and players_card_seen[index] == "Yes") or (float(players_stack[index]) - float(current_board) < 0 and players_card_seen[index] == "No") ):
            roundDetails[room_index]["currentPlayerPack"][index] = "Yes"
            if(current_player == player_names[room_index] and len(current_player_rotation)>1):
                roundDetails[room_index]["current_player_seatnum"]= current_player_rotation[1]
                roundDetails[room_index]["currentPlayerRotation"].remove(current_player_seat_num)
                index1 = players_seat_num.index(current_player_rotation[1])
                roundDetails[room_index]["current_player"] = player_names[index1]
                await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{current_player} has been packed",
                "move": move
                }, room=roomId)
                return({"Status":"Success", "Message": f"{current_player} has been packed"})
            elif(current_player != player_names[room_index] and len(current_player_rotation)>1):
                roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
                index2 = player_names.index(current_player)
                roundDetails[room_index]["currentPlayerRotation"] = players_seat_num[index2]
                index1 = players_seat_num.index(current_player_rotation[1])
                roundDetails[room_index]["current_player"] = player_names[index1]
                await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{current_player} has been packed",
                "move": move
                }, room=roomId)
                return({"Status":"Success", "Message": f"{current_player} has been packed"})
            elif(current_player != player_names[index] and len(current_player_rotation)<=1):
                roundDetails[room_index]["player_won"] = winner
                roundDetails[room_index]["current_player_seatnum"] = -1
                await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"{current_player} has been packed",
                "move": move
                }, room=roomId)
                return({"Status":"Success", "Message": f"{current_player} is the winner"})
        elif(float(players_stack[index]) - 2*float(current_board) >= 0 and players_card_seen[index] == "Yes"):
            roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - 2*float(current_board)
            roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
            roundDetails[room_index]["currentPot"] = float(current_pot)+2*float(current_board)
            index1 = players_seat_num.index(current_player_rotation[1])
            roundDetails[room_index]["current_player"] = player_names[index1]
            new_rotation = []
            for i in range(1, len(current_player_rotation),1):
                new_rotation.append(current_player_rotation[i])
            new_rotation.append(current_player_rotation[0])
            roundDetails[room_index]["currentPlayerRotation"] = new_rotation
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Board *2 was deducted",
                "move": move
                }, room=roomId)
            return({"Status":"Success", "Message": "Board *2 was deducted"})
        elif(float(players_stack[index]) - float(current_board) >= 0 and players_card_seen[index] == "No"):
            roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - float(current_board)
            roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
            roundDetails[room_index]["currentPot"] = float(current_pot)+float(current_board)          
            index1 = players_seat_num.index(current_player_rotation[1])
            roundDetails[room_index]["current_player"] = player_names[index1]
            new_rotation = []
            for i in range(1, len(current_player_rotation),1):
                new_rotation.append(current_player_rotation[i])
            new_rotation.append(current_player_rotation[0])
            roundDetails[room_index]["currentPlayerRotation"] = new_rotation
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Board was deducted",
                "move": move
                }, room=roomId)
            return({"Status":"Success", "Message": "Board was deducted"}) 
    elif(move  == 'Raise' and current_player == name):
        if(float(players_stack[index])-float(amount)>=0):
            if(players_card_seen[index] == "Yes"):
                roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - float(amount)
                roundDetails[room_index]["currentPot"] = float(current_pot)+float(amount) 
                roundDetails[room_index]["currentBoard"] = float(amount)/2
                print("case 1")
                
            else:
                roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - float(amount)
                roundDetails[room_index]["currentPot"] = float(current_pot)+float(amount) 
                roundDetails[room_index]["currentBoard"] = float(amount)
                print(amount)
                print(roundDetails[room_index]["currentBoard"])
                print("case 2")

            roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
            index1 = players_seat_num.index(current_player_rotation[1])
            roundDetails[room_index]["current_player"] = player_names[index1]
            new_rotation = []
            for i in range(1, len(current_player_rotation),1):
                new_rotation.append(current_player_rotation[i])
            new_rotation.append(current_player_rotation[0])
            roundDetails[room_index]["currentPlayerRotation"] = new_rotation
            
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Board has been raised",
                "move": move
                }, room=roomId)
            print("case 0: ", roundDetails[room_index]["currentBoard"])
            print("case 0")
            return({"Status":"Success", "Message": "Board has been raised"})
        else:
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"This move is not possible as the player has low funds",
                "move": move
                }, room=roomId)
            print("case 3")
            return ({"Status":"Failure", "Message": "This move is not possible as the player has low funds"})
    elif(move == "SideShow" and current_player == name):
        if(side_show == False):
            await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Side Show is not available at the moment",
                "move": move
                }, room=roomId)
            return({"Status":"Failure", "Message": "Side Show is not available at the moment"})
        else:
            temp = current_player_rotation.copy()
            # print(temp)
            temp.reverse()
            # print(temp)
            temp.pop()
            # print(temp)
            playerseat = int(playerseat)
            # print(type(playerseat), type(temp[0]), playerseat, temp)
            if(len(temp) ==1):
                await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Only full show is possible",
                "move": move
                }, room=roomId)
                return({"Status":"Failure", "Message": "Only full show is possible"})
            elif(len(temp) <=1):
                await sio.emit("player_update_move", {
                "roomId" : roomId,
                "message": f"Side Show is not possible, only 1 player remaining",
                "move": move
                }, room=roomId)
                return({"Status":"Failure", "Message": "Side Show is not possible, only 1 player remaining"})
            else:
                if(playerseat in temp):
                    index231 = current_player_name.index(name)
                    roundDetails[room_index]["currentPlayerStack"][index231] = float(players_stack[index231]) - float(current_board) * 2 
                    roundDetails[room_index]["currentPot"] = float(current_pot) + float(current_board) * 2
                    
                    myindex = players_seat_num.index(current_player_seat_num)
                    opponentindex = players_seat_num.index(playerseat)
                    winner  = check_winner([player_names[myindex], player_names[opponentindex] ], [player_cards[myindex],player_cards[opponentindex]])
                    if(winner[0] == player_names[myindex]):
                        roundDetails[room_index]["currentPlayerRotation"].remove(players_seat_num[opponentindex])
                        roundDetails[room_index]["currentPlayerPack"][opponentindex] = "Yes"
                        await sio.emit("player_update_move", {
                            "roomId" : roomId,
                            "message": f"{player_names[opponentindex]} has been packed",
                            "move": move
                            }, room=roomId)
                        return({"Status":"Success", "Message": f"{player_names[opponentindex]} has been packed"})
                    elif(winner[0] == player_names[opponentindex]):
                        roundDetails[room_index]["current_player_seatnum"] = current_player_rotation[1]
                        roundDetails[room_index]["currentPlayerRotation"].remove(current_player_seat_num)
                        roundDetails[room_index]["currentPlayerPack"][index] = "Yes"
                        index1 = players_seat_num.index(current_player_rotation[1])
                        roundDetails[room_index]["current_player"] = player_names[index1]
                        await sio.emit("player_update_move", {
                            "roomId" : roomId,
                            "message": f"{current_player} has been packed, {player_names[opponentindex]} has won the side show",
                            "move": move
                            }, room=roomId)
                        return({"Status":"Success", "Message": f"{current_player} has been packed, {player_names[opponentindex]} has won the side show"})
                else:
                    await sio.emit("player_update_move", {
                            "roomId" : roomId,
                            "message": f"Side Show is not possiblefor this player",
                            "move": move
                            }, room=roomId)
                    return({"Status":"Failure", "Message": "Side Show is not possiblefor this player"})


    elif(move == "FullShow" and current_player == name):
        print("full show called", current_player, name)
        if(full_show == True):
            if(players_card_seen[index] == "Yes"):
                if(float(players_stack[index]) - float(current_board)*2 >=0):
                    ## cut money from player stack, add to pot , full show, declare winner, transfer pot money
                    roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - float(current_board)*2
                    roundDetails[room_index]["currentPot"] = float(current_pot)+float(current_board)*2
                    my_cards = player_cards[index]
                    opponent_index = -1
                    for i in range(len(current_player_rotation)):
                        if(current_player_rotation[i] != players_seat_num[index]):
                            opponent_index = players_seat_num.index(current_player_rotation[i])
                    opponent_cards = player_cards[opponent_index]
                    winner  = check_winner([player_names[index], player_names[opponent_index] ], [my_cards,opponent_cards])
                    if(winner[0] == player_names[index]):
                        roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) + float(current_pot)+ float(current_board)*2
                        roundDetails[room_index]["currentPot"] = 0
                    else:
                        roundDetails[room_index]["currentPlayerStack"][opponent_index] = float(players_stack[opponent_index]) + float(current_pot)+ float(current_board)*2
                        roundDetails[room_index]["currentPot"] = 0
                    
                    for room in roundDetails:
                        if room["roomId"] == roomId:
                            players_stack = room['currentPlayerStack']

                    active_members_list = []
                    for i, room in enumerate(activeMembers):
                        if room["roomId"] == roomId:
                            active_members_list.append([i, room])

                    print("active members", active_members_list)
                    print("player_names", player_names)
                    for i in range(len(player_names)):
                        for j, member in active_members_list:
                            print(player_names, i, member)
                            if member["playerName"] == player_names[i]:
                                activeMembers[j]["playerStack"] = str(players_stack[i])
                                activeMembers[j]["playerSeatNum"] = int(players_seat_num[i])

                    roundDetails[room_index]["player_won"] = winner[0]
                    roundDetails[room_index]["current_player_seatnum"] = -1
                    await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"{winner[0]} wins, by {winner[1]}",
                        "move": move
                        }, room=roomId)
                    print({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                    return({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                                                    
                else:
                    print({"Status":"Failure", "Message": "Dont have enough money"})
                    await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"Dont have enough money",
                        "move": move
                        }, room=roomId)
                    return({"Status":"Failure", "Message": "Dont have enough money"})   
            elif(players_card_seen[index] == "No"):
                if(float(players_stack[index]) - float(current_board) >=0):
                    active_members_list = []
                    for i, room in enumerate(activeMembers):
                        if room["roomId"] == roomId:
                            active_members_list.append([i, room])
                    ## cut money from player stack, add to pot , full show, declare winner, transfer pot money
                    roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) - float(current_board)
                    roundDetails[room_index]["currentPot"] = float(current_pot)+float(current_board) 
                    my_cards = player_cards[index]
                    opponent_index = -1
                    for i in range(len(current_player_rotation)):
                        if(current_player_rotation[i] != players_seat_num[index]):
                            opponent_index = players_seat_num.index(current_player_rotation[i])
                    opponent_cards = player_cards[opponent_index]
                    winner  = check_winner([player_names[index], player_names[opponent_index] ], [my_cards,opponent_cards])
                    if(winner[0] == player_names[index]):
                        roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[index]) + float(current_pot)+ float(current_board)
                        roundDetails[room_index]["currentPot"] = 0
                    else:
                        roundDetails[room_index]["currentPlayerStack"][index] = float(players_stack[opponent_index]) + float(current_pot)+ float(current_board)
                        roundDetails[room_index]["currentPot"] = 0

                    for i in range(len(player_names)):
                        for j, member in active_members_list:
                            if member["playerName"] == player_names[i]:
                                activeMembers[j]["playerStack"] = str(players_stack[i])
                                activeMembers[j]["playerSeatNum"] = int(players_seat_num[i])

                    roundDetails[room_index]["player_won"] = winner[0]
                    roundDetails[room_index]["current_player_seatnum"] = -1
                    await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"{winner[0]} wins, by {winner[1]}",
                        "move": move
                        }, room=roomId)
                    print({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                    return({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                else:
                    await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"Dont have enough money",
                        "move": move
                        }, room=roomId)
                    print({"Status":"Failure", "Message": "Dont have enough money"})
                    return({"Status":"Failure", "Message": "Dont have enough money"})   
            else:            
                await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"Something went wrong",
                        "move": move
                        }, room=roomId)
                print({"Status":"Failure", "Message": "Something went wrong"})
                return({"Status":"Failure", "Message": "Something went wrong"})
        else:
            await sio.emit("player_update_move", {
                        "roomId" : roomId,
                        "message": f"Full Show not possible",
                        "move": move
                        }, room=roomId)
            print({"Status":"Failure", "Message": "Full Show not possible"})
            return({"Status":"Failure", "Message": "Full Show not possible"})

    else:
        await sio.emit("player_update_move", {
                            "roomId" : roomId,
                            "message": f"This move doesn't exist",
                            "move": move
                            }, room=roomId)
        return ({"Status":"Failure", "Message": "This move doesn't exist"})


# API endpoint : refreshRound :: This api will allow to check and update pot details for each game
@sio.on("refreshRound")
async def refreshRound(sid, data):
    roomId = data["roomId"]
    #ls_curr_id = []  ## contains id of all the players who are online and their seat number is assigned 
    ls_curr_names = []  ## contains names of the players who are online and their seat is assigned
    ls_curr_cards = []  ## contains cards of the players who are online and their seat is assigned
    #ls_total_id = []  ## contains id of the all players
    ls_total_seatnum = []  ##contains seat number of the all players
    ls_total_names = []  ## contains names of all players
    ls_curr_stack = []  ## contains stack of players who are online and their seat is assigned
    ls_curr_seatnum = []  ## contains seat number of players who are online and their seat is assigned
    current_dealer_name = ""  ## contains name of the player with lowest seat number
    current_player = ""  ## will contain the number of player seating next to dealer, will start the game.
    current_player_seatnum = 11
    starting_board = -1

    dummy_temp = []

    for room in activeMembers:
        if room['roomId'] == roomId:
            document = room
            print("doc 1", document)


            if(document["playerStatus"] == "Online" and document["playerSeatNum"] != -1):
                # ls_curr_id.append(document["_id"])
                ls_curr_names.append(document["playerName"])
                ls_curr_stack.append(document["playerStack"])
                ls_curr_seatnum.append(document["playerSeatNum"])
            ls_total_seatnum.append(document["playerSeatNum"])
            ls_total_names.append(document["playerName"])
        #ls_total_id.append(document["_id"])

    if(len(ls_curr_names) == 0):
        print({"Status":"Fail", "Message": "Noone is playing"})
        return({"Status":"Fail", "Message": "Noone is playing"})
    elif(len(ls_curr_names) == 1):
        print({"Status":"Fail", "Message": "Only one player is playing"})
        return({"Status":"Fail", "Message": "Only one player is playing"})
    else:
        for room in roundDetails:
            if room["roomId"] == roomId:
                document = room
                break

        print("doc", document)

        starting_board = document['game_board']
        current_dealer_name = document['currentDealer']

        temp = ls_curr_seatnum.copy()
        temp.sort()

        last_dealer = current_dealer_name
        current_dealer_name = ""

        if(last_dealer in ls_curr_names):
            last_dealer_seatnum = ls_curr_seatnum[ls_curr_names.index(last_dealer)]
            if(last_dealer_seatnum == temp[-1]):
                print("A")
                current_dealer_seatnum = temp[0]
                current_player_seatnum = temp[1]
                current_dealer_name = ls_curr_names[ls_curr_seatnum.index(current_dealer_seatnum)]
                current_player = ls_curr_names[ls_curr_seatnum.index(current_player_seatnum)]
            else:
                current_dealer_seatnum = temp[temp.index(last_dealer_seatnum)+1]
                current_dealer_name = ls_curr_names[ls_curr_seatnum.index(current_dealer_seatnum)]
                if(current_dealer_seatnum == temp[-1]):
                    print("B")
                    current_player_seatnum = temp[0]
                    current_player = ls_curr_names[ls_curr_seatnum.index(current_player_seatnum)]
                else:
                    print("C")
                    current_player_seatnum = temp[temp.index(current_dealer_seatnum)+1]
                    current_player = ls_curr_names[ls_curr_seatnum.index(current_player_seatnum)]
                    
        else:
            current_dealer_name = random.choice(ls_curr_names)
            current_dealer_seatnum = ls_curr_seatnum[ls_curr_names.index(current_dealer_name)]
            if(current_dealer_seatnum == temp[-1]):
                print("D")
                current_player = ls_curr_names[ls_curr_seatnum.index(temp[0])]
                current_player_seatnum = temp[0]
            else:
                print("E")
                current_player_seatnum = temp[temp.index(current_dealer_seatnum)+1]
                current_player = ls_curr_names[ls_curr_seatnum.index(current_player_seatnum)]

        for i in ls_curr_names:
            pass
        ls = []
        card_names = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]  ## All card names in a list
        card_types = ["Sp","He","Di","Cl"]  ## All card types in a list

        for i in range(len(card_names)):  ## Creating all card permutations
            for j in range(len(card_types)):
                ls.append(card_names[i]+"-"+card_types[j])  ## List ls has all cards in it


        random.shuffle(ls)  ## Shuffling the deck of cards
        for i in range(len(ls_curr_names)):  ## Number of cards for each player
            temp_str = ""
            for j in range(0,3):  ## One by one card for each player as done by dealer in real life
                if(j == 0 or j ==1):
                    temp_str = temp_str+ls[0]+" "
                else:
                    temp_str+= ls[0] 
                ls.pop(0)
            ls_curr_cards.append(temp_str)
        temp_array = []
        temp_array1 = []
        temp_array2 = []
        temp = ls_curr_seatnum.copy()
        temp.sort()
        print("temp", temp)
        seatnum_index = temp.index(current_player_seatnum)
        print("temp1", temp[seatnum_index:])
        print("temp2", temp[:seatnum_index])
        temp_array2 = temp[seatnum_index:]
        for i in range(len(temp[:seatnum_index])):
            temp_array2.append(temp[i])
        print("temp_array2", temp_array2)
        dummy_temp = temp_array2
        for i in range(len(ls_curr_names)):
            temp_array1.append(starting_board)
            temp_array.append("No")
            ls_curr_stack[i] = float(ls_curr_stack[i])-float(starting_board)

        mydict = {"roomId":roomId,  ##  Data Schema for the round details
        "currentPlayerDecision":"-", "currentBoard":starting_board, "currentDealer": current_dealer_name, "currentGameType":"Normal", "current_player":current_player,"current_player_seatnum":current_player_seatnum,
        "currentPlayerCardSeen": list(temp_array), "currentPlayerCards": ls_curr_cards, "currentPlayerNames":ls_curr_names, "currentPlayerPack": list(temp_array), "currentPlayerSeatNum":ls_curr_seatnum,
        "currentPot":float(starting_board)*len(ls_curr_names), "roundStarted": "Yes","currentPlayerRotation":dummy_temp, "totalPlayerNames": ls_total_names, "totalPlayerSeatNum":ls_total_seatnum, "fullShowPossible": False,
        "sideShowPossible":False, "currentPlayerBoard": list(temp_array1), "currentPlayerStack": ls_curr_stack, "game_board":starting_board, "player_won":""}

        for i, room in enumerate(roundDetails):
            if room["roomId"] == roomId:
                doc = room
                old_id = i
                break
        
        print("old index",old_id)
        print("roundDetails before pop",roundDetails)
        roundDetails.pop(old_id)
        print("after pop",roundDetails)
        
        roundDetails.append(mydict)
            
    print("\n\nrefresh round\n", roomId,roundDetails)
    print(dummy_temp)
    await sio.emit("gameStarted", {"Status":"Success", "Message": "Players have been re-assigned their cards"}, room=roomId)
    print(dummy_temp)
    return({"Status":"Success", "Message": "Players have been re-assigned their cards"})


@sio.on("start_timer")
async def start_timer(sid, data):
    
    await sio.emit("player_start_timer", data, room=data['roomId'])
    return data
# API endpoint : transferOwnerShip :: This api trasnfer ownership of the game to the player mentioned

def transferOwnerShip(roomId, name, owner):
    pass

## We bind our aiohttp endpoint to our app
## router
app.router.add_get('/', index)

## We kick off our server
if __name__ == '__main__':
    web.run_app(app)