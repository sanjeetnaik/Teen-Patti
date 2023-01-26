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


function App() {

  const [name, setName] = useState("")
  const [stack, setStack] = useState(0)
  const [gameURL, setGameURL] = useState("")
  const [showLoading, setShowLoading] = useState(false)
  const navigate = useNavigate()

  const [socket, setSocket] = useState(io("http://127.0.0.1:8080/", {cors: {
      origin: "http://localhost:8080",
      methods: ["GET", "POST"],
      transports: ['websocket', 'polling'],
      credentials: true
  },
  allowEIO3: true}));

  useEffect(() => {
    if(gameURL != ""){
      console.log("redirecting to /games/" + gameURL);
      navigate("/games/"+gameURL, {state: { name, stack }})
    }
  }, [gameURL])

  useEffect(() => {
    socket.on("connect", (data) => {
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
          <Route path="/" element={<StartScreen setName={setName} setStack={setStack} setGameURL={setGameURL} socket={socket} showLoading={showLoading} />} />
          <Route path="games/:url" element={<Game socket={socket} />} />
        </Routes>
    </div>
  );
}

export default App;
