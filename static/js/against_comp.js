//not good code, may have to change it entirely

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

const player1 = "X";
const player2 = "O";
let currentPlayer = undefined;

const dispboardarr = [[zz, zo, zt],
[oz, oo, ot],
[tz, to, tt]];

let boardarr = [[" ", " ", " "],
[" ", " ", " "],
[" ", " ", " "]];

let winner = " ";
// let count = 9;
let isPlayerMove = true;
let unbeatable = false;
// let start = false;


let row = undefined;
let col = undefined;

unbeatB.addEventListener('click',function(){
    resetBoard();
    // unbeatable ? $(this).css({'box-shadow' : 'none'}):$(this).css({'box-shadow' : '0 0 0 1px yellow'});
    (unbeatB.classList.contains('unbdisp')) ? unbeatB.classList.remove('unbdisp') : unbeatB.classList.add('unbdisp');
    unbeatable = !unbeatable;
    console.log(unbeatable);
});

compfst.addEventListener('click', function () {
    if (checkFreeSpaces(boardarr) == 9) {
        compfst.style.opacity = 0.5;
        computerMove();
    }
    else {
        console.log("computer has already moved");
    }
});

//assigning playermove function to each unit
for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
        dispboardarr[i][j].addEventListener('click',playerMove);
    }
}

function checkFreeSpaces(board){
    let count = 0;
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            if(board[i][j]==" "){
                count++;
            }
        }
    }
    return count;
}

function checkGameOver(thisBoardArr) {
    winner = checkWinner(thisBoardArr);
    console.log(winner);
    if (checkFreeSpaces(thisBoardArr) == 0 || winner != " ") {
        resDisp.innerText =(winner==" ")?"Tie":"Winner: "+winner;
        return true;
    }
    return false;
}

function checkWinner(whichBoardArr) {
    // checking rows
    for (let i = 0; i < 3; i++) {
        if (((whichBoardArr[i][0] == whichBoardArr[i][1]) && (whichBoardArr[i][0] == whichBoardArr[i][2]))
            && whichBoardArr[i][0] != " ") {
            return whichBoardArr[i][0];
        }
    }
    //checking cols
    for (let i = 0; i < 3; i++) {
        if (((whichBoardArr[0][i] == whichBoardArr[1][i]) && (whichBoardArr[0][i] == whichBoardArr[2][i]))
            && whichBoardArr[0][i] != " ") {
            return whichBoardArr[0][i];
        }
    }
    //checking diagonals
    if (((whichBoardArr[0][0] == whichBoardArr[1][1]) && (whichBoardArr[1][1] == whichBoardArr[2][2])) && whichBoardArr[1][1] != " ") {
        return whichBoardArr[1][1];
    }
    if (((whichBoardArr[0][2] == whichBoardArr[1][1]) && (whichBoardArr[1][1] == whichBoardArr[2][0])) && whichBoardArr[1][1] != " ") {
        return whichBoardArr[1][1];
    }

    return winner;
}

function playerMove(e) {
    console.log("player move")
    if (!checkGameOver(boardarr)) {
        let tgt = e.target.id;
        row = tgt[1];
        col = tgt[2];
        // console.log(row, col);
        console.log(boardarr);
        if (boardarr[row][col] == " ") {
            boardarr[row][col] = player1;
            dispboardarr[row][col].innerText =player1;
            isPlayerMove = false;
            // console.log("pwin", checkWinner());
            computerMove();
        }
        else {
            console.log("incorrect move");
        }
    }
    else {
        console.log("Game over. Winner is: "+winner);
    }
}

function computerMove() {
    console.log("comp move")
    if (!checkGameOver(boardarr)) {
        //minimax
        if (unbeatable) {
            let fLvlBoardInst = [];
            console.log("unb")
            for(let i=0;i<3;i++){
                fLvlBoardInst.push(boardarr[i]);
            }
            // console.log("fLvlBoardInst",fLvlBoardInst);
            let cScore = -Infinity;
            let score;
            let r;
            let c;
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    if(fLvlBoardInst[i][j]==" "){
                        fLvlBoardInst[i][j] = "O";
                        console.log("checking",i,j);
                        //false as the comp already played on the above line and now it's the turn of the minimizing player
                        score = minimax(fLvlBoardInst, false);
                        if(score>cScore){
                                console.log("y",cScore,score);
                                cScore = score;
                                r = i;
                                c = j;
                        }
                        fLvlBoardInst[i][j] = " ";
                    }
                }
            }
            console.log(r,c);
            boardarr[r][c] = player2;
            dispboardarr[r][c].innerText =player2;
            // let mmRes = minimax(fLvlBoardInst);
           
        }
        else {
            while (true) {
                let i = Math.floor(Math.random() * 3);
                let j = Math.floor(Math.random() * 3);
                if (boardarr[i][j] == " ") {
                    boardarr[i][j] = player2;
                    dispboardarr[i][j].innerText =player2;
                    break;
                }
            }
        }
        checkGameOver(boardarr);
        // console.log("cwin", checkWinner());
        isPlayerMove = true;
    }
    else {
        console.log("Game over. Winner is: "+winner);
    }
}

function resetBoard() {
    winner = " ";
    resDisp.innerText =winner;
    compfst.style.opacity = 1;
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            boardarr[i][j] = " ";
            dispboardarr[i][j].innerText =" ";
        }
    }
}

const reset = document.querySelector("#reset");
reset.addEventListener('click', resetBoard);

//minimax algo

lookUpTable = {
    "X":-1,
    "O": 1,
    " ": 0
}

// console.log(lookUpTable["X"],lookUpTable["O"],lookUpTable["T"]);
//broken
function minimax(currentBoard, isMaximizing){

    if(checkWinner(currentBoard)!==" " || checkFreeSpaces(currentBoard)===0){
        // console.log(lookUpTable[checkWinner(currentBoard)]);
        return lookUpTable[checkWinner(currentBoard)];
    }

    //if computer (consider computer as maximising ie it has to win)
    if(isMaximizing){
        let bestScore = -Infinity;
        let score;

        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if(currentBoard[i][j]==" "){
                    currentBoard[i][j] = "O";
                    score = minimax(currentBoard,false);
                    bestScore = Math.max(score, bestScore);
                    currentBoard[i][j] = " ";
                }
            }
        }
        return bestScore;
    }
    else{
        let bestScore = Infinity;
        let score;
        // let r = undefined;
        // let c = undefined;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if(currentBoard[i][j]==" "){
                    currentBoard[i][j] = "X";
                    score = minimax(currentBoard, true);
                    bestScore = Math.min(score, bestScore);
                    currentBoard[i][j] = " ";
                }
            }
        }
        return bestScore;
    }
}