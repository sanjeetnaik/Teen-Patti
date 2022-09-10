# This file will help generate players for testing out codes, till the real players are connected in the DB
# Here the players will have demo data, not related to the actual player data.

# Actual player data : {
#                           "playerUID": (str) [unique for each player, gotten from auth],
#                           "playerName" : (str) [name decided by the player when logging into the game]
#                           "playerRoom": (url) [url that helps them connect to the room],
#                           "playerStatus": (str) [whether the player is Online or Offline],
#                           "playerRole" : (str) [whether the player is a Room Leader or a Player],
#                           "playerStack" : (int) [player money in the game],
#                           "playerMove" : (str) [player move on the table (pack, raise, bet)]
#                           "playerSeatNum" : (int) [player seat number],
#                           "playerApproval" : (String) [playerhas been accepted in the room or not]
#                           "playerCards" : (List) [list of cards held by the user]
#                           "playerPack" : (boolean) [whether player is pack or not]
#                      }


# Import Statements

import numpy as np
import pandas as pd
import requests
import string
from dealer import dealCards  ## Importing this module to get dealCards()


# playerGenerator : helps generate random dummy players for testing the basic codes

def playerGen(num_players):

    # Hardcoding DB information
    
    uid = 10000
    name = "Dummy"
    room = "url"
    status = "online"
    role = "Temporary"
    stack = "100"
    move = ""
    approval = "True"
    playerpack = False

    cards = dealCards(num_players)
    players_data = []


    for i in range(1,num_players+1):

        data = {
                "playerUID": uid+i,  ## Get unique id for each player
                "playerName" : name,
                "playerRoom": room,
                "playerStatus": status,
                "playerRole" : role,
                "playerStack" : stack,
                "playerMove" : move,
                "playerSeatNum" : i,  ## Clockwise Seat Number
                "playerApproval": approval,
                "playerCards" : cards[i-1],  ## Cards for eack player
                "playerpack" : playerpack
            }

        players_data.append(data)

    return players_data


# playerGen(3)  ## Testing the playergen function