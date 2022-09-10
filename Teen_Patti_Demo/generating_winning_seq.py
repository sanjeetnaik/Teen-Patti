# This file will help generate the winning sequence for the game. Manually entering the sequence is the current solution.


# Import Statements

import numpy as np
import pandas as pd
import math
import string
import random


# Laying Down Cards and their Suits

cds = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw","Ac"]
suits = ["Sp","He","Di","Cl"]


# Generating all P&C for Pure Sequence 

ls_pure_seq = []
combos = [[0,1,2],[0,2,1],[1,2,0],[1,0,2],[2,1,0],[2,0,1]]

for i in range(0, len(cds)-2,1):
    for j in range(len(suits)):
        ls_pure_seq.append(cds[i]+"-"+suits[j]+" "+cds[i+1]+"-"+suits[j]+" "+cds[i+2]+"-"+suits[j])
        ls_pure_seq.append(cds[i]+"-"+suits[j]+" "+cds[i+2]+"-"+suits[j]+" "+cds[i+1]+"-"+suits[j])        
        ls_pure_seq.append(cds[i+1]+"-"+suits[j]+" "+cds[i+2]+"-"+suits[j]+" "+cds[i]+"-"+suits[j])        
        ls_pure_seq.append(cds[i+1]+"-"+suits[j]+" "+cds[i]+"-"+suits[j]+" "+cds[i+2]+"-"+suits[j])        
        ls_pure_seq.append(cds[i+2]+"-"+suits[j]+" "+cds[i+1]+"-"+suits[j]+" "+cds[i]+"-"+suits[j])        
        ls_pure_seq.append(cds[i+2]+"-"+suits[j]+" "+cds[i]+"-"+suits[j]+" "+cds[i+1]+"-"+suits[j]) 


# Generating all P&C for Sequence 

ls_seq = []
for i in range(len(cds)-2):
    f = cds[i]
    s = cds[i+1]
    t = cds[i+2]
    ls_seq.append(f+"-"+s+"-"+t)
    ls_seq.append(f+"-"+t+"-"+s)    
    ls_seq.append(t+"-"+s+"-"+f)    
    ls_seq.append(t+"-"+f+"-"+s)    
    ls_seq.append(s+"-"+f+"-"+t)    
    ls_seq.append(s+"-"+t+"-"+f) 


# This function helps checking if the cards is trio or not 

def check_tr(t_cds):  
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]  
    
    if(f==s==t): 
        return cds.index(f)
    else:
        return -1


# This function helps checking if the cards is sequence or not

def check_seq(t_cds): 
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]  
    s1 = temp[0].split("-")[1]
    s2 = temp[1].split("-")[1]  
    s3 = temp[2].split("-")[1] 
    combined = f+"-"+s+"-"+t
    
    if(combined in ls_seq):
        if((s1 == s2 == s3)):
            return (ls_pure_seq.index(t_cds), "pure")
        else:
            return (ls_seq.index(f+"-"+s+"-"+t), "seq")
    else:
        return -1


# This function helps checking if the cards is color or not

def check_colo(t_cds):
    temp = t_cds.split(" ")
    s1 = temp[0].split("-")[1]
    s2 = temp[1].split("-")[1]  
    s3 = temp[2].split("-")[1]
    index = suits.index(s1)
    high_index = get_hi(t_cds)
    if(s1 == s2 == s3):
        return (index, high_index)
    else:
        return -1


# This function helps checking if the cards is duo or not

def check_du(t_cds):  ## All testcases passed
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]  
    
    if(f == s and t !=s and t != f):
        return cds.index(f)
    elif(s == t and f != s and f != t):
        return cds.index(s)
    elif(t == f and s != f and s != t):
        return cds.index(t)
    else:
        return -1


# This function helps to give the highest card

def get_hi(t_cds):
    cds = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]
    fi = cds.index(f)
    si = cds.index(s)
    ti = cds.index(t)
    least = min([fi,si,ti])
    return(least)


# This function helps to give the second highest card

def get_sec_hi(t_cds): ## All testcases passed
    cds = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]
    fi = cds.index(f)
    si = cds.index(s)
    ti = cds.index(t)
    least = min([fi,si,ti])
    if(f == cds[least]):
        least = min([si,ti])
        return (least)
    elif(s == cds[least]):
        least = min([fi,ti])
        return (least)
    elif(t == cds[least]):
        least = min([fi,si])
        return (least)


# This function helps to give the third highest card

def get_thi_hi(t_cds):  ## All testcases passed
    cds = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]
    temp = t_cds.split(" ")
    f = temp[0].split("-")[0]
    s = temp[1].split("-")[0]  
    t = temp[2].split("-")[0]
    fi = cds.index(f)
    si = cds.index(s)
    ti = cds.index(t)
    highest = max([fi,si,ti])
    return (highest)


# This function helps checking for the rest of the situation condition

def others(t_cds):
    cds = ["Ac","Ki","Qu","Ja","Te","Ni","Ei","Se","Si","Fi","Fo","Th","Tw"]
    get_f = get_hi(t_cds)
    get_s = get_sec_hi(t_cds)
    get_t = get_thi_hi(t_cds)
    summ = int(get_f)*100+int(get_s)*10+int(get_t)
    return(summ)


# This part of the code will help determine the winner of the round 

ls_trio = []
lss_pure_seq = []
lss_seq = []
ls_color = []
ls_duo = []
ls_others = []

def check_winner(ls_names1, ls_cards1):   
    num_players = len(ls_names1)
    for i in range(num_players):
        current_cards = ls_cards1[i]
        if(check_tr(current_cards) != -1):
            ls_trio.append([current_cards, check_tr(current_cards)])
        elif(check_seq(current_cards) != -1):
            answer = check_seq(current_cards)
            if(answer[1] == "pure"):
                lss_pure_seq.append([current_cards, answer[0]])
            elif(answer[1] == "seq"):
                lss_seq.append([current_cards, answer[0]])
        elif(check_colo(current_cards) != -1):
            ls_color.append([current_cards,check_colo(current_cards)[0],check_colo(current_cards)[1]])
        elif(check_du(current_cards) != -1):
            ls_duo.append([current_cards,check_du(current_cards)])
        else:
            ls_others.append([current_cards,others(current_cards)])
    
    ls_trio.sort(key = lambda x: x[1])
    lss_pure_seq.sort(key = lambda x: x[1])
    lss_seq.sort(key = lambda x: x[1])
    ls_color.sort(key = lambda x: (x[1],x[2]))
    ls_duo.sort(key = lambda x: x[1])
    ls_others.sort(key = lambda x: x[1])
    
    
    if(len(ls_trio) != 0):
        return(ls_names1[ls_cards1.index(ls_trio[0][0])],"Trio")
    elif(len(lss_pure_seq)!= 0):
        return(ls_names1[ls_cards1.index(lss_pure_seq[0][0])],"Pure Sequence")
    elif(len(lss_seq) != 0):
        return(ls_names1[ls_cards1.index(lss_seq[0][0])], "Sequence")
    elif(len(ls_color) != 0):
        return(ls_names1[ls_cards1.index(ls_color[0][0])], "Color")
    elif(len(ls_duo) != 0):
        return(ls_names1[ls_cards1.index(ls_duo[0][0])], "Duo")
    else:
        return(ls_names1[ls_cards1.index(ls_others[0][0])], "Highest Card")    