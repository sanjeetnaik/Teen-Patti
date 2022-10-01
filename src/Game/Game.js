import React, { useEffect, useState } from 'react';

import tableMobile from "../assets/table-mobile.png"
import table from "../assets/table.png"
import Seat from './Components/Seat';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import CancelSeatRequest from './Components/CancelSeatRequest';
import RequestIndicator from './Components/RequestIndicator';
import OptionMenu from './OptionMenu';
import StartGameBtn from './Components/StartGameBtn';
import { useCookies } from 'react-cookie';
import RaiseAmountSlider from './Components/RaiseAmountSlider';
import Cards from './Components/Cards';
import useWindowDimensions  from "../helper/windowDimensions"
import TopBar from './Components/TopBar';
import PopupMessage from './Components/PopupMessage';

const Game = ({socket}) => {

    const [playerSeat, setPlayerSeat] = useState(0)
    const [showPopup, setShowPopup] = useState(true)
    const [isRoomLead, setIsRoomLead] = useState(false)
    const [tempSeatNum, setTempSeatNum] = useState(0)
    const [seatWaiting, setSeatWating] = useState(false)
    const [isRequestWaiting, setIsRequestWaiting] = useState(false)
    const [seatRequests, setSeatRequests] = useState([])
    const [numRequestWaiting, setNumRequestWaiting] = useState(0)
    const [showOptionMenu, setShowOptionMenu] = useState(false)
    const [seatDeniedPlayer, setSeatDeniedPlayer] = useState('./.')
    const [showRedirectHome, setShowRedirectHome] = useState(false)
    const [hasGameStarted, setHasGameStarted] = useState(false)
    const [cookies, setCookie, removeCookie] = useCookies(['user']);
    const [playerCreated, setPlayerCreated] = useState(false)
    const [dataLoaded, setDataLoaded] = useState(false)
    const [showRaiseSlider, setShowRaiseSlider] = useState(false)
    const [bet, setBet] = useState(10)
    const [roundDetails, setRoundDetails] = useState({})
    const [isPlayerTurn, setIsPlayerTurn] = useState(false)
    const [reloadRoundInfo, setReloadRoundInfo] = useState(false)
    const [playerIndex, setPlayerIndex] = useState(-1)
    const [fullShow, setFullShow] = useState(false)
    const [showSeatRequestSentPopup, setShowSeatRequestSentPopup] = useState(false)
    const [playerWon, setPlayerWon] = useState("")
    const [playerWonMessage, setPlayerWonMessage] = useState("")
    const [showPlayerWonPopup, setShowPlayerWonPopup] = useState(false)
    const { height, width } = useWindowDimensions();
    const [playerAway, setPlayerAway] = useState(false)
    const [playerLeft, setPlayerLeft] = useState(false)
    const [sideShowRequest, setSideShowRequest] = useState({name: "", seat: -1})
    const [showSideShowRequestSentPopup, setShowSideShowRequestSentPopup] = useState(false)
    const [isReqPlayer, setIsReqPlayer] = useState(false)
    const [reqPlayerName, setReqPlayerName] = useState("-")
    const [sideShowResult, setSideShowResult] = useState("")
    const [ showSideShowResult, setShowSideShowResult] = useState(false)
    

    let location = useLocation()
    const [name, setName] = useState("")
    const [stack, setStack] = useState(0)
    const [players, setPlayers] = useState({})

    const roomId = location.pathname.split("/")[2]

    console.log(isReqPlayer, showSideShowRequestSentPopup );

    console.log(numRequestWaiting);
    const setRoomLeader = (user_name) => {
        console.log("room id", roomId, user_name);
        axios.get("http://localhost:8000/isRoomLead", {
            params: {
                name: user_name,
                roomId
            }
        })
        .then(res => {
            setIsRoomLead(res.data)
            if(res.data){setPlayerSeat(1)}
        })
    }

    useEffect(() => {

        (async () => {
        await getMembers()
        updateRequestList()
        
        if (location.state !== null){

            if(cookies.roomId !== roomId){
                removeCookie("roomId")
                removeCookie("name")
                removeCookie("stack")
                removeCookie("hasGameStarted")

                setName(location.state.name)
                setStack(location.state.stack)
                console.log("set room leaded", location.state.name);
                setRoomLeader(location.state.name)
                removeCookie("hasGameStarted")
                setPlayerCreated(true)
                setCookie("name", location.state.name, { path: '/' })
                setCookie("stack", location.state.stack, { path: '/' })
                setCookie("roomId", roomId, { path: '/' })
            }

            else {
                setName(cookies.name)
                setStack(cookies.stack)
                setPlayerCreated(true)
                var seat = Object.keys(players).find(key => players[key] === name)
                if (!(seat === undefined)){
                    setPlayerSeat(seat)
                    console.log("set seat", seat);
                }
                console.log("game start", cookies.hasGameStarted);
                if(cookies.hasGameStarted === "true"){
                    setHasGameStarted(true)
                    console.log("called from useeffect int");

                    getRoundDetails("called from useeffect")
                }
            }
            
            socket.emit("room_lead", 
                {
                    name: location.state.name,
                    seatNum:  1,
                    roomId
                }
            )
        }

        else if (cookies.roomId) {
            if(cookies.roomId === roomId){
                setName(cookies.name)
                setStack(cookies.stack)
                setPlayerCreated(true)
                var seat = Object.keys(players).find(key => players[key] === name)
                if (!(seat === undefined)){
                    setPlayerSeat(seat)
                    console.log("set seat", seat);
                }
                console.log("game start", cookies.hasGameStarted);
                if(cookies.hasGameStarted === "true"){
                    setHasGameStarted(true)
                    console.log("called from useeffect int");

                    getRoundDetails("called from useeffect")
                }

                socket.emit("player_joined", {
                    roomId
                })
            }

            else{
                removeCookie("roomId")
                removeCookie("name")
                removeCookie("stack")
                removeCookie("hasGameStarted")
            }
        }

        setDataLoaded(true)
        })()
    }
        
    , [])

    useEffect(() => {
        console.log("is room lead", isRoomLead);
    }, [isRoomLead])

    useEffect(() => {
        console.log("players: ", players)
    }, [players])

    useEffect(() => {
        socket.on("seat_request_recieved", (data) => {
            console.log("seat req received all broadcast");
            setIsRequestWaiting(true)
            updateRequestList()
        })

        socket.on("player_seat_denied", (data) => {
            console.log(data.name, "has been denied");
            console.log(name, "this is");
            setSeatDeniedPlayer(data.name)
        })
    
        socket.on("player_seat_req_cancelled", (data) => {
            updateRequestList()
        })
    
        socket.on("player_seat_approved", (data) => {
            console.log(data.name, "has been approved");
            getMembers()
            setSeatWating(false)
        })
    
        socket.on("player_game_started", (data) => {
            setHasGameStarted(true)
            setCookie("hasGameStarted", true, { path: '/' })
            setFullShow(false)
            // console.log("called from game start");
            // setReloadRoundInfo(val => !val)
            getRoundDetails("called from game start")
            console.log("game has started");
        })
    
        socket.on("player_update_move", (data) => {
            console.log("called from update move");
            // setReloadRoundInfo(val => !val)
            if(data.message.includes("win")){
                setPlayerWonMessage(data.message)
                setShowPlayerWonPopup(true)
                setTimeout(() => {
                    setHasGameStarted(false)
                    setShowPlayerWonPopup(false)
                }, 5000);
            }
            getRoundDetails("called from update move")
            // console.log("player moved");
            if(data.move == "FullShow"){
                setFullShow(true)
            }
        })

        socket.on("player_side_show_request", (data) => {
            recSideShow(data)
        })

        socket.on("player_player_left", (data) => {
            getMembers()
        })

        socket.on("player_sideshow_result", (data) => {
            setSideShowResult(data.message)
            setSideShowRequest(true)
            setTimeout(() => {
                setSideShowRequest(false)
            })

        })

        // socket.on("player_full_show", (data) => {
        //     setFullShow(true)
        // })

    }, [])

    const recSideShow = (data) => {
        console.log("side show req rec", data.reqPlayer, name, playerSeat);
        console.log("side show request received to", name);
        setShowSideShowRequestSentPopup(true)
        setSideShowRequest({
            name: data.name,
            seat: data.playerSeat,
            reqPlayer: data.reqPlayer,
            reqPlayerName: data.reqPlayerName
        })

        setTimeout(() => {
            setShowSideShowRequestSentPopup(false)
        }, 3000);

        setReqPlayerName(data.reqPlayerName)

        // if(data.reqPlayer == playerSeat){
        //     console.log("side show request received from", data.name);
        //     setIsReqPlayer(true)
        //     // setNumRequestWaiting(numRequestWaiting+1)
        // }
    }

    useEffect(() => {
        if (reqPlayerName == name){
            setIsReqPlayer(true)
        }
    }, [reqPlayerName])

    useEffect(() => {
        var seat = Object.keys(players).find(key => players[key]["name"] === name)
        if (!(seat === undefined)){
            setPlayerSeat(seat)
        }
    }, [players])

    const getRoundDetails = (text) => {
        axios.get("http://localhost:8000/getRoundInfo", {
            params: {roomId}
        }).then(res => {
            
            console.log(res.data);
            setRoundDetails(res.data)
            if(res.data !== {}){
                if(res.data.player_won !== ""){
                    setPlayerWon(res.data.player_won)
                }
                res.data.currentPlayerNames.forEach((p,i) => {
                    if (p == name){
                        console.log("player index is ",i);
                        setPlayerIndex(i)
                    }
                });
            }
            
        }).catch(err => console.log(err))
    }

    const getMembers = async () => {
        try {
            let res = await axios.get("http://localhost:8000/getMembers", {
                params: {roomId}
            })
            console.log("members",res.data);
            var seat = Object.keys(res.data).find(key => res.data[key] === name)
            if (!(seat === null)){
                setPlayerSeat(seat)
            }
            setPlayers(res.data)
        }
        catch (e){
            console.log(e);
        }
    }


    // useEffect(() => {
    // }, [name])

    const updateRequestList = () => {
        axios.get("http://localhost:8000/checkQueue", {
            params: {roomId}
        })
        .then(res => {
            console.log("player queue");
            console.log(res.data);
            setSeatRequests(res.data)
            setNumRequestWaiting(res.data.length) 
        })
    }
    
    const getSeatHandler = (seatNum) => {
        // console.log("room lead", isRoomLead);
        if((playerSeat === 0 || playerSeat === undefined)){
            setTempSeatNum(seatNum)
            requestSeat(seatNum)
        }
        // setSeatTaken(true)
    }

    const createMember = () => {
        axios.post("http://localhost:8000/createMember", "", {
            params: {
                name,
                stack,
                roomId
            }   
        }).then(
            res => {
                console.log(res);
                setShowPopup(false)
            }
        ).catch(
            err => console.log(err)
        )
        setCookie("name", name, { path: '/' })
        setCookie("stack", stack, { path: '/' })
        setCookie("roomId", roomId, { path: '/' })
        setPlayerCreated(true)
    }

    const requestSeat = (seatNum) => {
        if(playerSeat === undefined || playerSeat === 0){
        
        setSeatWating(true)

        axios.post("http://localhost:8000/requestSeat", "", {
            params: {
                name,
                seatNum,
                roomId
            }
        }).then(res => {
            console.log("seat request sent");
            socket.emit("seat_request", {
                name,
                seatNum,
                stack,
                roomId
            })
        }).catch(err => console.log(err))
    }
    }

    useEffect(() => {
        if(hasGameStarted){
            getRoundDetails("call from updated")
        }
    }, [reloadRoundInfo])

    const findPlayerTurn = () => {
        if(roundDetails.current_player_seatnum == playerSeat){
            setIsPlayerTurn(true)
            console.log(name, playerSeat,roundDetails.current_player_seatnum, "is player turn set ", true);
        }
        else{
            setIsPlayerTurn(false)
            console.log(name, playerSeat,roundDetails.current_player_seatnum, "is player turn set ", false);
        }
    }

    useEffect(() => {
        findPlayerTurn()
    }, [roundDetails])

    useEffect(() => {
        if(seatDeniedPlayer == name){
            setShowRedirectHome(true)
        }

    }, [seatDeniedPlayer])

    const handleMove = (move, amount=0) => {
        setIsPlayerTurn(false)
        
        axios.post("http://localhost:8000/updateMove", "", {
            params: {
                roomId,
                name,
                move,
                amount
            }
        }).then(res => {
            console.log("update data",res.data);
            console.log("message", res.data.Message);
            getRoundDetails("called from handle", move)
            
            if(move == "FullShow"){
                setFullShow(true)
            }   
            if (res.data.Message.includes("win")){
                setPlayerWonMessage(res.data.Message)
                setShowPlayerWonPopup(true)
                setTimeout(() => {
                    setHasGameStarted(false)
                    setShowPlayerWonPopup(false)
                }, 5000);
            }
            socket.emit("update_move", {
                roomId,
                message: res.data.Message,
                move
            })
            
        })
    }

    const cancelSeat = (() => {
        axios.put("http://localhost:8000/allowPlayer", "", {
            params: {
                name,
                stack:0,
                decision:"Deny",
                roomId,
                seatNum:-1
            }
        }).then(res => {
            console.log(res);
            updateRequestList()
            setSeatWating(false)
            socket.emit("seat_req_cancelled", {
                name,
                roomId
            })
        }).catch(err => console.log(err))
    })

    const handleSideShowRequest = () => {
        console.log("side show req");
        
        const reqPlayerIndex = roundDetails.currentPlayerRotation.length - 1        
        const reqPlayer = roundDetails.currentPlayerRotation[reqPlayerIndex]
        console.log(roundDetails.currentPlayerSeatNum);
        const ind = roundDetails.currentPlayerSeatNum.indexOf(reqPlayer)
        const reqPlayerName = roundDetails.currentPlayerNames[ind]

        console.log("send from seat", playerSeat, "send req to ", reqPlayer);
        socket.emit("side_show_request", {
            roomId,
            name,
            playerSeat,
            reqPlayer,
            reqPlayerName
        })

        // console.log(roundDetails.currentPlayerRotation);
    }

    // console.log(numRequestWaiting, isRoomLead);

    const approveSideShow = () => {
        axios.post("http://localhost:8000/updateMove", "", {
            params: {
                roomId,
                name: sideShowRequest.name,
                move:"SideShow",
                playerseat: playerSeat,
                amount:0
            }
        }).then(res => {
            console.log("update data",res.data);
            console.log("message", res.data.Message);
            getRoundDetails("called from handle sideshow")
            setIsReqPlayer(false)
            setShowSideShowRequestSentPopup(false)
            setSideShowRequest(res.data.Message)
            setShowSideShowResult(true)

            setTimeout(() => {
                setShowSideShowResult(false)
            }, 3000);

            socket.emit("sideshow_result", {
                roomId,
                message: res.data.Message
            })
            
            
            socket.emit("update_move", {
                roomId,
                message: res.data.Message,
                move:"SideShow"
            })
            
        }).catch(err => {
            console.log("errors", err);
        })
    }

    const denySideShow = () => {
        setShowSideShowRequestSentPopup(false)
        setIsReqPlayer(false)

        axios.post("http://localhost:8000/updateMove", "", {
            params: {
                roomId,
                name:sideShowRequest.reqPlayerName,
                move:"Check",
                seat:playerSeat,
                amount:0
            }
        }).then(res => {
            console.log("update data",res.data);
            console.log("message", res.data.Message);
            getRoundDetails("called from handle")
            
            socket.emit("update_move", {
                roomId,
                message: res.data.Message,
                move:"Check"
            })
            
        })
    }


    if (!showOptionMenu) {
        return (
            <div className='bg-[#212120] relative h-screen max-h-screen' >
                <div className='absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-full max-w-[520px] md:max-w-[890px] md:h-full  bg-bg bg-no-repeat bg-cover' >
                
                <div className="h-full w-full p-2 relative py-4" >
                    <div className='h-full' >
                        <TopBar name={name} roomId={roomId} sideShowRequest={sideShowRequest} setShowRedirectHome={setShowRedirectHome} getMembers={getMembers}  socket={socket} numRequestWaiting={numRequestWaiting} hasGameStarted={hasGameStarted} isRoomLead={isRoomLead} setShowOptionMenu={setShowOptionMenu} playerAway={playerAway} setPlayerAway={setPlayerAway} setPlayerLeft={setPlayerLeft} />

                        
                        <div className="relative h-full" >
                            <img className="relative -top-4 max-w-[90%] max-h-[80vh] w-full object-contain m-auto md:hidden " src={tableMobile} />
                            <img className="relative -top-4 max-h-[100vh] object-contain m-auto w-11/12 hidden md:block " src={table} />
                            <div className="" >
                                {Array.apply(0, Array(10)).map(function (x, i) {
                                        
                                        return <Seat key={i} name={name} stack={stack} 
                                        roundDetails={roundDetails} seatNum={i+1} 
                                        playerSeat={playerSeat} getSeatHandler={getSeatHandler} 
                                        players={players} hasGameStarted={hasGameStarted} 
                                        fullShow={fullShow} seatWaiting={seatWaiting}
                                        setShowSeatRequestSentPopup={setShowSeatRequestSentPopup} 
                                        />
                                        
                                    })}
                            </div>
                        </div> 
                        

                        {dataLoaded && isRoomLead && Object.keys(players).length < 2 && <div className="w-9/12 p-2 text-sm bg-white rounded-lg absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" >
                            <div className='text-[#3EA66C]' > <p className="font-bold" >Waiting Players.</p> Click below to copy the link and send to your friends.</div>
                            <p className='mt-2 rounded-lg p-1 text-xs border-2 break-all' > {"http://localhost:3000"+window.location.pathname}</p>
                        </div>}

                        {/* {hasGameStarted && <Cards roundDetails={roundDetails} name={name} playerIndex={playerIndex} />} */}

                        {dataLoaded && !playerCreated && (
                                <div className={`w-64 rounded-lg z-10 px-4 py-6 bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 ${showPopup ? "" : "hidden"}`}  >
                                    <p className='text-sm text-black/70' >Your nickname</p>
                                    <input className='text-lg text-black/70 border-2 w-full my-2 h-12 p-2 rounded-lg'
                                        value = {name}
                                        onChange = {e => setName(e.target.value)}
                                        disabled={isRoomLead}
                                    />
                                    <p className='text-sm text-black/70 mt-2' >Your intended stack</p>
                                    <input className='text-lg text-black/70 border-2 w-full my-2 h-12 p-2 rounded-lg'
                                        value = {stack}
                                        onChange = {e => setStack(e.target.value)} 
                                    />
                                    <button className="font-bold bg-[#3EA66C] text-white text-lg w-full h-12 mt-4 rounded-lg"  
                                        onClick={e => {
                                            // setShowPopup(false)
                                            createMember()
                                            // assignSeat()
                                        }}
                                    >SAVE</button>
                                </div>
                            )
                        }

                        {showSeatRequestSentPopup && 
                            <div className='w-11/12 rounded-lg z-10 px-4 py-2 bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' >
                                <p className='bg-[#EFEEEE] text-lg text-center p-2 rounded-md text-black' >Your requested this seat. Wait for owner approval</p>
                                <button 
                                    onClick={e => setShowSeatRequestSentPopup(false)}
                                    className='border-[#939393] border-2 mt-4 text-[#939393] font-bold w-16 block rounded-lg ml-auto p-2' >OK</button>
                            </div>
                        }

                        {showPlayerWonPopup  && 
                            <PopupMessage message={playerWonMessage} />
                        }

                        {showSideShowResult  && 
                            <PopupMessage message={sideShowResult} />
                        }

                        {(showSideShowRequestSentPopup || isReqPlayer)  &&
                            <div className='w-64 rounded-lg z-10 px-4 py-6 bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' >
                                <p className='font-semibold text-lg text-center text-black' >{ isReqPlayer ? `You have recieved side show request from ${sideShowRequest.name}` : `${sideShowRequest.name} sent Side Show Request to ${sideShowRequest.reqPlayerName}`}</p>
                                
                                {isReqPlayer && 
                                <div className='flex' >
                                    <button 
                                        onClick={e => approveSideShow()}
                                        className='border-green-500 border-2 mt-4 text-green-600 font-bold block rounded-lg ml-4 p-2' >Approve
                                    </button>
                                    <button 
                                        onClick={e => denySideShow()}
                                        className='border-red-500 border-2 mt-4 text-red-600 font-bold block rounded-lg ml-auto mr-4 p-2' >Deny
                                    </button>
                                </div>
                                }
                            
                            </div>
                        }


                        <div className={`w-64 text-red-600 text-center rounded-lg z-10 px-4 py-6 bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 font-bold ${showRedirectHome ? "" : "hidden"}`} >
                            <p>Your request has been denied</p>
                            <button 

                            onClick={() => {
                                window.location = '/'
                            }}
                            className='border-2 border-red-600 text-red-600 w-20 m-auto rounded-lg mt-4 p-1' >OK</button>
                        </div>
                        
                        <div className='relative flex' >
                            {!hasGameStarted && <div className='relative mt-2 left-2 h-12 w-3/12 bg-black/40 text-white/80 text-center'>
                                ad box
                            </div>}

                            <div className='absolute right-2' >
                                {isRoomLead && Object.keys(players).length > 1 && !hasGameStarted && <StartGameBtn roomId={roomId} setHasGameStarted={setHasGameStarted} setFullShow={setFullShow} socket={socket} roundDetails={roundDetails} getRoundDetails={getRoundDetails} />}
                            </div>
                        </div>
                    </div> 

                    
                </div>

                {/* <div className='absolute right-2' >
                        {seatWaiting && <CancelSeatRequest cancelSeat={cancelSeat} />}
                </div> */}

                {/* {!hasGameStarted && <div className='absolute left-2 h-12 w-3/12 bg-black/40 text-white/80 text-center'>
                    ad box
                </div>} */}

                {hasGameStarted && showRaiseSlider && <RaiseAmountSlider stack={stack} bet={bet} setShowRaiseSlider={setShowRaiseSlider} handleMove={handleMove} hasGameStarted={hasGameStarted} roundDetails={roundDetails} name={name} />}

                {hasGameStarted && !showRaiseSlider && !(playerIndex != -1 && roundDetails.currentPlayerCardSeen[playerIndex] == "Yes") && <button 
                onClick={e => handleMove("SeeCards")} 
                className={`game-btn absolute -translate-y-full right-2 p-1`} >
                        See Cards
                </button>}

                {hasGameStarted && !showRaiseSlider && roundDetails.fullShowPossible == true && <button 
                onClick={e => {
                    handleMove("FullShow")
                }} 
                className={`game-btn absolute -translate-y-full left-2 p-1  ${isPlayerTurn ? "" : "opacity-40"}`} disabled={!isPlayerTurn} >
                        Full Show
                </button>}

                {hasGameStarted && !showRaiseSlider && roundDetails.fullShowPossible == false && roundDetails.sideShowPossible == true && <button 
                onClick={e => {
                    // handleMove("FullShow")
                    handleSideShowRequest()

                }} 
                className={`game-btn absolute -translate-y-full left-2 p-1  ${isPlayerTurn ? "" : "opacity-40"}`} disabled={!isPlayerTurn} >
                        Side Show
                </button>}

                {hasGameStarted && !showRaiseSlider && <div className='grid grid-cols-4 w-full gap-4 mt-2 px-2' >
 
                    <button className={`game-btn col-start-2 ${isPlayerTurn ? "" : "opacity-40"}`} disabled={!isPlayerTurn} onClick={e => setShowRaiseSlider(true)} >
                        Raise   
                    </button>

                    <div
                        onClick={e => handleMove("Check")} 
                        className={`game-btn col-start-3 ${isPlayerTurn ? "" : "opacity-40"}`} disabled={!isPlayerTurn} >
                        Check
                    </div>
                    
                    <div
                        onClick={e => handleMove("Pack")} 
                        className={`game-btn col-start-4 !text-red-500 !border-red-700 ${isPlayerTurn ? "" : "opacity-40"}`} disabled={!isPlayerTurn} >
                        Fold
                    </div>

                </div>}
                

                </div>
            </div>
        );
    }
    else {
        return (
            <OptionMenu setShowOptionMenu={setShowOptionMenu} playerSeat={playerSeat} sideShowRequest={sideShowRequest} seatRequests={seatRequests} roomId={roomId} getRoundDetails={getRoundDetails} setPlayerWonMessage={setPlayerWonMessage} setShowPlayerWonPopup={setShowPlayerWonPopup} setHasGameStarted={setHasGameStarted} updateRequestList={updateRequestList} socket={socket} getMembers={getMembers} setSeatRequests={setSeatRequests} isRoomLead={isRoomLead} hasGameStarted={hasGameStarted} />
        )
    }
};

export default Game;