import React, { useEffect, useState } from 'react';
import "./slider.scss"

const RaiseAmountSlider = ({stack, bet, setShowRaiseSlider, handleMove, hasGameStarted, roundDetails, name}) => {

    const [value, setValue] = useState(bet+10)
    const [playerIndex, setPlayerIndex] = useState(-1)

    useEffect(e => {
        roundDetails.currentPlayerNames.htmlForEach((p,i) => {
            if (p == name){
                console.log("player index is ",i);
                setPlayerIndex(i)
            }
        });
    })


    return (
        <div className='w-full relative md:absolute md:bottom-8 pl-2'>
            <div className='absolute py-2 px-6 rounded-lg -top-16 left-2 text-[#F2F2F2] bg-[#333232]' >
                <p className='text-sm' >Amount</p>
                <p className='text-2xl font-bold text-center'>{value}</p>
            </div>
            <div id="slider" className='w-full' >
                <div id="raise-amount-slider" className='mr-auto'>
                    <input type="radio" name="raise-amount" onChange={e => setValue(bet+10)} id="1" value="1" defaultChecked />
                    <label htmlFor="1" data-raise-amount="+$10"></label>
                    <input type="radio" name="raise-amount" onChange={e => setValue(bet+20)} id="2" value="2" />
                    <label htmlFor="2" data-raise-amount="+$20"></label>
                    <input type="radio" name="raise-amount" onChange={e => setValue(bet+30)} id="3" value="3" />
                    <label htmlFor="3" data-raise-amount="+$30"></label>
                    <input type="radio" name="raise-amount" id="4" onChange={e => setValue(bet+50)} value="4" />
                    <label htmlFor="4" data-raise-amount="+$50"></label>
                    <input type="radio" name="raise-amount" onChange={e => {
                            console.log(roundDetails.currentPlayerStack, playerIndex);
                            setValue(hasGameStarted ? roundDetails.currentPlayerStack[playerIndex] : stack)
                        
                        }} id="5" value="5" />
                    <label htmlFor="5" data-raise-amount="All In"></label>
                    <div id="raise-amount-pos"></div>
                </div>

                <div className='absolute right-2 md:right-8 w-5/12 flex justify-end' >
                    <button 
                    onClick={
                        e => {
                                console.log("raise amount", value);
                                handleMove("Raise", value)
                                setShowRaiseSlider(false)
                            }
                        }
                    className='border-2 border-[#F2F2F2] text-[#F2F2F2] rounded-md p-2 md:p-4 font-bold mr-2 md:mr-8' >
                        Raise
                    </button>
                    <button 
                    onClick={e => setShowRaiseSlider(false)}
                    className='border-2 border-[#F2F2F2] text-[#F2F2F2] rounded-md p-2 md:p-4 font-bold'>
                        Back
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RaiseAmountSlider;