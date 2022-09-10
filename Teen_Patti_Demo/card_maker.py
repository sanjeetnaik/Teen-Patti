# This file will help create the number of cards depending on the number of decks the dealer wishes to have

# Different functions for different number of packs will be made as per dealer's request


# Import Statements

import pandas as pd
import numpy as np
import random  ## Imported for calling the shuffle function


# One Pack function : Creating and returning list of one card pack

def one_pack():
    ls = []
    card_names = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]  ## All card names in a list
    card_types = ["Sp","He","Di","Cl"]  ## All card types in a list

    for i in range(len(card_names)):  ## Creating all card permutations
        for j in range(len(card_types)):
            ls.append(card_names[i]+"-"+card_types[j])  ## List ls has all cards in it

    random.shuffle(ls)  ## Shuffling the deck of cards

    return ls


# Two Pack function : Creating and returning list of two card pack 

def two_pack():
    ls = one_pack()  ## Loading one pack
    ls2 = one_pack()  ## Loading the second pack

    for i in ls2:  ## Combining both the packs in ls
        ls.append(i)
    
    random.shuffle(ls)  ## Shuffling voth the packs

    return ls

one_pack()  ## Checking two_pack function