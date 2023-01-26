import axios from 'axios';
import React, { useState } from 'react';
import ReactLoading from "react-loading"

import PlayerRequestEdit from './Components/PlayerRequestEdit';
import "./style.css"

const OptionMenu = ({setShowOptionMenu, setSeatDeniedPlayer, playerSeat, sideShowRequest, seatRequests, roomId, getRoundDetails, updateRequestList, socket, getMembers, setSeatRequests, isRoomLead, hasGameStarted, setHasGameStarted, setShowPlayerWonPopup, setPlayerWonMessage}) => {

    const [selectedTab, setSelectedTab] = useState('players')
    const [showPlayer, setShowPlayer] = useState(false)
    const [approvePlayerData, setApprovePlayerData] = useState({})
    const [stack, setStack] = useState(0)
    const [showLoader, setShowLoader] = useState(false)

    const denySeat = (name => {
        setShowLoader(true)
        socket.emit("allowPlayer", {
                    name,
                    stack: 0,
                    decision: "Deny",
                    roomId: roomId,
                    seatnum: -1
                }, (data) => {
                    setShowLoader(false)
                    updateRequestList()
                    getMembers()
                    setSeatRequests(items => items.filter(req => req.name != approvePlayerData.name))
                    setShowPlayer(false)
            })
    })

    const approveSeat = () => {
        setShowLoader(true)
        socket.emit("allowPlayer", {
                    name: approvePlayerData.name,
                    stack: stack,
                    decision: "Allow",
                    roomId: approvePlayerData.roomId,
                    seatnum: approvePlayerData.seatNum
                }, (data) => {
                    setShowLoader(false)
                    updateRequestList()
                    getMembers()
                    setSeatRequests(items => items.filter(req => req.name != approvePlayerData.name))
                    setShowPlayer(false)
            })
    }

    
    return (
        <div className='bg-[#212120] h-screen' >
        <div className='bg-[#212120] text-white m-auto max-w-[520px] md:max-w-[890px] lg:max-w-[85%]' >
            <div className='h-20 border-b-8 border-[#919767] pr-10 pl-2' >
                <div className='h-full grid grid-cols-4 uppercase mr-10 text-sm pt-3' >
                    <p className='options ' 
                        onClick={() => {
                            setSelectedTab(setShowOptionMenu(false))
                        }}
                    >« Back</p>
                    <p className={`options ${selectedTab == 'players' ? 'bg-[#919767]': ''}`}
                        onClick={() => {
                            setSelectedTab("players")
                        }}
                    >Players</p>
                    <p className={`options ${selectedTab == 'game' ? 'bg-[#919767]': ''}`}
                        onClick={() => {
                            setSelectedTab("game")
                        }}
                    >Game</p>
                    <p className={`options ${selectedTab == 'preferences' ? 'bg-[#919767]': ''}`}
                        onClick={() => {
                            setSelectedTab("preferences")
                        }}
                    >Preferences</p>
                </div>
            </div>
            </div>



            {selectedTab == 'players' && !showPlayer &&
                <div className='p-2 text-white m-auto mt-2 max-w-[520px] md:max-w-[890px] lg:max-w-[85%]' > 
                    
                    {seatRequests.map((req, i) => {
                        return (
                            <div key={i} className="border-2 rounded-lg p-4 mt-2" >
                                <p className='text-lg font-bold' >{req.name}</p>
                                <p>Requested Seat {req.seatNum}</p>
                                <div className='mt-4' >
                                    <button
                                        disabled={hasGameStarted}
                                        onClick={e => {
                                            setShowPlayer(true)
                                            setStack(req.stack)
                                            setApprovePlayerData(req)
                                        }} 
                                        className={`px-4 py-2 rounded-lg border-2 border-green-600 text-green-400 uppercase font-bold ${hasGameStarted ? "opacity-60": ""}`} >
                                            Approve
                                    </button>
                                    <button className='px-4 py-2 ml-2 rounded-lg border-2 border-red-600 text-red-400 uppercase font-bold'
                                        onClick={e => denySeat(req.name)}
                                    >
                                        Deny
                                    </button>
                                </div>
                            </div>
                        )
                    })}
                </div>
            }

            {isRoomLead && selectedTab == 'players' && showPlayer && (
                
                <div className='p-4 max-w-[520px] md:max-w-[890px] lg:max-w-[85%] md:m-auto text-white md:mt-4' > 
                    { showLoader && <div className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10' >
                        <ReactLoading type="spin" color="#efefef" width={150} />
                    </div>}
                    <p className='text-3xl font-bold' >{approvePlayerData.name}</p>
                    <p className='mt-12 md:text-xl' >Player's Stack</p>
                    <input type="number"
                     className='h-12 px-4 text-lg mt-2 w-full bg-transparent border-2 border-white/60 rounded-lg md:w-5/12 md:block'
                     value={stack}
                     onChange={e => setStack(e.target.value)}
                    />

                    <button 
                        onClick={e => approveSeat()}
                        className='uppercase mt-8 h-16 rounded-lg border-2 border-green-600 text-green-500 font-bold w-full md:w-5/12 ' >
                        Approve player
                    </button>
                    <button 
                    onClick={e => denySeat(approvePlayerData.name)}
                    className='uppercase mt-2 h-16 rounded-lg border-2 border-red-600 text-red-500 font-bold w-full md:w-5/12 md:ml-8 ' >
                        Deny player
                    </button>
                    
                </div>
            )
            }
        </div>
    );
};

export default OptionMenu;
