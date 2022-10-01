import React, { useEffect, useState } from 'react';
import backCard from "../../assets/cards/1.png"

const getPosition = (seatNum) => {
    var position = ""
    if(seatNum == 1){
        position = "bottom-2 left-1/2 -translate-x-1/2"
    }
    else if (seatNum == 2){
        position = "top-[80%] -translate-y-1/2"
    }
    else if (seatNum == 3){
        position = "top-[65%] -translate-y-1/2"
    }
    else if (seatNum == 4){
        position = "top-[35%] -translate-y-1/2"
    }
    else if (seatNum == 5){
        position = "top-[20%] -translate-y-1/2"
    }
    else if (seatNum == 6){
        position = "top-2 left-1/2 -translate-x-1/2"
    }
    else if (seatNum == 7){
        position = "top-[20%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 8){
        position = "top-[35%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 9){
        position = "top-[65%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 10){
        position = "top-[80%] -translate-y-1/2 right-2"
    }

    return position
}

const Seat = ({name, seatNum, playerSeat, getSeatHandler, players, roundDetails, hasGameStarted, fullShow, seatWaiting, setShowSeatRequestSentPopup}) => {

    let position;
    let index
    
    if(playerSeat !== undefined){
        // console.log("new pos", seatNum, playerSeat, (seatNum - playerSeat)%10 + 1);
        let newpos = (seatNum - playerSeat)%10 + 1
        if (newpos <= 0){
            newpos += 10
        }
        position = getPosition(newpos)
    }
    else{
        position = getPosition(seatNum)
    }

    if(hasGameStarted && roundDetails.current_player_seatnum == seatNum && players[seatNum]){

        let playerCards
        if(roundDetails.currentPlayerCards){
            index = roundDetails.currentPlayerNames.findIndex((p,i) => {
                if(p == players[seatNum]["name"]){
                    return true
                }
            })

            playerCards = roundDetails.currentPlayerCards[index].split(" ")
        }

        console.log("sm",roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes")));

        return (
            <div className='' >
                { hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes")) ?
                
                    <div className={'absolute ' + position} >
                        <div className='flex relative  -translate-y-6  ' >
                            <img src={require("../../assets/cards/"+playerCards[0]+".png")} className={"w-10 -rotate-12 "} />
                            <img src={require("../../assets/cards/"+playerCards[1]+".png")} className={"w-10 -translate-x-2 -translate-y-1  "} />
                            <img src={require("../../assets/cards/"+playerCards[2]+".png")} className={"w-10 rotate-12 -translate-x-4  "} />
                        </div>
                    </div>
                : hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && 
                  <div className={'absolute ' + position} >
                        <div className='flex relative  -translate-y-6  ' >
                            <img src={backCard} className={"w-10 -rotate-12 "} />
                            <img src={backCard} className={"w-10 -translate-x-2 -translate-y-1  "} />
                            <img src={backCard} className={"w-10 rotate-12 -translate-x-4  "} />
                        </div>
                    </div>
                }
                <div className={"bg-[#333232] text-xs px-4 py-1 absolute w-4/12 rounded-lg text-white/90 scale-[105%] text-amber-500 shadow-md shadow-amber-500/70 " + position} >
                    <p className='text-white/80' >{players[seatNum] !== undefined && players[seatNum]["name"]  }</p>
                    <p className='font-bold' >{roundDetails.currentPlayerStack ? roundDetails.currentPlayerStack[index] : players[seatNum]["stack"]}</p>
                </div>
            </div>
            
        )
    }

    if(seatNum in players){
        let playerCards;
        if(roundDetails.currentPlayerNames){
            index = roundDetails.currentPlayerNames.findIndex((p,i) => {
                if(p == players[seatNum]["name"]){
                    return true
                }
            })
            playerCards = roundDetails.currentPlayerCards[index].split(" ")
        }
        // const playerCards = roundDetails.currentPlayerCards[index].split(" ")

        return (
            <div>
                {hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes"))  ?
                
                <div className={'absolute ' + position} >
                    <div className='flex relative  -translate-y-6  ' >
                            <img src={require("../../assets/cards/"+playerCards[0]+".png")} className={"w-10 -rotate-12 "} />
                            <img src={require("../../assets/cards/"+playerCards[1]+".png")} className={"w-10 -translate-x-2 -translate-y-1  "} />
                            <img src={require("../../assets/cards/"+playerCards[2]+".png")} className={"w-10 rotate-12 -translate-x-4  "} />
                    </div>
                </div>
             :  hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && <div className={'absolute ' + position} >
                    <div className='flex relative  -translate-y-6  ' >
                        <img src={backCard} className={"w-10 -rotate-12 "} />
                        <img src={backCard} className={"w-10 -translate-x-2 -translate-y-1  "} />
                        <img src={backCard} className={"w-10 rotate-12 -translate-x-4  "} />
                    </div>
                </div>
            }
                <div className={"bg-[#333232] z-10 text-xs px-4 py-1 absolute w-4/12 rounded-lg text-white/90 " + position} >
                    <p className='text-white/80' >{players[seatNum] !== undefined && players[seatNum]["name"]}</p>
                    <p className='font-bold' >{roundDetails.currentPlayerStack ? roundDetails.currentPlayerStack[index] : players[seatNum]["stack"]}</p>
                </div>
            </div>
        )
    }

    else if(!hasGameStarted)  {
        return (
            <>
            <button onClick={e => {
                    getSeatHandler(seatNum)
                    setShowSeatRequestSentPopup(true)
                }} 
                disabled={seatWaiting}
                className={'border-white/40 p-2 text-white/80 font-light absolute w-3/12 border-2 border-dotted rounded-lg ' + position}  >
                
                <p>{seatNum}</p>
                <p className='text-center' >SEAT</p> 
            </button>
            </>
        );
    }
};

export default Seat;