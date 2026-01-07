const room_name = JSON.parse(document.getElementById('room_code').textContent);
const url = `ws://${window.location.host}/ws/move/${room_name}/`;
const moveSocket = new WebSocket(url);

const gameCodeDisp = document.querySelector("#game_code_disp");
const gameCodeCpyBtn = document.querySelector("#copyCodeBtn");
gameCodeDisp.innerText = `${room_name}`;
gameCodeCpyBtn.onclick = function(){
    const gameCode = gameCodeDisp.innerText;
    navigator.clipboard.writeText(gameCode);
    gameCodeCpyBtn.disabled = true;
    gameCodeCpyBtn.style.opacity = 0.65;
    gameCodeCpyBtn.innerText = "copied";
    setTimeout(()=>{
        gameCodeCpyBtn.disabled = false;
        gameCodeCpyBtn.style.opacity = 1;
        gameCodeCpyBtn.innerText = "Copy code";
    }, 2000);
}


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
    // console.log("Data", data);
    console.log(data['action']);
    if (data['action'] === "chat_message") {
        onChatMsg(data);
    }
    else if (data['action'] === "player_moved") {
        onPlayerMove(data);
    }
    else if(data['action'] === "move_timer_over"){
        checkGameOver(data)
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
    else if(data['action'] === "move_failed"){
        onMoveFailed(data);
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
    const pl1_name = data['player_symbols']["X"];
    const pl2_name = data['player_symbols']["O"];
    if(pl1_name){
        playerInfo1.innerText = pl1_name;
        // playerInfo1.classList.add(playerName.replace('#','_'));
    }
    if(pl2_name){
        playerInfo2.innerText = pl2_name;
        // playerInfo2.classList.add(playerName.replace('#','_'));
    }
    turnDispHandler(data);
}
function onPlayerLeaveDsp(data){
    const playerName = data['player_name'];
    displaySysMsg(`${playerName} left`);
    // const plCls = playerName.replace('#','_');
    // document.querySelector(`.${plCls}`).innerText = `${playerName} disconnected`;
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
    const isGameOver = checkGameOver(data);
    if(!isGameOver){
        turnDispHandler(data);
    }
}

function onMoveFailed(data){
    console.log(data);
    const failMsg = data['fail_msg'];
    const infoDiv = document.querySelector("#info_selfPlayer");
    infoDiv.innerText = failMsg;
    setTimeout(()=>{
        infoDiv.innerText = '';
    }, 2500);
}

function checkGameOver(data){
    if(data['game_over']){
        console.log(`game over`);
        winnerDisp.innerText = `Winner: ${data['winner']}`;
        if(timerIntervalGb != null){
            clearInterval(timerIntervalGb);
        }
        return true;
    }
    return false;
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
        gameResetTimerHelper();
    }
}

function gameResetTimerHelper(){
    if(timerIntervalGb != null) {clearInterval(timerIntervalGb);}
        const Xdisp = document.querySelector(`#X_plDisp`);
        const Odisp = document.querySelector(`#O_plDisp`);
        Xdisp.style.border = "4px solid black";
        Odisp.style.border = "4px solid gray";
        Xtimer = Xdisp.querySelector('.timerDisplay');
        Otimer = Odisp.querySelector('.timerDisplay');
        Xtimer.innerText = '--:--:--';
        Otimer.innerText = '--:--:--';
        Xtimer.style.border = '2px solid red';
        Xtimer.style.backgroundColor = "#ee8888";
        Otimer.style.border = '2px solid gray';
        Otimer.style.backgroundColor = "white";
}

// timer and turn handler
let timerIntervalGb = null;
// document.querySelector('#X_plDisp').style.border = "4px solid black";
function turnDispHandler(data){
    const turn = data['turn']
    const notTurn = (turn=="X") ? "O":"X";
    // console.log("turn not turn", turn, notTurn);
    const activePlayerDisp = document.querySelector(`#${turn}_plDisp`);
    const waitingPlayerDist = document.querySelector(`#${notTurn}_plDisp`);
    waitingPlayerDist.style.border = "4px solid gray";
    activePlayerDisp.style.border = "4px solid black";

    // timerHandler(turn, notTurn, data['next_move_time_limit']);
    const activeTimerDisp = activePlayerDisp.querySelector(".timerDisplay");
    const waitingTimerDisp = waitingPlayerDist.querySelector(".timerDisplay");

    activeTimerDisp.style.border = '2px solid red';
    activeTimerDisp.style.backgroundColor = "#ee8888";
    
    if(timerIntervalGb!=null){
        clearInterval(timerIntervalGb);
    }
    waitingTimerDisp.innerText = "--:--:--";
    waitingTimerDisp.style.border = '2px solid gray';
    waitingTimerDisp.style.backgroundColor = "white";

    const nextMoveTimeLimit = data['next_move_time_limit'];
    if(nextMoveTimeLimit!=null){
        // let dateTimeObj = new Date();
        // const currentTime = dateTimeObj.getTime();
        const currentTime = Date.now();
        console.log(turn, nextMoveTimeLimit, currentTime);
        // const remainingTime = nextMoveTimeLimit-currentTime;

        if(currentTime>=nextMoveTimeLimit){
            activeTimerDisp.innerText = "--:--:--";
            console.error(`Time conflict error ${nextMoveTimeLimit} ${currentTime}`);
            return;
        }
    
        let currentTimeMs = currentTime;
        timerIntervalGb = setInterval(()=>{
            currentTimeMs = Date.now();
            if(currentTimeMs>=nextMoveTimeLimit){
                clearInterval(timerIntervalGb);
                activeTimerDisp.innerText = '00:00:00';
            }
            else{
                activeTimerDisp.innerText = timerConvertHelper(nextMoveTimeLimit-currentTimeMs);
            }
        }, 10);
    }
}

function timerConvertHelper(timeInMs) {
    const millisecs =(Math.floor((timeInMs%1000)/10)).toString().padStart(2, '0'); 
    const secs = (Math.floor(timeInMs/1000)%60).toString().padStart(2, '0');
    const mins = (Math.floor(timeInMs/(1000*60))%60).toString().padStart(2, '0');
    return `${mins}:${secs}:${millisecs}`;
}

function onChatMsg(data){
    const newNode = document.createElement('div');
    newNode.innerText = `${data['player_name']}: ${data['message_was']}`
    newNode.classList.add('chatMessage');
    msgdisp.appendChild(newNode);
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



