GET : /status : checks the status of the API
Params : -
Returns : (String) [Status]

GET : /getRoomscoys : gets list of all existing rooms names (ex. sd
SDeSAC-KUtgVbIo) in the database
Params : -
Returns : (List) [(String) Status, (List) List of room names]

POST : /createMember&Room : creates a new member and creates a new room in the database
Params : (name [of new memeber], stack [of new memeber], ls_roomsId [of new memeber])
Returns : (String) [Status]

POST : /createMember : creates a new member and adds them to an existing room
Params : (name [of new memeber], stack [of new memeber], roomId [existing room])
Returns : (String) [Status]

GET : /checkQueue : checks the queue of allowing players in the game
Params : (roomId [existing room])
Returns : (List) List of players in the queue

PUT : /allowPlayer : allows the player in waiting queue inside the game
Params : (name [of new member] ,stack [of new member] ,decision [Allowed or not], roomId [existing room])
Retruns : (String) [Status]

PUT : /assignSeat : assigns the seat of the new player
Params : (name [of new member] , seatnum [chosen seat number] , roomId [existing room])
Returns : (String) [Status]

PUT : /playerExit : player exits the game
Params : (name [of player], roomId [existing room])
Returns : (String) [Status]

PUT : /playerAway : player away for this round
Params : (name [of player], roomId [existing room])
Returns : (String) [Status]

PUT : /playerBack : player back from being away
Params : (name [of player], roomId [existing room])
Returns : (String) [Status]

POST : /startFirstRound : used to start the first ever round for the newly found room
Params : (roomId [existing room] , starting_board [for this round] )
Returns : (String) [Status]

GET : /getRoundInfo : Gets all the round details for an existing room
Params : (String) roomId of existing room
Return : (Dict) JSON preview of all existing round details data

POST : /updateMove : updates move for the player
Params : (roomId [existing room] , name [of the player] , move [chosen by the player], amount = 0 [not required], playerseat = -22 [not required])
Returns : (String) [Status]

PUT : /refreshRound : refreshes the round details - after every new round
Params : (String) roomId of exsiting room
Returns : (String) [Status]


