import { useState } from "react";
import StartScreen from "./StartScreen";
import axios from 'axios';

function App() {

  const [name, setName] = useState("")
  const [stack, setStack] = useState(0)
  const [gameURL, setGameURL] = useState("")

  const getDetails = (user_name, stack) => {
    console.log(user_name, stack);
    setName(user_name)
    setStack(stack)
    getGameURL()
  }

  const getGameURL = () => {
    axios.post("http://localhost:8000/createMember&Room", "", {params: {
      name, stack
    }})
    .then(response => setGameURL(response.data.data))
    .catch(err => console.log(err))
  }  

  return (
    <div className="App">
      {gameURL == "" ?
      <StartScreen getDetails={getDetails} /> :
        <h1>{gameURL}</h1>
      }
    </div>
  );
}

export default App;
