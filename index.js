// server/index.js

const express = require('express');
const app = express();
http = require('http');
const cors = require('cors');
const { Server } = require('socket.io'); // Add this

app.use(cors()); // Add cors middleware

const server = http.createServer(app); // Add this

// Add this
// Create an io server and allow for CORS from http://localhost:3000 with GET and POST methods
const io = new Server(server, {
  cors: {
    origin: 'https://teenpattiwebsite.herokuapp.com/',
    credentials: true ,
    methods: ['GET', 'POST', 'PUT'],
  },
});

// Add this
// Listen for when the client connects via socket.io-client

let allUsers = []
let room = ''

io.on('connection', (socket) => {
  console.log(`User connected ${socket.id}`);
  socket.emit("connected", {
    message: "Connected to socket.io on backend"
  })

  socket.on("room_lead", (data) => {
    
    const index = allUsers.findIndex(obj => (obj.name === data.name) && (obj.roomId === data.roomId))
    if (index === -1){
      allUsers.push(data)
      socket.join(data["roomId"])
    }
    console.log("room lead all users", allUsers);
  })

  socket.on("player_joined", (data) => {
    var room = data["roomId"]
    socket.join(room)
  })

  socket.on("seat_request", (data) => {
    var room = data["roomId"]
    console.log("seat request",data, room);
    const index = allUsers.findIndex(obj => (obj.name === data.name) && (obj.roomId === data.roomId))
    if (index === -1){
      allUsers.push(data)
      socket.join(data["roomId"])
    }
    socket.to(room).emit("seat_request_recieved", data)
    console.log("all users", allUsers);
    // socket.emit("seat_request_recieved", data)
  })

  socket.on("seat_denied", (data) => {
    var room = data["roomId"]
    socket.to(room).emit("player_seat_denied", data)
  })

  socket.on("seat_approved", (data) => {
    var room = data["roomId"]
    socket.to(room).emit("player_seat_approved", data)
  })

  socket.on("game_started", (data) => {
    console.log("game has started");
    var room = data["roomId"] 
    socket.to(room).emit("player_game_started", data)
  })

  socket.on("update_move", (data) => {
    console.log("player moved");
    var room = data["roomId"] 
    socket.to(room).emit("player_update_move", data)
  })

  socket.on("full_show", (data) => {
    console.log("full_show");
    var room = data["roomId"] 
    socket.to(room).emit("player_full_show", data)
  })

  socket.on("side_show_request", (data) => {
    console.log("side_show");
    var room = data["roomId"] 
    socket.to(room).emit("player_side_show_request", data)
  })

  socket.on("player_left", (data) => {
    console.log("player_left");
    var room = data["roomId"] 
    socket.to(room).emit("player_player_left", data)
  })

  socket.on("sideshow_result", (data) => {
    console.log("sideshow_result");
    var room = data["roomId"] 
    socket.to(room).emit("player_sideshow_result", data)
  })



  // We can write our socket event listeners in here...
});

app.get('/', (req, res) => {
    res.send('Hello world');
  })

server.listen(4000, () => 'Server is running on port 4000');
