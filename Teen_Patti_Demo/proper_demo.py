# This file contains the proper demo run of the teen patti game


# Import Statements

import numpy as np
import pandas as pd
from temp_player_genrators import playerGen  ## Importing demo dummy user data for testing
from generating_winning_seq import check_winner  ## This function will help us determine the winner of the round



# Temporary Card Getter Code : For testing the rules, original one will include players, rooms and stack

def proper_demo(num_players): 
    playerData = playerGen(num_players)  ## Getting temporary user players data


    ls_uid = []  ## contains user uid of all players who havent packed yet
    ls_cards = []  ## contains user cards of all players who havent packed yet
    for i in range(len(playerData)):
        if(playerData[i]['playerpack'] == False):
            ls_uid.append(playerData[i]['playerUID'])
            ls_cards.append(playerData[i]['playerCards'][0])
    
    winner = check_winner(ls_uid, ls_cards)  ## Calling the function to determin the winner
    
    for i in range(len(ls_uid)):
        print(ls_uid[i], ls_cards[i] )
    # print(ls_cards)
    print("The winner UID number is : "+str(winner[0]),"Winner reason is : "+winner[1])  ## Printing the result to check


proper_demo(8)  ## Only for testing