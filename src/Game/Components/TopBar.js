import React from 'react';
import MenuButton from "../../icons/menu"
import Sound from '../../assets/sound.png';
import RequestIndicator from './RequestIndicator';
import away from "../../assets/away.png"
import leave from "../../assets/leave.png"
import back from "../../assets/back.png"
import axios from 'axios';

const TopBar = ({name, roomId, socket, handleClearInterval, handleMove, setShowRedirectHomeMessage, isPlayerTurn, sideShowRequest, getMembers, setShowRedirectHome, numRequestWaiting, hasGameStarted, isRoomLead, setShowOptionMenu, playerAway, setPlayerAway, setPlayerLeft}) => {

    const handlePlayerAway = () => {
        handleClearInterval()
        console.log("player away");
        // axios.put("http://localhost:8000/playerAway", "", {
        //     params: {
        //         name,
        //         roomId
        //     }
        // }).then(() => {
        // }).catch(err => console.log(err))
        socket.emit("playerAway", {
            name,
            roomId
        }, (data) => {
            setPlayerAway(true)
            if(hasGameStarted && isPlayerTurn){
                handleMove("Pack")
            }
            getMembers()
        })
    }

    const handlePlayerBack = () => {
        // handleClearInterval()
        // axios.put("http://localhost:8000/playerBack", "", {
        //     params: {
        //         name,
        //         roomId
        //     }
        // }).then(() => {
        //     setPlayerAway(false)
        // }).catch(err => console.log(err))
        socket.emit("playerBack", {
            name,
            roomId
        }, (data) => {
            setPlayerAway(false)
        })
    }

    const handlePlayerLeft = () => {
        console.log("player left");

        handleClearInterval()
        socket.emit("playerExit", {
            name, 
            roomId
        }, (data) => {
            console.log(data);
            if(hasGameStarted && isPlayerTurn){
                handleMove("Pack")
            }
            setPlayerLeft(true)
            // getMembers()
            setShowRedirectHome(true)
            setShowRedirectHomeMessage("You have left the game")
            // socket.emit("player_left", {
            //     roomId
            // })
        })
        
    }

    return (
        <div className='px-4 py-2 flex md:block md:absolute md:top-[1rem] md:w-20 z-10'>
            {numRequestWaiting > 0 && isRoomLead && <RequestIndicator numRequestWaiting={numRequestWaiting} />}
            
            
            <MenuButton setShowOptionMenu={setShowOptionMenu} />
            
            <button onClick={handlePlayerLeft} className="block ml-4 w-8 h-10 cursor-pointer align-middle md:ml-2 md:mt-4 z-10" >
                <img  className=" " src={leave} />
            </button>
            
            {hasGameStarted &&
                     (playerAway ? <img onClick={handlePlayerBack} className="ml-2 cursor-pointer md:mt-4 w-8 h-full align-middle " src={back} />
                     : <img onClick={handlePlayerAway} className="ml-2 md:mt-4 cursor-pointer w-8 h-full align-middle " src={away} />)
            }
            <img className="absolute cursor-pointer right-5 inline-block md:mt-4" src={Sound} />
        </div>
    ); 
};

export default TopBar;