const createBtn = document.querySelector("#createBtn");
const joinRoomInp = document.querySelector("#joinRoomInp");
const playerNameInp = document.querySelector("#playerNameInp");
const joinBtn = document.querySelector("#joinBtn");

joinBtn.onclick = function(){
    const roomName = joinRoomInp.value;
    if(roomName != ""){
        window.location.pathname = `/game/board/${roomName}`;
    }
}