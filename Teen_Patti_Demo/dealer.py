# This file creates the virtual dealer who will deal the cards to the dealer according to the pack number


# Import Statements

import numpy as np
import pandas as pd
import random  ## Imported for calling the shuffle function
from card_maker import one_pack,two_pack  ## Imported for calling the cards for different packs


def dealCards(num_players, num_packs=1):  ## num_players : number of players playing in the room, num_packs : number of packs user wants the dealer to use
    
    # Creating the player cards list to keep record of each player's cards which is initialised as [[],[],[],.....n(being the number of players)]
    
    player_cards = []
    for i in range(num_players):
        player_cards.append([])

    
    cards = one_pack()  ## Calling the pack of cards for the dealer

    random.shuffle(cards)  ## Shuffling the cards

    for i in range(num_players):  ## Number of cards for each player
        temp_str = ""
        for j in range(0,3):  ## One by one card for each player as done by dealer in real life
            if(j == 0 or j ==1):
                temp_str = temp_str+cards[0]+" "
            else:
                temp_str+= cards[0] 
            cards.pop(0)
        player_cards[i].append(temp_str)

    return player_cards  ## Returing cards of all players for finding who won


def checkCards(num_players):  ## Testing function to test dealCards

    player_cards = dealCards(num_players)

    for i in range(num_players):  ## Printing Cards Of all players
        print("Player "+str(i+1), player_cards[i])


checkCards(3)  ## Checking checkCards function



