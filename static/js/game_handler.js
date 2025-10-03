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
const compfstBtn = document.querySelector("#compfst");
const winnerDisp = document.querySelector("#result");
const unbeatBtn = document.querySelector("#unbeatable");
const resetBtn = document.querySelector("#reset");

const dispboardarr = [zz, zo, zt, oz, oo, ot, tz, to, tt];

moveSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log("Data", data);
    console.log(data['action']);
    if (data['action'] === "chat_message") {
        onChatMsg(data);
    }
    else if (data['action'] === "player_moved") {
        onPlayerMove(data);
    }
    else if(data['action'] === "connection_made"){
        onRoomConnectionMade(data);
    }
    else if(data['action'] === "player_joined"){
        onPlayerJoinDsp(data);
    }
    else if(data['action'] === "player_left"){
        onPlayerLeaveDsp(data);
    }
    else if(data['action'] === "game_reset"){
        console.log("game reset signal");
        onGameReset(data);
    }
}

moveSocket.onclose = function (e) {
    console.error("move socket closed unexp");
}

const msgInp = document.querySelector("#msgInp");
const sendBtn = document.querySelector("#sendBtn");
const msgdisp = document.querySelector("#msgDisp");

sendBtn.onclick = function () {
    moveSocket.send(JSON.stringify({
        'action': 'send_chat',
        'message_body': msgInp.value
    }));
    msgInp.value = ""
}

let resetVal = true;
resetBtn.onclick = function(){
    console.log("reset wish");
    moveSocket.send(JSON.stringify({
        'action': 'reset_game',
        'play_again_value': resetVal
    }));
    resetVal = !resetVal;
}

for(let unt of dispboardarr){
    unt.onclick = function() {
        json_dict = {    
            'action': 'make_move',
            'move_x': String(unt.id).charAt(1),
            'move_y': String(unt.id).charAt(2)
        }
        moveSocket.send(JSON.stringify(json_dict));
    }
}

const playerInfo1 = document.querySelector("#pl1symb");
const playerInfo2 = document.querySelector("#pl2symb");

function onPlayerJoinDsp(data){
    const playerName = data['player_name'];
    displaySysMsg(`${playerName} joined`);
    console.log(data['player_symbols'])
    const pl1 = data['player_symbols']["X"];
    const pl2 = data['player_symbols']["O"];
    if(pl1){
        playerInfo1.innerText = pl1;
    }
    if(pl2){
        playerInfo2.innerText = pl2;
    }
}
function onPlayerLeaveDsp(data){
    const playerName = data['player_name'];
    displaySysMsg(`${playerName} left`);
    
}

function onRoomConnectionMade(data){
    const chatLog = data['chat_log'];
    const board = data['board_state'];
    const winner = data['winner'];
    console.log(chatLog);
    for(let chatTuple of chatLog){
        if(chatTuple[0]=="game_sys"){
            displaySysMsg(`${chatTuple[1]}`);
        }
        else{
            onChatMsg({'player_name': chatTuple[0], 'message_was': chatTuple[1]});
        }
    }
    let count = 0;
    for(let i=0; i<board.length; i++){
        for(let j=0; j<board[0].length; j++){
            dispboardarr[count].innerText = board[i][j];
            count+=1;
        }
    }
}

function onPlayerMove(data) {
    console.log("received data", data);
    // const expectedPlayer = data['expected_player'];
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
    // if(expectedPlayer){
    //     if(!success){
    //         console.log('invalid move');
    //     }
    // }
    checkGameOver(data);
}

function checkGameOver(data){
    if(data['game_over']){
        console.log(`game over`);
        winnerDisp.innerText = `Winner: ${data['winner']}`;
    }
}

function onChatMsg(data){
    const newNode = document.createElement('div');
    newNode.innerText = `${data['player_name']}: ${data['message_was']}`
    newNode.classList.add('chatMessage');
    msgdisp.appendChild(newNode);
}

function displaySysMsg(dataStr){
    const newNode = document.createElement('div');
    const boldNode = document.createElement('b');
    boldNode.innerText = `${dataStr}`;
    newNode.appendChild(boldNode);
    newNode.classList.add('chatMessage');
    msgdisp.appendChild(newNode);
}

function onGameReset(data){
    console.log(data);
    // console.log(data['reset_state']);
    displaySysMsg(`${data['reset_message']}`);
   
    if(data['reset_state']){
        // displaySysMsg(`${data['reset_message']}`);
        const board = data['board'];
        winnerDisp.innerText = "";
        let count = 0;
        for(let i=0; i<board.length; i++){
            for(let j=0; j<board[0].length; j++){
                dispboardarr[count].innerText = board[i][j];
                count+=1;
            }
        }
        resetVal = true;
        // displaySysMsg("Game has been reset");
    }
}


function scrollToLastChatMsg(){
    // messageInp.style.height = "auto";
    let lastMsg = msgdisp.lastElementChild;
    if(lastMsg!=null){
        lastMsg.scrollIntoView({behaviour: "instant", block:"end"});
    }
}

msgInp.addEventListener("input", function(){
    this.style.height = "auto";
    if(this.scrollHeight<=180){
        this.style.height = `${this.scrollHeight}px`;
    }
    else{
        this.style.height = "180px";
    }
});

let chatObserver = new MutationObserver(scrollToLastChatMsg);
chatObserver.observe(msgdisp, {childList: true, subtree: true});