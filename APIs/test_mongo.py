from pymongo import MongoClient

dataBase = "TeenPatti"  
room_collection = "roomDetails"
playerQueue = "playerQueue"
activeMembers= "activeMembers"
rid = "Testing"
new_user = ['MeiMei', '1000', 'Testing']

array = []

# with MongoClient() as client:
#     msg_collection = client[dataBase][playerQueue] 
#     msg_collection.update_one({"roomId":rid}, {"$push":{"queue": new_user}})

playerRoomNames = []

# with MongoClient() as client:
#     msg_collection = client[dataBase][activeMembers].find({"roomId" :"aqfXnvc-KstfxBjdk" })
#     for document in msg_collection:
#         playerRoomNames = document

with MongoClient() as client:
    msg_collection = client[dataBase][activeMembers].find({"roomId" :"aCAoWHm-ubFAKxHaU" })
    print(msg_collection)
    for document in msg_collection:
        print("aa")
        print(document)

# print(playerRoomNames)
