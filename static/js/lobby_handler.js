const createBtn = document.querySelector("#createBtn");
const joinRoomInp = document.querySelector("#joinRoomInp");
const playerNameInp = document.querySelector("#playerNameInp");
const joinBtn = document.querySelector("#joinBtn");

joinBtn.onclick = function(){
    const roomName = joinRoomInp.value;
    const playerName = playerNameInp.value;
    if(playerName){
        setCookie('player_name', playerName, 24);
    }
    if(roomName != ""){
        window.location.pathname = `/game/board/${roomName}`;
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