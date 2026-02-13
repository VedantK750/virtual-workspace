const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const params = new URLSearchParams(window.location.search);
const room = params.get("room") || "default";

let ws = new WebSocket(`ws://127.0.0.1:8000/ws?room=${room}`);

let players = {};
// if inside proximity
let connectedPlayers = [];

// client-side state synchronization
// Key = player ID
// Value = player data from server

let myId = null;

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "JOIN") {
        myId = data.payload.your_id;

        players = {};
        data.payload.players.forEach(player => {
            players[player.id] = player;
        });
        updateProximity();
    }

    if (data.type === "WORLD_STATE") {
        // Reset Local State
        players = {};
        
        // Rebuild Local State
        data.payload.players.forEach(player => {
            players[player.id] = player;
        });
        if (data.payload.your_id) {
            myId = data.payload.your_id;
        }
        // update whenever there is a state change
        updateProximity();

    }
};

function render() {
    // erases the whole canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // draw every player
    Object.values(players).forEach(player => {
        if (player.id === myId) {
            ctx.fillStyle = "red";
        } else if(connectedPlayers.includes(player.id)){
            ctx.fillStyle = "green";
        } else{
            ctx.fillStyle = "white";
        }
        ctx.fillRect(player.x, player.y, 20, 20);
    });

    // a while(true) loop that keeps on rendering 
    requestAnimationFrame(render);
}

render();

document.addEventListener("keydown", (e) => {
    const speed = 10;

    let move = { x: 0, y: 0 };

    if (e.key === "ArrowUp") move.y -= speed;
    if (e.key === "ArrowDown") move.y += speed;
    if (e.key === "ArrowLeft") move.x -= speed;
    if (e.key === "ArrowRight") move.x += speed;

    // Get current player position
    const myPlayer = players[myId];
    if (!myPlayer) return;

    ws.send(JSON.stringify({
        type: "MOVE",
        payload: {
            x: myPlayer.x + move.x,
            y: myPlayer.y + move.y
        }
    }));
});

// implementing proximity client-side (for now)
function updateProximity() {
    connectedPlayers = [];
    const me = players[myId];
    if (!me) return;

    const threshold = 100;

    Object.values(players).forEach(other =>{
        if(other.id!= myId) {
            const dx = other.x - me.x;
            const dy = other.y - me.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < threshold) {
                connectedPlayers.push(other.id);
        }
    }
    });
}

    

