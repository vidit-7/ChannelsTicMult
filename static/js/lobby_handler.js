const createBtn = document.querySelector("#createBtn");
const joinRoomInp = document.querySelector("#joinRoomInp");
const playerNameInp = document.querySelector("#playerNameInp");
const joinBtn = document.querySelector("#joinBtn");
const infoMsg = document.querySelector("#infomsg");

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function roomCreJoiMsgDisp(text, col){
    infoMsg.style.color = col;
    infoMsg.innerText = text;
    setTimeout(()=>{
        infoMsg.innerText = "";
    }, 6500);
}

createBtn.onclick = async function(){
    try {
        let response = await fetch(
            `/game/create-room/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken 
                },
            }
        );
        let data = await response.json();
        console.log(data);
        if(data['success']){
            roomCreJoiMsgDisp(`Room ${data['game_code']} is ready to join.`, "green");
            joinRoomInp.value = data['game_code'];
        }
        else{
            roomCreJoiMsgDisp("Couldn't create room.", "red");
            console.log("Couldn't create room");
        }
        // handle the logic of adding comment w/o reloading here later
        // location.reload();
    }
    catch (e) {
        console.log(e);
    }

}

joinBtn.onclick = function(){
    const roomCode = joinRoomInp.value;
    const playerName = playerNameInp.value;
    if(playerName){
        setCookie('player_name', playerName, 24);
    }

    if(roomCode != ""){
        window.location.pathname = `/game/board/${roomCode}`;
    }
}

function setCookie(name, value, expiryDays){
    const date = new Date();
    date.setTime(date.getTime() + (expiryDays*24*60*60*1000));
    const expiryDate = date.toUTCString();
    document.cookie = `${name}=${value}; ${expiryDate}; path=/`;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let player_name = getCookie('player_name');
if(player_name){
    playerNameInp.value = player_name;
}