import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
  Navigate
} from "react-router-dom";
import axios from 'axios';
import io from 'socket.io-client';

import StartScreen from "./StartScreen";
import Game from "./Game/Game";

const socket = io.connect('http://localhost:4000');

function App() {

  const [name, setName] = useState("")
  const [stack, setStack] = useState(0)
  const [gameURL, setGameURL] = useState("")
  let navigate = useNavigate()

  const getDetails = async (user_name, user_stack) => {
    // console.log(user_name, stack);
    await setName(user_name)
    await setStack(user_stack)
    console.log(user_name, user_stack);
    console.log(name, stack);
  }

  useEffect(() => {
    if (name != "" && stack != 0){
      getGameURL()
    }
  }, [name, stack])

  const getGameURL = () => {
    axios.post("http://localhost:8000/createMember&Room", "", {params: {
      name, stack
    }})
    .then(response => {
      setGameURL(response.data.data)
      
      console.log("redirecting", name, stack);
      navigate("/games/"+response.data.data, {state: { name, stack }})
    })
    .catch(err => console.log(err))
  }

  useEffect(() => {
    socket.on("connected", (data) => {
        console.log("connected");
    })

    return () => {
      console.log("disconnect");
      socket.off('connect');
    }
}, [socket])

  return (
    <div className="App max-h-screen">
        <Routes>
          <Route path="/" 
            element={
              gameURL == "" ?
              <StartScreen getDetails={getDetails} /> :
              <h1>{gameURL}</h1>} 
            />
          <Route path="games/:url" element={<Game socket={socket} />} />
        </Routes>
    </div>
  );
}

export default App;
