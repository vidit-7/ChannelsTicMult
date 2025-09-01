# def checkWinner(board):
#     for i in range(3):
#         if board[i][0] != "" and (board[i][0]==board[i][1]==board[i][2]):
#             return board[i][0]
#     for i in range(3):
#         if board[0][i] != "" and (board[0][i]==board[1][i]==board[2][i]):
#             return board[0][i]
    
#     if(board[0][0] != "") and (board[0][0]==board[1][1]==board[2][2]):
#         return board[0][0]
    
#     if(board[0][2] != "") and (board[0][2]==board[1][1]==board[2][0]):
#         return board[0][2]

#     return ""

def checkWinner(board):
    n = len(board)

    for i in range(n):
        rowFirst = board[i][0]
        count = 1
        if rowFirst != "":
            for j in range(1, n):
                if(board[i][j] != rowFirst):
                    break
                count+=1
        if count == n:
            return rowFirst
    
    for i in range(n):
        colFirst = board[0][i]
        count = 1
        if colFirst != "":
            for j in range(1, n):
                if(board[j][i] != colFirst):
                    break
                count+=1
        if count == n:
            return colFirst
    
    diagFirst = board[0][0]
    diagCount = 1
    if diagFirst != "":
        for i in range(1, n):
            if board[i][i] != diagFirst:
                break
            diagCount += 1
    if(diagCount==n):
        return diagFirst
    
    antiDiagFirst = board[0][n-1]
    antiDiagCount = 1
    if antiDiagFirst != "":
        for i in range(1, n):
            if board[i][n-1-i] != antiDiagFirst:
                break
            antiDiagCount += 1
    if(antiDiagCount==n):
        return antiDiagFirst

    return ""

def checkValidMove(board, i, j):
    if board[i][j] == "":
        return True
    return False

def checkFreeSpots(board):
    n = len(board)
    total = n*n
    taken = 0
    for i in range(n):
        for j in range(n):
            if board[i][j] != "":
                taken += 1
    return False if taken==total else True

def checkGameOverWin(board):
    winner = checkWinner()
    if winner != "":
        return (True, winner)
    
    if(not checkFreeSpots(board)):
        return (True, "Tie")
    
    return (False, None)

def playerMakeMove(current_game, x, y, playerSymbol):
    if checkValidMove(x, y) and current_game['move_hist'][-1][3]!=playerSymbol:
        current_game['board'][x][y] = playerSymbol
        current_game['move_hist'].append((x,y,playerSymbol))
        return True
    return False

def newGameBoard():
    return {
        "board" : [["" for _ in range(3)] for _ in range(3)],
        "players" : dict(), # sessionid to X or O, X or O to sessionid
        "turn" : None, # player/session id
        "move_hist" : list(),
        "winner": None
    }

def assignSymbols(game_state, player_id):
    if len(game_state['players']) == 0:
        game_state['players'][player_id] = "X"
    elif len(game_state['players']) == 1:
        game_state['players'][player_id] = "O"