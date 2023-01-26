import React, { useEffect, useState } from 'react';
import backCard from "../../assets/cards/1.png"

const getPosition = (seatNum) => {
    var position = ""
    if(seatNum == 1){
        position = "bottom-2 left-1/2 md:top-[70%] md:left-[65%] -translate-x-1/2"
    }
    else if (seatNum == 2){
        position = "top-[80%] md:top-[75%] md:left-[30%] -translate-y-1/2"
    }
    else if (seatNum == 3){
        position = "top-[65%] md:top-[60%] md:left-[10%] -translate-y-1/2"
    }
    else if (seatNum == 4){
        position = "top-[35%] md:top-[40%] md:left-[5%] -translate-y-1/2"
    }
    else if (seatNum == 5){
        position = "top-[20%] md:top-[20%] md:left-[10%] -translate-y-1/2"
    }
    else if (seatNum == 6){
        position = "top-2 left-1/2 md:top-[3%] md:left-[36%] -translate-x-1/2 -translate-y-1/2"
    }
    else if (seatNum == 7){
        position = "top-[20%] md:top-[3%] md:left-[55%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 8){
        position = "top-[35%] md:top-[20%] md:left-[73%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 9){
        position = "top-[65%] md:top-[40%] md:left-[78%] -translate-y-1/2 right-2"
    }
    else if (seatNum == 10){
        position = "top-[80%] md:top-[60%] md:left-[73%] -translate-y-1/2 right-2"
    }

    return position
}

const Seat = ({name, seatNum, playerCreated, playerSeat, getSeatHandler, players, roundDetails, hasGameStarted, fullShow, isRoomLead, seatWaiting, setShowSeatRequestSentPopup}) => {

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

        // console.log("sm",roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes")));

        return (
            <div className='' >
                { hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes")) ?
                
                    <div className={'absolute ' + position} >
                        <div className='flex relative -translate-y-6  ' >
                            <img src={require("../../assets/cards/"+playerCards[0]+".png")} className={"w-10 -rotate-12 md:-translate-y-2"} />
                            <img src={require("../../assets/cards/"+playerCards[1]+".png")} className={"w-10 -translate-x-2 -translate-y-1 md:-translate-y-4"} />
                            <img src={require("../../assets/cards/"+playerCards[2]+".png")} className={"w-10 rotate-12 -translate-x-4 md:-translate-y-2"} />
                        </div>
                    </div>
                : hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && 
                  <div className={'absolute ' + position} >
                        <div className='flex relative -translate-y-6  ' >
                            <img src={backCard} className={"w-10 -rotate-12 md:-translate-y-2"} />
                            <img src={backCard} className={"w-10 -translate-x-2 -translate-y-1 md:-translate-y-4  "} />
                            <img src={backCard} className={"w-10 rotate-12 -translate-x-4 md:-translate-y-2"} />
                        </div>
                    </div>
                }
                <div className={"bg-[#333232] h-12 text-xs px-4 py-1 absolute w-4/12 md:w-2/12 rounded-lg text-white/90 scale-[105%] text-amber-500 shadow-md shadow-amber-500/70 " + position} >
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

            // console.log(index, roundDetails.currentPlayerCards);
            if(index != -1){
                playerCards = roundDetails.currentPlayerCards[index].split(" ")
             }
        }
        // const playerCards = roundDetails.currentPlayerCards[index].split(" ")

        return (
            <div>
                {hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && (fullShow || (playerSeat == seatNum && roundDetails.currentPlayerCardSeen[index] == "Yes"))  ?
                
                <div className={'absolute ' + position} >
                    <div className='flex relative  -translate-y-6  ' >
                            <img src={require("../../assets/cards/"+playerCards[0]+".png")} className={"w-10 -rotate-12 md:-translate-y-2"} />
                            <img src={require("../../assets/cards/"+playerCards[1]+".png")} className={"w-10 -translate-x-2 -translate-y-1 md:-translate-y-4"} />
                            <img src={require("../../assets/cards/"+playerCards[2]+".png")} className={"w-10 rotate-12 -translate-x-4 md:-translate-y-2"} />
                    </div>
                </div>
             :  hasGameStarted && roundDetails.currentPlayerPack && roundDetails.currentPlayerPack[index] == "No" && <div className={'absolute ' + position} >
                    <div className='flex relative  -translate-y-6  ' >
                        <img src={backCard} className={"w-10 -rotate-12 md:-translate-y-2"} />
                        <img src={backCard} className={"w-10 -translate-x-2 -translate-y-1 md:-translate-y-4"} />
                        <img src={backCard} className={"w-10 rotate-12 -translate-x-4 md:-translate-y-2"} />
                    </div>
                </div>
            }
                <div className={"bg-[#333232] h-12 z-10 text-xs px-4 py-1 absolute w-4/12 md:w-2/12 md:md:w-2/12 rounded-lg text-white/90 " + position} >
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
                    if (playerCreated && !isRoomLead){
                    getSeatHandler(seatNum)
                    setShowSeatRequestSentPopup(true)
                    }
                }} 
                disabled={seatWaiting}
                className={'border-white/40 p-2 h-16 text-white/80 font-light absolute w-4/12 md:w-2/12 border-2 border-dotted rounded-lg ' + position}  >
                
                <p>{seatNum}</p>
                <p className='text-center' >SEAT</p> 
            </button>
            </>
        );
    }
};

export default Seat;