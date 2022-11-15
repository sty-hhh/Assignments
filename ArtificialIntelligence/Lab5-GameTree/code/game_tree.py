import numpy as np

INF = 1000000
depth = 5

# 建立新棋盘
def NewBoard():
    board = []
    for _ in range(8):
        board.append(['.'] * 8)
    return board

# 初始化棋盘
def resetBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = '.'
    # 初始布局
    board[3][3] = 'X'
    board[3][4] = 'O'
    board[4][3] = 'O'
    board[4][4] = 'X'

# 是否出界
def OnBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <= 7

# 返回能被翻转的棋子位置，没有则返回False
def FlipPosition(board, Color, x, y):
    # 如果出界了或者该位置已经有棋子，返回False
    if not OnBoard(x, y) or board[x][y] != '.':
        return False
    if Color == 'X':
        otherColor = 'O'
    else:
        otherColor = 'X'
    # 要被翻转的棋子
    Flipchess = []
    for xdirection, ydirection in [[0, 1],[1, 1],[1, 0],[1, -1],[0, -1],[-1, -1],[-1, 0],[-1, 1]]:
        i, j = x, y
        i += xdirection
        j += ydirection
        if OnBoard(i, j) and board[i][j] == otherColor:
            i += xdirection
            j += ydirection
            # 一直走到出界或不是对方棋子的位置
            while OnBoard(i, j) and board[i][j] == otherColor:
                i += xdirection
                j += ydirection
            # 出界了，则没有棋子要翻转
            if not OnBoard(i, j):
                continue
            # 是自己的棋子
            if board[i][j] == Color:
                while True:
                    i -= xdirection
                    j -= ydirection
                    # 回到了起点则结束
                    if i == x and j == y:
                        break
                    # 需要翻转的棋子
                    Flipchess.append([i, j])
    # 没有要被翻转的棋子，则走法非法。翻转棋的规则。
    if len(Flipchess) == 0: 
        return False
    return Flipchess

# 返回可落子的位置
def ValidMoves(board, Color):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if FlipPosition(board, Color, x, y) != False:
                validMoves.append([x, y])
    return validMoves

# 获取棋盘上黑白双方的棋子数
def Score(board):
    BoardBlack = np.zeros((8,8))
    BoardWhite = np.zeros((8,8))
	# 棋盘估值表
    Vmap = np.array([[100, -25, 10, 5, 5, 10, -25, 100], 
                     [-25, -45, 1, 1, 1, 1, -45, -25], 
                     [10, 1, 3, 2, 2, 3, 1, 10],
                     [5, 1, 2, 1, 1, 2, 1, 5], 
                     [5, 1, 2, 1, 1, 2, 1, 5], 
                     [10, 1, 3, 2, 2, 3, 1, 10],
                     [-25, -45, 1, 1, 1, 1, -45, -25], 
                     [100, -25, 10, 5, 5, 10, -25, 100]])
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'X':
                BoardBlack[x][y] = 1
            if board[x][y] == 'O':
                BoardWhite[x][y] = 1

    BoardBlack = BoardBlack * Vmap
    BoardWhite = BoardWhite * Vmap
    BlackValue = np.sum(BoardBlack)
    WhiteValue = np.sum(BoardWhite)
    return {'X': BlackValue, 'O': WhiteValue}

# 将一个Color棋子放到(x, y)，返回True或False，并在board中修改值
def makeMove(board, Color, x, y):
    Flipchess = FlipPosition(board, Color, x, y)
    if Flipchess == False:
        return False
    board[x][y] = Color
    for i, j in Flipchess:
        board[i][j] = Color
    return True

# 复制棋盘
def CopyBoard(board):
    dupeBoard = NewBoard()
    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]
    return dupeBoard

# 返回电脑最佳走法的坐标和得分
def ComputerMove(board, computerColor):
    bestMove = []
    possibleMoves = ValidMoves(board, computerColor)
    bestScore = 0
    for x, y in possibleMoves:
        dupeBoard = CopyBoard(board)
        makeMove(dupeBoard, computerColor, x, y)
        score = MaxValue(dupeBoard,computerColor,-INF,INF,depth)
        if score is not INF and score > bestScore:
            bestMove = [x, y]
            bestScore = score
    if len(bestMove) == 0:
        for x, y in possibleMoves:
            bestMove = [x,y]
            break
    return bestMove, bestScore

def MaxValue(board,Color,alpha,beta,depth):
    if depth == 1:
        return Score(board)[Color]
    bestValue = -INF
    if Color == 'X':
        otherColor = 'O'
    else:
        otherColor = 'X'
    possible = ValidMoves(board,Color)
    for x,y in possible:
        copyBoard = CopyBoard(board)
        makeMove(copyBoard,Color,x,y)
        bestValue = max(bestValue, MinValue(copyBoard,otherColor,alpha,beta,depth-1))
        if bestValue >= beta:   # Max节点alpha剪枝：效益值 >= 任何祖先Min节点beta值
            return bestValue
        alpha = max(alpha, bestValue)
    return bestValue

def MinValue(board,Color,alpha,beta,depth):
    if depth == 1:
        return Score(board)[Color]
    bestValue = INF
    if Color == 'X':
        otherColor = 'O'
    else:
        otherColor = 'X'
    possible = ValidMoves(board,Color)
    for x,y in possible:
        copyBoard = CopyBoard(board)
        makeMove(copyBoard,Color,x,y)
        bestValue = min(bestValue, MaxValue(copyBoard,otherColor,alpha,beta,depth-1))
        if bestValue <= alpha:  # Min节点beta剪枝：效益值 <= 任何祖先Max节点alpha值
            return bestValue
        beta = min(beta, bestValue)
    return bestValue

# 是否游戏结束
def GameOver(board):
    for x in range(8):
        for y in range(8):
            if board[x][y] == '.':
                return False
    return True

# 输出棋盘
def printBoard(mainBoard, validMoves):
    str = ''
    black = 0
    white = 0
    for i in range(8):
        for j in range(8):
            if [i,j] in validMoves:
                str += '#'
            elif mainBoard[i][j] == 'X':
                str += 'X'
                black += 1
            elif mainBoard[i][j] == 'O':
                str += 'O'
                white += 1
            else:
                str +='.'
        str += '\n'
    print(str)
    print('black:', black)
    print('white:', white)

# main
mainBoard = NewBoard()
resetBoard(mainBoard)
turn = 'player'   # 可设定玩家先手还是电脑先手
if turn == 'player':
    playerColor = 'X'
    computerColor = 'O'
else:
    playerColor = 'O'
    computerColor = 'X'
gameOver = False

# 游戏主循环
validMoves = [[2,4],[3,5],[4,2],[5,3]]
round = 1
while True:
    print('********************************')
    print('Round', round)
    round += 1
    printBoard(mainBoard, validMoves)
    if gameOver == False and turn == 'player':
        print(turn)
        x,y = input('Input the position:').split()
        x = int(x)
        y = int(y)
        if makeMove(mainBoard, playerColor, x, y) == True:
            # score = Score(mainBoard)[playerColor]
            score = MaxValue(mainBoard,computerColor,-INF,INF,depth+1)
            print('player score:', score)
            validMoves = ValidMoves(mainBoard, computerColor)
            if validMoves != []:
                turn = 'computer'  
        elif len(ValidMoves(mainBoard, playerColor)) == 0:
            if ValidMoves(mainBoard, computerColor) != []:
                turn = 'computer'
            else:
                gameOver = True
    printBoard(mainBoard, validMoves)
    if gameOver == False and turn == 'computer':
        print(turn)
        tmp, score = ComputerMove(mainBoard, computerColor)
        if len(tmp):
            x, y = tmp
        else:
            if ValidMoves(mainBoard, playerColor)!= []:
                turn = 'player'
            else:
                gameOver = True
        makeMove(mainBoard, computerColor, x, y)
        # score = Score(mainBoard)[computerColor]
        print(tmp)
        print('computer score:', score)
        # 玩家有可行的走法
        validMoves = ValidMoves(mainBoard, playerColor)
        if validMoves != []:
            turn = 'player'
    
    if GameOver(mainBoard) or gameOver is True:
        print('Game over!')
        break
