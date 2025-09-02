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
    // console.log("Data", data);
    console.log(data['action']);
    if (data['action'] === "chat_message") {
        const newNode = document.createElement('li');
        newNode.innerText = `${data['player_id']}\n${data['message_was']}`
        msgdisp.appendChild(newNode);
    }
    else if (data['action'] === "player_moved") {
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
        'message_body': msg.value
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
        moveSocket.send(JSON.stringify(json_dict));
        // onPlayerMove(data);
    }
}

function onPlayerMove(data) {
    console.log("received data", data);
    const expectedPlayer = data['expected_player'];
    const success = data['success'];
    const board = data['board'];
    // const id_sel = `#u${x}${y}`;

    let count = 0;
    for(let i=0; i<board.length; i++){
        for(let j=0; j<board[0].length; j++){
            dispboardarr[count].innerText = board[i][j];
            count+=1;
        }
    }
    if(data['winner']){
        document.querySelector("#result").innerText = data['winner'];
    }
    if(expectedPlayer){
        if(!success){
            console.log('invalid move');
        }
    }
}

function checkGameOver(data){
    if(data['game_over']){
        console.log(`game over`);
        document.querySelector("#result").innerText = `Winner: ${data['winner']}`;
    }
}
