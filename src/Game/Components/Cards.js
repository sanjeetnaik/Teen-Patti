import React from 'react';
import backCard from "../../assets/cards/1.png"

const Cards = ({roundDetails, playerIndex}) => {
    if(playerIndex != -1 && roundDetails.currentPlayerCardSeen[playerIndex] == "Yes"){
        const playerCards = roundDetails.currentPlayerCards[playerIndex].split(" ")
        console.log("player cards", playerCards);
        return (
            <div className='w-40 h-20 absolute grid grid-cols-3 gap-2 top-3/4 left-1/2 -translate-x-1/2 -translate-y-1/2' >
                {playerCards.map(card => {
                    console.log("../../assets/cards/"+card+".png");
                    return (
                        <img src={require("../../assets/cards/"+card+".png")} className="w-full" />
                    )
                })}
               
            </div>
        );
    }
    else {
        return (
            <div className='w-40 h-20 absolute grid grid-cols-3 gap-2 top-3/4 left-1/2 -translate-x-1/2 -translate-y-1/2' >
                <img src={backCard} className="w-full" />
                <img src={backCard} className="w-full" />
                <img src={backCard} className="w-full" />
            </div>
        );
    }
};

export default Cards;