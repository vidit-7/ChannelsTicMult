const room_name = JSON.parse(document.getElementById('room_name').textContent);
const url = `ws://${window.location.host}/ws/move/${room_name}/`;
const moveSocket = new WebSocket(url);

document.querySelector("#game_code_disp").innerText = `Game Code: ${room_name}`;


const zz = document.querySelector("#u00");
const zo = document.querySelector("#u01");
const zt = document.querySelector("#u02");
const oz = document.querySelector("#u10");
const oo = document.querySelector("#u11");
const ot = document.querySelector("#u12");
const tz = document.querySelector("#u20");
const to = document.querySelector("#u21");
const tt = document.querySelector("#u22");
const compfst = document.querySelector("#compfst");
const unbeatB = document.querySelector("#unbeatable");
const resDisp = document.querySelector("#result");

const dispboardarr = [zz, zo, zt, oz, oo, ot, tz, to, tt];

moveSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log("Data", data);
    console.log(data['action']);
    if (data['action'] === "chat_message") {
        const newNode = document.createElement('li');
        newNode.innerText = `${data['message_was']}`
        msgdisp.appendChild(newNode);
    }
    else if (data['action' === "player_moved"]) {
        onPlayerMove(data);
    }
}

moveSocket.onclose = function (e) {
    console.error("move socket closed unexp");
}

const msg = document.querySelector("#msg");
const sendBtn = document.querySelector("#sendBtn");
const msgdisp = document.querySelector("#msg-disp");

sendBtn.onclick = function () {
    moveSocket.send(JSON.stringify({
        'action': 'send_chat',
        'message': msg.value
    }));
    msg.value = ""
}

for(let unt of dispboardarr){
    unt.onclick = function() {
        json_dict = {    
            'action': 'make_move',
            'move_x': String(unt.id).charAt(1),
            'move_y': String(unt.id).charAt(2)
        }
    }
}

function onPlayerMove(data) {
    if (data['success']) {
        const x = data['ch_x']
        const y = data['ch_y']
        const symbol = data['symbol']
        const id_sel = `u${x}${y}`;
        document.querySelector(`#${id_sel}`).innerText = symbol;
    }
    else {
        console.log('invalid move');
    }
}

function checkGameOver(data){
    if(data['game_over']){
        console.log(`game over`);
        document.querySelector("#result").innerText = `Winner: ${data['winner']}`;
    }
}
