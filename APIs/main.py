# Import Statements

from msilib.schema import Error
from operator import index
from urllib import response
import random  ## Required for finding random element from the list 
import requests
from requests import get,post
from pymongo import MongoClient  ## Pymongo for connecting databases
from fastapi import FastAPI, status  ## FastAPI imports, status for checking the status of the API
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  ## Gives us the BaseModel of the API for POST request
from helper_functions import get_random_string  ## Getting random string
import numpy as np  ## to check null values
import random  ## Imported for calling the shuffle function
from generating_winning_seq import check_winner  ## This function will help us determine the winner of the round


# Database and Collection Instantiation

dataBase = "TeenPatti"  ## Database connected via MongoClient
roomDetails = "roomDetails"  ## Collections connected via MongoClient
activeMembers = "activeMembers"  ## Collections connected via MongoClient
playerQueue = "playerQueue"  ## Collections connected via MongoClient
roundDetails = "roundDetails"  ## Collections connected via MongoClient
base_url = "mongodb+srv://admin:admin@clusterteen.aoenx9t.mongodb.net/"  ## Base url for all endpoints


# FastApi app Initialisation

app = FastAPI()  ## name of the app is 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoint : status :: checking status of the API

@app.get("/status/")
def get_status():
    return {"status": "running"}


# API endpoint : getRoomscoys :: getting all rooms ids

@app.get("/getRoomscoys/")
def get_rooms():

    ls_roomsId = []  ## Stores all the room ids present in the database
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][roomDetails]
        distinct_channel_list = msg_collection.find()
        for document in distinct_channel_list:
            ls_roomsId.append(document['roomId'])

    return ({"Status": "Success", "data":ls_roomsId})


@app.get("/getMembers")
def get_members(roomId):

    members = {}
    with MongoClient(base_url) as client:
        member_collection = client[dataBase][activeMembers].find({"roomId": roomId})
        for member in member_collection:
            members[member["playerSeatNum"]] = {"name": member['playerName'], "stack": member["playerStack"]}
            
    return members

    

# API endpoint : createMember&Room :: creating new player and room along with rest of details required in the database

@app.post("/createMember&Room/")
async def create_member_room(name, stack):

    ls_roomsId = get_rooms()["data"]
    room_id = ""
    counter = 0
    while(room_id in ls_roomsId == False or counter ==0):
        first = get_random_string(15)  ## first string of length 15
        second = get_random_string(15)  ## second string of length 15
        room_id = first+"-"+second  ## final room id
        print(room_id)
        counter+=1
    
    mydict = {"members":[name], "roomId": room_id, "roomLeader": name}

    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][roomDetails]
        msg_collection.insert_one(mydict)
    
        mydict = {"playerName": name,"roomId": room_id,"playerStatus": "Online", "playerRole":"Owner", "playerStack": stack,  "playerMove": "", "playerSeatNum": 1, "playerApproval": "True",  "playerCards": "", "playerPack": "False" }
    
        msg_collection = client[dataBase][activeMembers]
        msg_collection.insert_one(mydict)
    
    return({"Status":"Success", "Message":"New room and player has been created", "data":room_id})


# API endpoint : createmember :: creating new player, this is the player joining preexisting room

@app.post("/createMember/")
async def create_member(name, stack, roomId):
    playerRoomNames = []  ## collecting names of the players present in the room
    
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][roomDetails].find({"roomId" :roomId })
        for document in msg_collection:
            playerRoomNames = document
    if(len(playerRoomNames)!=0):
        playerRoomNames = playerRoomNames['members']
    
    
    playerQueueNames = []  ## collecting names of the players present in the queue for that room
    with MongoClient(base_url) as client:
            msg_collection = client[dataBase][playerQueue].find({"roomId" :roomId })
            for document in msg_collection:
                playerQueueNames = document
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
                with MongoClient(base_url) as client:
                    msg_collection = client[dataBase][playerQueue] 
                    msg_collection.update_one({"roomId":roomId}, {"$push":{"queue": {"name" : name, "stack": stack,"roomId": roomId, "seatNum":-1}}})  ## Updating queue in the appropriate collection
                    return ({"Status":"Success", "Message": "New member has been added to the playerqueue"})
            elif(name in playerQueueNames):
                return({"Status":"Fail", "Message": "Name exists in queue, pick a different name"})
            elif(name in playerRoomNames):
                return({"Status":"Fail", "Message": "Name exists in room, pick a different name"})
            else:
                return({"Status":"Fail", "Message": "Something wrong happened"})
        
        else:
            with MongoClient(base_url) as client:
                msg_collection = client[dataBase][playerQueue] 
                msg_collection.insert_one({"queue" : [{"name" : name, "stack": stack,"roomId": roomId, "seatNum":-1}], "roomId":roomId})  ## Adding a new collection for particular roomid
                return ({"Status":"Success", "Message":"New player has been created and new queue has been added to the playerqueue"})
    else:
        return({"Status":"Fail", "Message": "Room doesn't exist"})
    

# API endpoint : checkQueue :: Only owner can use this to check the queue 

@app.get("/checkQueue/")
def check_Queue(roomId):
    ls_temp = []
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][playerQueue].find({"roomId" :roomId })
        for document in msg_collection:
                ls_temp = document['queue']
    
    return ls_temp

@app.get("/isRoomLead")
def is_room_lead(name, roomId):
    with MongoClient(base_url) as client:
        room_rec = client[dataBase][roomDetails].find({"roomId" :roomId })
        for doc in room_rec:
            if doc["roomLeader"] == name:
                return True
    return False


@app.post("/requestSeat")
def request_seat(name, seatNum, roomId):
    with MongoClient(base_url) as client:
        room_rec = client[dataBase][playerQueue].find({"roomId" :roomId})
        for room in room_rec:
            update_index = None
            for i, player in enumerate(room["queue"]):
                if player["name"] == name:
                    update_index = i
                    break

            print("update index", update_index)
            client[dataBase][playerQueue].update_one(
                    {"roomId": roomId},
                    {
                        "$set" : {"queue."+str(update_index)+".seatNum": seatNum}
                    }
                )

            return "seat number updated"
                    


# API endpoint : allowPlayer :: Only owner can use this to allow players into table

@app.put("/allowPlayer/")
def allowPlayer(name,stack,decision,roomId):  ## We get queue from checkQueue

    id = ""
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][playerQueue].find({"roomId" :roomId })
        for document in msg_collection:
                ls_temp = document['queue']
                id = document['_id']
        queue = ls_temp
    
        if(decision == "Allow"):  
            for i in range(len(queue)):   ## If player exists, we go for createPlayer
                if(name == queue[i]["name"]):
                    if(len(queue) ==1):
                        client[dataBase][playerQueue].delete_one(
                            {"_id":id}
                        )
                        mydict = {"playerName": name,"roomId": roomId,"playerStatus": "Online", "playerRole":"Player", "playerStack": stack,  "playerMove": "", "playerSeatNum": -1, "playerApproval": "True",  "playerCards": "", "playerPack": "False" }
                        client[dataBase][activeMembers].insert_one(
                            mydict
                        )
                        client[dataBase][roomDetails].update_one(
                            {"roomId":roomId}, {"$push":{"members": name}}
                        )
                    else:
                        client[dataBase][playerQueue].update_one(
                        {"_id" : id},
                        {"$pull" : {"queue":{"name":name}}}
                        )
                        mydict = {"playerName": name,"roomId": roomId,"playerStatus": "Online", "playerRole":"Player", "playerStack": stack,  "playerMove": "", "playerSeatNum": -1, "playerApproval": "True",  "playerCards": "", "playerPack": "False" }
                        client[dataBase][activeMembers].insert_one(
                            mydict
                        )
                        client[dataBase][roomDetails].update_one(
                            {"roomId":roomId}, {"$push":{"members": name}}
                        )
                    return ({"Status":"Success", "Message": "Player has been added to activeMembers"})
        else:
             if(len(queue) ==1):
                        client[dataBase][playerQueue].delete_one(
                            {"_id":id}
                        )
             else:
                client[dataBase][playerQueue].update_one(
                    {"_id" : id},
                    {"$pull" : {"queue":{"name":name}}}
            )
            
        return ({"Status":"Fail", "Message": "Player doesn't exist in the queue"})

# API endpoint : assignSeat :: This api will assign the seat to the player just added to the room

@app.put("/assignSeat/")
def assignSeat(name, seatnum, roomId): 
    id = ""
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })
        for document in msg_collection:
                if(document["playerName"] == name):
                    id = document['_id']
        client[dataBase][activeMembers].update_one(
            {"_id":id}, {"$set":{"playerSeatNum": int(seatnum)}}
        )

    return ({"Status":"Success", "Message": "Player seat number has been changed"})


# API endpoint : playerExit :: This api will remove player from the room and activemember

@app.put("/playerExit/")
def playerExit(name, roomId):  
    id = ""
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })
        for document in msg_collection:
                if(document["playerName"] == name):
                    id = document['_id']
        client[dataBase][roomDetails].update_one(
            {"roomId" : roomId},
            {"$pull" : {"members":name}}
            )
            
        client[dataBase][activeMembers].delete_one(
                        {"_id":id}
                    )
    return ({"Status":"Success", "Message": "Player has been exited"})


# API endpoint : playerAway :: This api will change player's status to Away

@app.put("/playerAway/")
def playerAway(name, roomId):
    id = ""
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })
        stack = 0
        for document in msg_collection:
            if(document["playerName"] == name):
                stack = document['playerStack']
                id = document['_id']
        client[dataBase][activeMembers].update_one(
                        {"_id":id},
                        {"$set":{"playerStatus":"Away"}}
        )
        client[dataBase][activeMembers].update_one(
                        {"_id":id},
                        {"$set":{"playerSeatNum":-1}}
        )  
        msg_collection = client[dataBase][playerQueue] 
        msg_collection.update_one({"roomId":roomId}, {"$push":{"queue": {"name" : name, "stack": stack,"roomId": roomId}}})  ## Updating queue in the appropriate collection
    return ({"Status":"Success", "Message": "Player status has been changed to Away and returned to player queue"})


# API endpoint : playerBack :: This api will change player's status to Online

@app.put("/playerBack/")
def playerBack(name, roomId):
    id = ""
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })
        for document in msg_collection:
                if(document["playerName"] == name):
                    id = document['_id']
        client[dataBase][activeMembers].update_one(
                        {"_id":id},
                        {"$set":{"playerStatus":"Online"}}
        )
    return ({"Status":"Success", "Message": "Player status has been changed to Online"})


# API endpoint : startRound :: This api will start a new round for the players to play

@app.post("/startFirstRound/")
def startFirstRound(roomId, starting_board=10):  ## starts round and assigns card to players who are online and their seat number is assigned 
    ls_curr_id = []  ## contains id of all the players who are online and their seat number is assigned 
    ls_curr_names = []  ## contains names of the players who are online and their seat is assigned
    ls_curr_cards = []  ## contains cards of the players who are online and their seat is assigned
    ls_total_id = []  ## contains id of the all players
    ls_total_seatnum = []  ##contains seat number of the all players
    ls_total_names = []  ## contains names of all players
    ls_curr_stack = []  ## contains stack of players who are online and their seat is assigned
    ls_curr_seatnum = []  ## contains seat number of players who are online and their seat is assigned
    current_dealer_name = ""  ## contains name of the player with lowest seat number
    current_player = ""  ## will contain the number of player seating next to dealer, will start the game.
    current_player_seatnum = 11
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })

        for document in msg_collection:
            if(document["playerStatus"] == "Online" and document["playerSeatNum"] != -1):
                ls_curr_id.append(document["_id"])
                ls_curr_names.append(document["playerName"])
                ls_curr_stack.append(document["playerStack"])
                ls_curr_seatnum.append(document["playerSeatNum"])
            ls_total_seatnum.append(document["playerSeatNum"])
            ls_total_names.append(document["playerName"])
            ls_total_id.append(document["_id"])

        if(len(ls_curr_id) == 0):
            return({"Status":"Fail", "Message": "Noone is playing"})
        elif(len(ls_curr_id) == 1):
            return({"Status":"Fail", "Message": "Only one player is playing"})
        else:
            temp = ls_curr_seatnum.copy()
            temp.sort()
            current_dealer_name = ls_curr_names[ls_curr_seatnum.index(temp[0])]
            current_player = ls_curr_names[ls_curr_seatnum.index(temp[1])]
            current_player_seatnum = temp[1]

            for i in ls_curr_id:
               pass
            ls = []
            card_names = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]  ## All card names in a list
            card_types = ["Sp","He","Di","Cl"]  ## All card types in a list

            for i in range(len(card_names)):  ## Creating all card permutations
                for j in range(len(card_types)):
                    ls.append(card_names[i]+"-"+card_types[j])  ## List ls has all cards in it


            random.shuffle(ls)  ## Shuffling the deck of cards
            for i in range(len(ls_curr_id)):  ## Number of cards for each player
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
        seatnum_index = temp.index(current_player_seatnum)
        temp_array2 = temp[seatnum_index:]
        for i in range(len(temp[:seatnum_index])):
            temp_array2.append(temp[i])
        for i in range(len(ls_curr_names)):
            temp_array1.append(starting_board)
            temp_array.append("No")
            ls_curr_stack[i] = float(ls_curr_stack[i])-float(starting_board)


        mydict = {"roomId":roomId,  ##  Data Schema for the round details
        "currentPlayerDecision":"-", "currentBoard":starting_board, "currentDealer": current_dealer_name, "currentGameType":"Normal", "current_player":current_player,"current_player_seatnum":current_player_seatnum,
        "currentPlayerCardSeen": temp_array,"currentPlayerId":ls_curr_id, "currentPlayerCards": ls_curr_cards, "currentPlayerNames":ls_curr_names, "currentPlayerPack": temp_array, "currentPlayerSeatNum":ls_curr_seatnum,
        "currentPot":float(starting_board)*len(ls_curr_names), "roundStarted": "Yes","currentPlayerRotation":temp_array2, "totalPlayerNames": ls_total_names, "totalPlayerSeatNum":ls_total_seatnum, "totalPlayerId": ls_total_id, "fullShowPossible": False,
        "sideShowPossible":False, "currentPlayerBoard": temp_array1, "currentPlayerStack": ls_curr_stack, "game_board": starting_board, "player_won":""}

        msg_collection1 = client[dataBase][roundDetails]
        msg_collection1.insert_one(mydict)
            
    return({"Status":"Success", "Message": "Players have been assigned their cards"})


# API endpoint : getRoundInfo :: This api will get the getRoundInfo move for frontend

@app.get("/getRoundInfo/")
def getRoundInfo(roomId):
    
    mydict = {}

    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][roundDetails].find({"roomId" :roomId})
        print("msg collect", msg_collection)
        mydict = None
        for document in msg_collection:
            mydict = document
        
    if not mydict:
        return {}

    del mydict['_id']
    del mydict['currentPlayerId']
    del mydict['totalPlayerId']

    return(mydict)  ## returns all the data from roundDetails for that room


# API endpoint : updateMove :: This api will update the database depending on the currentPlayer's move

@app.post("/updateMove/")
def updateMove(roomId, name, move, amount = 0, playerseat = -22):
    print("update move called")
    try:
        with MongoClient(base_url) as client:
            msg_collection = client[dataBase][roundDetails].find({"roomId" :roomId })
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

            
            for document in msg_collection:
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

           ## Checking for full show possibility
            if(full_show == False):
                if(len(current_player_rotation) == 2):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"fullShowPossible": True}}) 
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"sideShowPossible": False}}) 
                    full_show = True  

            ## Will Contain the code for all the moves played by the current user
            if(move == "SeeCards"):
                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerCardSeen.{index}": "Yes"}})
                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerBoard.{index}": current_board*2}})

                if(side_show == False):
                    c = 1
                    print(current_player_pack, players_card_seen)
                    for i in range(len(players_card_seen)):
                        if(current_player_pack[i] == "No" and players_card_seen[i] == "Yes"):
                            c+=1          
                    print("card seen",c, len(current_player_rotation))
                    if(c >= len(current_player_rotation)):
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"sideShowPossible": True}})      
                return(player_Cards[index])
            
            elif(move == "Pack" ):
                if(len(current_player_rotation)<=2):
                    current_player_rotation.remove(current_player_seat_num)
                    winner_seatnum = current_player_rotation[0]
                    winner  = player_names[players_seat_num.index(winner_seatnum)]
                    # Changing player_won name 
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"player_won": winner}})
                    return({"Status":"Success", "Message": f"{winner} is the winner"})
                elif(current_player == player_names[index] and len(current_player_rotation)>1):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(current_player_seat_num)}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerPack.{index}": "Yes"}})
                    index1 = players_seat_num.index(current_player_rotation[1])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                    return({"Status":"Success", "Message": f"{current_player} has been packed"})
                elif(current_player != player_names[index] and len(current_player_rotation)>1):
                    # index1 = players_seat_num[player_names.index(name)]
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(players_seat_num[player_names.index(name)])}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerPack.{player_names.index(name)}": "Yes"}})
                    return({"Status":"Success", "Message": f"{player_names[index]} has been packed"})
                

                if(len(current_player_rotation)-1 == 2):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"fullShowPossible": True}})

            elif(move == "Check" and current_player == name):
                if((float(players_stack[index]) - 2*float(current_board) < 0 and players_card_seen[index] == "Yes") or (float(players_stack[index]) - float(current_board) < 0 and players_card_seen[index] == "No") ):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerPack.{index}": "Yes"}})
                    if(current_player == player_names[index] and len(current_player_rotation)>1):
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(current_player_seat_num)}})
                        index1 = players_seat_num.index(current_player_rotation[1])
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                        return({"Status":"Success", "Message": f"{current_player} has been packed"})
                    elif(current_player != player_names[index] and len(current_player_rotation)>1):
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                        index2 = player_names.index(current_player)
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(players_seat_num[index2])}})
                        index1 = players_seat_num.index(current_player_rotation[1])
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                        return({"Status":"Success", "Message": f"{current_player} has been packed"})
                    elif(current_player != player_names[index] and len(current_player_rotation)<=1):
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"player_won": winner}})
                        return({"Status":"Success", "Message": f"{current_player} is the winner"})
                elif(float(players_stack[index]) - 2*float(current_board) >= 0 and players_card_seen[index] == "Yes"):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - 2*float(current_board)}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+2*float(current_board)}})
                    index1 = players_seat_num.index(current_player_rotation[1])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                    new_rotation = []
                    for i in range(1, len(current_player_rotation),1):
                        new_rotation.append(current_player_rotation[i])
                    new_rotation.append(current_player_rotation[0])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPlayerRotation": new_rotation}})
                    return({"Status":"Success", "Message": "Board *2 was deducted"})
                elif(float(players_stack[index]) - float(current_board) >= 0 and players_card_seen[index] == "No"):
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - float(current_board)}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+float(current_board)}})          
                    index1 = players_seat_num.index(current_player_rotation[1])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                    new_rotation = []
                    for i in range(1, len(current_player_rotation),1):
                        new_rotation.append(current_player_rotation[i])
                    new_rotation.append(current_player_rotation[0])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPlayerRotation": new_rotation}})
                    return({"Status":"Success", "Message": "Board was deducted"}) 
            elif(move  == 'Raise' and current_player == name):
                if(float(players_stack[index])-float(amount)>=0):
                    if(players_card_seen[index] == "Yes"):
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - float(amount)}})
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+float(amount)}})  
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentBoard": float(amount)/2}})
                        
                    else:
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - float(amount)}})
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+float(amount)}})  
                        client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentBoard": float(amount)}}) 

                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                    index1 = players_seat_num.index(current_player_rotation[1])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                    new_rotation = []
                    for i in range(1, len(current_player_rotation),1):
                        new_rotation.append(current_player_rotation[i])
                    new_rotation.append(current_player_rotation[0])
                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPlayerRotation": new_rotation}})

                    return({"Status":"Success", "Message": "Board has been raised"})
                else:
                    return ({"Status":"Failure", "Message": "This move is not possible as the player has low funds"})
            elif(move == "SideShow" and current_player == name):
                if(side_show == False):
                    return({"Status":"Failure", "Message": "Side Show is not available at the moment"})
                else:
                    temp = current_player_rotation.copy()
                    print(temp)
                    temp.reverse()
                    print(temp)
                    temp.pop()
                    print(temp)
                    playerseat = int(playerseat)
                    print(type(playerseat), type(temp[0]), playerseat, temp)
                    if(len(temp) ==1):
                        return({"Status":"Failure", "Message": "Only full show is possible"})
                    elif(len(temp) <=1):
                        return({"Status":"Failure", "Message": "Side Show is not possible, only 1 player remaining"})
                    else:
                        if(playerseat in temp):
                            index231 = current_player_name.index(name)
                            client[dataBase][roundDetails].update_one({"roomId": roomId }, {"$set": {f"currentPlayerStack.{index231}": float(players_stack[index231]) - float(current_board) * 2 }})
                            client[dataBase][roundDetails].update_one({"roomId": roomId }, {"$set": {f"currentPot": float(current_pot) + float(current_board) * 2 }})
                            
                            myindex = players_seat_num.index(current_player_seat_num)
                            opponentindex = players_seat_num.index(playerseat)
                            winner  = check_winner([player_names[myindex], player_names[opponentindex] ], [player_cards[myindex],player_cards[opponentindex]])
                            if(winner[0] == player_names[myindex]):
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(players_seat_num[opponentindex])}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerPack.{opponentindex}": "Yes"}})
                                return({"Status":"Success", "Message": f"{player_names[opponentindex]} has been packed"})
                            elif(winner[0] == player_names[opponentindex]):
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player_seatnum": current_player_rotation[1]}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$pull" : {"currentPlayerRotation":(current_player_seat_num)}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerPack.{index}": "Yes"}})
                                index1 = players_seat_num.index(current_player_rotation[1])
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"current_player": player_names[index1]}})
                                return({"Status":"Success", "Message": f"{current_player} has been packed, {player_names[opponentindex]} has won the side show"})
                        else:
                            return({"Status":"Failure", "Message": "Side Show is not possiblefor this player"})


            elif(move == "FullShow" and current_player == name):
                print("full show called", current_player, name)
                try:
                    if(full_show == True):
                        if(players_card_seen[index] == "Yes"):
                            if(float(players_stack[index]) - float(current_board)*2 >=0):
                                ## cut money from player stack, add to pot , full show, declare winner, transfer pot money
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - float(current_board)*2}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+float(current_board)*2}}) 
                                my_cards = player_cards[index]
                                opponent_index = -1
                                for i in range(len(current_player_rotation)):
                                    if(current_player_rotation[i] != players_seat_num[index]):
                                        opponent_index = players_seat_num.index(current_player_rotation[i])
                                opponent_cards = player_cards[opponent_index]
                                winner  = check_winner([player_names[index], player_names[opponent_index] ], [my_cards,opponent_cards])
                                if(winner[0] == player_names[index]):
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) + float(current_pot)+ float(current_board)*2}})
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": 0}}) 
                                else:
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{opponent_index}": float(players_stack[opponent_index]) + float(current_pot)+ float(current_board)*2}})
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": 0}}) 
                                
                                msg_collection11 = client[dataBase][roundDetails].find({"roomId" :roomId })
                                for i in msg_collection11:
                                    players_stack = i['currentPlayerStack']

                                for i in range(len(player_names)):
                                    client[dataBase][activeMembers].update_one({"roomId" :roomId, "playerName":player_names[i]}, {"$set":{"playerStack":str(players_stack[i])}})
                                
                                for i in range(len(player_names)):
                                    client[dataBase][activeMembers].update_one({"roomId" :roomId, "playerName":player_names[i]}, {"$set":{"playerSeatNum":int(players_seat_num[i])}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"player_won": winner[0]}})
                                print({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                                return({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                                                                
                            else:
                                print({"Status":"Failure", "Message": "Dont have enough money"})
                                return({"Status":"Failure", "Message": "Dont have enough money"})   
                        elif(players_card_seen[index] == "No"):
                            if(float(players_stack[index]) - float(current_board) >=0):
                                ## cut money from player stack, add to pot , full show, declare winner, transfer pot money
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) - float(current_board)}})
                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": float(current_pot)+float(current_board)}}) 
                                my_cards = player_cards[index]
                                opponent_index = -1
                                for i in range(len(current_player_rotation)):
                                    if(current_player_rotation[i] != players_seat_num[index]):
                                        opponent_index = players_seat_num.index(current_player_rotation[i])
                                opponent_cards = player_cards[opponent_index]
                                winner  = check_winner([player_names[index], player_names[opponent_index] ], [my_cards,opponent_cards])
                                if(winner[0] == player_names[index]):
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[index]) + float(current_pot)+ float(current_board)}})
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": 0}}) 
                                else:
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerStack.{index}": float(players_stack[opponent_index]) + float(current_pot)+ float(current_board)}})
                                    client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPot": 0}}) 

                                msg_collection11 = client[dataBase][roundDetails].find({"roomId" :roomId })
                                for i in msg_collection11:
                                    players_stack = i['currentPlayerStack']
                                
                                for i in range(len(player_names)):
                                    client[dataBase][activeMembers].update_one({"roomId" :roomId, "playerName":player_names[i]}, {"$set":{"playerStack":str(players_stack[i])}})
                                
                                for i in range(len(player_names)):
                                    client[dataBase][activeMembers].update_one({"roomId" :roomId, "playerName":player_names[i]}, {"$set":{"playerSeatNum":int(players_seat_num[i])}})

                                client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"player_won": winner[0]}})
                                print({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                                return({"Status":"Success", "Message": f"{winner[0]} wins, by {winner[1]}"})
                            else:
                                print({"Status":"Failure", "Message": "Dont have enough money"})
                                return({"Status":"Failure", "Message": "Dont have enough money"})   
                        else:            
                            print({"Status":"Failure", "Message": "Something went wrong"})
                            return({"Status":"Failure", "Message": "Something went wrong"})
                    else:
                        print({"Status":"Failure", "Message": "Full Show not possible"})
                        return({"Status":"Failure", "Message": "Full Show not possible"})

                except Error as e:
                    print("Error", e)
            else:
                return ({"Status":"Failure", "Message": "This move doesn't exist"})

        
    except Error as e:
            print("outer e", e)

# API endpoint : refreshRound :: This api will allow to check and update pot details for each game

@app.put("/refreshRound/")
def refreshRound(roomId):
    ls_curr_id = []  ## contains id of all the players who are online and their seat number is assigned 
    ls_curr_names = []  ## contains names of the players who are online and their seat is assigned
    ls_curr_cards = []  ## contains cards of the players who are online and their seat is assigned
    ls_total_id = []  ## contains id of the all players
    ls_total_seatnum = []  ##contains seat number of the all players
    ls_total_names = []  ## contains names of all players
    ls_curr_stack = []  ## contains stack of players who are online and their seat is assigned
    ls_curr_seatnum = []  ## contains seat number of players who are online and their seat is assigned
    current_dealer_name = ""  ## contains name of the player with lowest seat number
    current_player = ""  ## will contain the number of player seating next to dealer, will start the game.
    current_player_seatnum = 11
    starting_board = -1
    with MongoClient(base_url) as client:
        msg_collection = client[dataBase][activeMembers].find({"roomId" :roomId })

        for document in msg_collection:
            if(document["playerStatus"] == "Online" and document["playerSeatNum"] != -1):
                ls_curr_id.append(document["_id"])
                ls_curr_names.append(document["playerName"])
                ls_curr_stack.append(document["playerStack"])
                ls_curr_seatnum.append(document["playerSeatNum"])
            ls_total_seatnum.append(document["playerSeatNum"])
            ls_total_names.append(document["playerName"])
            ls_total_id.append(document["_id"])

        if(len(ls_curr_id) == 0):
            return({"Status":"Fail", "Message": "Noone is playing"})
        elif(len(ls_curr_id) == 1):
            return({"Status":"Fail", "Message": "Only one player is playing"})
        else:
            msg_collection = client[dataBase][roundDetails].find({"roomId" :roomId })
            for document in msg_collection:
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

            for i in ls_curr_id:
               pass
            ls = []
            card_names = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]  ## All card names in a list
            card_types = ["Sp","He","Di","Cl"]  ## All card types in a list

            for i in range(len(card_names)):  ## Creating all card permutations
                for j in range(len(card_types)):
                    ls.append(card_names[i]+"-"+card_types[j])  ## List ls has all cards in it


            random.shuffle(ls)  ## Shuffling the deck of cards
            for i in range(len(ls_curr_id)):  ## Number of cards for each player
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
        seatnum_index = temp.index(current_player_seatnum)
        temp_array2 = temp[seatnum_index:]
        for i in range(len(temp[:seatnum_index])):
            temp_array2.append(temp[i])
        for i in range(len(ls_curr_names)):
            temp_array1.append(starting_board)
            temp_array.append("No")
            ls_curr_stack[i] = float(ls_curr_stack[i])-float(starting_board)

        mydict = {"roomId":roomId,  ##  Data Schema for the round details
        "currentPlayerDecision":"-", "currentBoard":starting_board, "currentDealer": current_dealer_name, "currentGameType":"Normal", "current_player":current_player,"current_player_seatnum":current_player_seatnum,
        "currentPlayerCardSeen": temp_array,"currentPlayerId":ls_curr_id, "currentPlayerCards": ls_curr_cards, "currentPlayerNames":ls_curr_names, "currentPlayerPack": temp_array, "currentPlayerSeatNum":ls_curr_seatnum,
        "currentPot":float(starting_board)*len(ls_curr_names), "roundStarted": "Yes","currentPlayerRotation":temp_array2, "totalPlayerNames": ls_total_names, "totalPlayerSeatNum":ls_total_seatnum, "totalPlayerId": ls_total_id, "fullShowPossible": False,
        "sideShowPossible":False, "currentPlayerBoard": temp_array1, "currentPlayerStack": ls_curr_stack, "game_board":starting_board, "player_won":""}

        msg = client[dataBase][roundDetails].find({"roomId":roomId})
        old_id = ""
        for doc in msg:
            old_id = doc["_id"]

        client[dataBase][roundDetails].delete_one(
                        {"_id":old_id}
                    )
        

        msg_collection1 = client[dataBase][roundDetails]
        msg_collection1.insert_one(mydict)
            
    return({"Status":"Success", "Message": "Players have been re-assigned their cards"})


# API endpoint : transferOwnerShip :: This api trasnfer ownership of the game to the player mentioned

@app.put("/transferOwnerShip/")
def transferOwnerShip(roomId, name, owner):
    pass


# @app.post("/fillwitharray/")
# def fillwitharray(roomId):  
#     with MongoClient(base_url) as client:

#         client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{"currentPlayerCardSeen": ["No","No","No","No","No","No" ]}})


# @app.post("/changearray/")
# def changearray(roomId, index):  
#     with MongoClient(base_url) as client:
#         client[dataBase][roundDetails].update_one({"roomId" :roomId}, {"$set":{f"currentPlayerCardSeen.{index}": "Yes"}})

