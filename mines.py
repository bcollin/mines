from tkinter import *
import tkinter.font as font
import time, pathlib, datetime

gridWidth = 9
gridHeight = 9
clock = 0
gameState = 'playing' # Can receive clicks on the board.
levels = {'easy': 0.14, 'meh': 0.156, 'hard': 0.206}

def getLevel():
    global gridWidth
    if gridWidth < 10:
        return 'easy'
    elif gridWidth > 25:
        return 'hard'
    else:
        return 'meh'

def readHighscores(path):
    try:
        with open(path, 'r') as f:
            print ('f')
    except Exception as error:
        print ('Error: ', error)
        return {}

def setHighScores(path):
    global highscores
    for lineDict in highscores:
        print ('test')
    try:
        pass
        # with open(path, 'w')
    except:
        pass

def addHighscore():
    global highscores, statusTimeVar
    level = getLevel()
    time = statusTimeVar.get()
    improvement = False
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if level not in highscores:
        highscores[level] = []
    highscores[level].append({'score': time, 'date': today})
    highscores[level] = sorted(highscores[level], key=lambda d: d['date'])
    highscores[level] = sorted(highscores[level], key=lambda d: d['score'])
    if len(highscores[level]) > 5:
        highscores[level].pop()

def showTime():
    global clock, gameState, ui, statusTimeVar
    if gameState != 'waiting':
        ui.after(1000, showTime)
    passed = time.time()-clock
    if passed < 3600:
        seconds = floor(passed % 60)
        minutes = floor(passed / 60)
        tStr = f"{minutes:02}.{seconds:02}"
    else:
        tStr = '1hr+'
    statusTimeVar.set(tStr)

def toggleReplayDialog():
    global gameState, replayFrame, replayFrameSettings
    if gameState == 'playing':
        replayFrame.pack_forget()
    else:
        replayFrame.pack(**replayFrameSettings)

def clearField(field):
    global drawingField
    drawingField.itemconfig(field.elem[0], fill='#a5a5a5')
    drawingField.itemconfig(field.elem[1], fill='#808080')
    x1, y1, x2, y2 = drawingField.coords(field.elem[2])
    drawingField.coords(field.elem[2])
    drawingField.coords(field.elem[2], x1-2, y1-2, x2+2, y2+2)
    if field.threatCount < 1:
        drawingField.itemconfig(field.elem[3], text = ' ') 
    else:
        drawingField.itemconfig(field.elem[3], text = field.threatCount, fill='#808080') 


def doWin():
    global gameState, uiTree, statusMessage, statusVar, drawingField 
    if gameState == 'waiting':
        return None
    gameState = 'waiting' # Player must initiate new game
    toggleReplayDialog()
    statusVar.set('You won!')
    statusMessage.config(fg='#00cc00', font="-weight bold")
    addHighscore()
    # Flag the bombs.
    for y in range(len(uiTree)):
        for x in range(len(uiTree[y])):
            field = uiTree[y][x]
            if field.hasBomb and not field.hasFlag:
                drawingField.itemconfig(field.elem[3], text = 'P')

def doLose():
    global gameState, statusMessage, statusVar, uiTree, drawingField 
    gameState = 'waiting'
    toggleReplayDialog()
    statusVar.set('You la-la-lost...')
    statusMessage.config(fg="#cc0000", font= "-weight bold")
    # Reveal the bombs.
    for y in range(len(uiTree)):
        for x in range(len(uiTree[y])):
            field = uiTree[y][x]
            if field.hasBomb:
                drawingField.itemconfig(field.elem[3], text = 'X')
            else:
                clearField(field)

def buildFakeButton(parent, label = '', x=0, y=0, width=10, height=10, font = None):
    global drawingField
    x1 = x * width
    x2 = x1 + width
    xt = (x2 + x1) / 2
    y1 = y * height
    y2 = y1 + height
    yt = (y2 + y1) / 2
    # To toggle, swap the fills of sq1 and sq2, e.g.
    # canvas.itemconfig(element, fill='black').
    
    # Represents top and left edge.
    sq1 = drawingField.create_polygon(x1, y1, x2, y1, x1, y2, fill="#ffffff", outline='')

    # Represents bottom and right edge
    sq2 = drawingField.create_polygon(x1, y2, x2, y2, x2, y1, fill="#606060", outline='')

    # The clickable center.
    sq3 = drawingField.create_rectangle(x1+3, y1+3, x2-3, y2-3, fill="#c6c6c6", outline='')

    # Option to render a bomb symbol, a flag or a threat count.
    sq4 = drawingField.create_text(xt, yt, text = label, font=font)

    out = [sq1, sq2, sq3, sq4]

    return out

class Field:
    def __init__(self, x, y):
        global gameFrame, drawingField
        self.x = x
        self.y = y
        self.visible = False
        self.hasFlag = False
        self.hasBomb = False
        self.threatCount = 0

        self.label = StringVar(gameFrame, ' ')
        self.elem = buildFakeButton(gameFrame,
                        label=' ',
                        x=x,
                        y=y,
                        width=40,
                        height=40,
                        font=tileFont)

        # Tkinter's events are basically X-Windows events.
        # Documentation can be sparse, outdated, and only
        # maintained by someone who seemingly needed 
        # someone better informed to do it.
        command = lambda arg0 = None, arg1=x, arg2=y: rightClickField(event = arg0, x = arg1, y = arg2)
        drawingField.tag_bind(self.elem[2], '<Button-3>', command)
        drawingField.tag_bind(self.elem[3], '<Button-3>', command)
        command = lambda arg0 = None, arg1=x, arg2=y: rightClickField(event = arg0, x = arg1, y = arg2)
        drawingField.tag_bind(self.elem[2], '<Control-Button-1>', command)
        drawingField.tag_bind(self.elem[3], '<Control-Button-1>', command)
        command = lambda arg0 = None, arg1=x, arg2=y: leftClickField(event = arg0, x = arg1, y = arg2)
        drawingField.tag_bind(self.elem[2], '<Button-1>', command)
        drawingField.tag_bind(self.elem[3], '<Button-1>', command)
    def test(self):
        if self.hasBomb:
            return False
        elif self.hasFlag:
            # maybe warn that field cannot be tested?
            return True
        else:
            return True
    def toggleFlag(self):
        if not self.visible: # cannot plant flag in tested field
            if self.hasFlag:
                self.hasFlag = False
            else:
                self.hasFlag = True
    def getCoords(self):
        return (x, y)
    def setNeighboursWithBombs(self, num):
        self.threatCount = num
    def clearField(self):
        global fieldsToClear
        if not self.visible and \
        not self.hasFlag and \
        not self.hasBomb:
            # print('if', self.visible,x,y)
            fieldsToClear = fieldsToClear - 1
            self.visible = True
            clearField(self)
        if fieldsToClear < 1:
            doWin()
    # End of class Field.

def inRange(value, direction = 'hor'):
    global gridWidth, gridHeight
    if direction == 'hor':
        if 0 <= value < gridWidth:
            return True
    if direction == 'ver':
        if 0 <= value < gridHeight:
            return True
    return False

def neighboursWithBombs(x, y, board):
    bombs = 0
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0) and inRange(x+i, 'hor') and inRange(y+j, 'ver'):
                if board[y+j][x+i].hasBomb:
                    bombs = bombs + 1
    return bombs

def openNeighbours(x, y, grid):
    global uiTree
    # temp = [[0,0,0],[0,0,0],[0,0,0]]
    grid[y][x] = 1
    worthy_neighbours = []
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0):
                if inRange(x+i, 'hor') and inRange(y+j, 'ver') and grid[y+j][x+i] != 1:
                    thisField = uiTree[y+j][x+i]
                    if not thisField.visible:
                        thisField.clearField()
                    if uiTree[y+j][x+i].threatCount == 0:
                        openNeighbours(x+i, y+j, grid)
                   

def leftClickField(event, x, y):
    global ui, uiTree, testGrid, gameState, clock
    # print(gameState)
    if gameState == 'waiting':
        return None
    if clock == 0:
        # Invoking Tkinter's built-in scheduler. 
        ui.after(1, showTime)
        clock = time.time()
    if not uiTree[y][x].hasFlag:
        result = uiTree[y][x].test()
        if result:
            uiTree[y][x].clearField()
            openNeighbours(x, y, testGrid)
        else:
            doLose()
        # print('LMB:', event, x, y, vars(uiTree[y][x]))
    else:
        print('Has flag')

def rightClickField(event, x, y):
    global uiTree, gameState
    if gameState == 'waiting':
        return None
    elem = uiTree[y][x]
    if not elem.visible:
        elem.toggleFlag()
        if elem.hasFlag:
            uiTree[y][x].label.set('P')
        else:
            uiTree[y][x].label.set(' ')
            pass
    # print('RMB:', event, x, y, vars(uiTree[y][x]))

def floor(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(inVal)

def ceil(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(floor(inVal)+1)
    

def plantBombs(board, level='easy'):
    import random
    global gridWidth, gridHeight, levels

    if level not in levels:
        level = 'easy'

    difficulty = levels[level]

    tileMax = gridWidth * gridHeight
    bombMax = ceil(difficulty * tileMax)

    bombsPlanted = 0
    attempts = 0
    while bombsPlanted < bombMax and attempts < 1000:
        x = random.randint(1, gridWidth) - 1
        y = random.randint(1, gridHeight) - 1
        if not board[y][x].hasBomb:
            board[y][x].hasBomb = True
            # board[y][x].label.set('X')
            bombsPlanted = bombsPlanted + 1
        attempts = attempts + 1
    print ('Bombs planted:', bombsPlanted)
    return bombsPlanted

def setUp(level='easy'):
    global uiTree, gameFrame, drawingField, testGrid, gridWidth, gridHeight, fieldsToClear, statusVar, gameState, statusMessage, clock, statusTimeVar, highscores

    print(highscores)

    if level == 'meh':
        gridWidth = 16
        gridHeight = 16
    elif level == 'hard':
        gridWidth = 30
        gridHeight = 16
    else:
        # level == 'easy'
        gridWidth = 9
        gridHeight = 9

    if gameFrame != '':
        gameFrame.destroy()
    gameFrame = Frame(relief='groove', bd=4)
    gameFrame.pack(side='bottom', expand=True, padx=4, pady=4)
    if drawingField != '':
        drawingField.destroy
        print(drawingField)
    drawingField = Canvas(gameFrame, width=gridWidth * 40, height=gridHeight * 40)
    drawingField.pack()

    uiTree = []
    testGrid  = []

    for y in range(gridHeight):
        uiTree.append([])
        testGrid.append([])
        for x in range(gridWidth):
            uiTree[y].append(Field(x, y))
            testGrid[y].append(0)

    bombsPlanted = plantBombs(uiTree, level)
    fieldsToClear = gridWidth * gridHeight - bombsPlanted

    for y in range(gridHeight):
        for x in range(gridWidth):
            uiTree[y][x].setNeighboursWithBombs(neighboursWithBombs(x, y, uiTree))

    statusVar.set('Hello!')
    statusMessage.config(fg="#000000", font="-weight normal")
    gameState = 'playing'
    toggleReplayDialog()
    clock = 0
    statusTimeVar.set('00.00')

def restartGame(level='easy'):
    global gameState
    if gameState == 'playing':
        # Needs to equal 'waiting' for the button to respond.
        return None
    setUp(level)
    gameState = 'playing'

ui = Tk()
ui.title('Mines')

tileFont = font.Font(size = 10)

statusFrame = Frame(ui, height=32, width=320)
statusFrame.pack(side='top', fill = 'x', pady=(6,2))
statusFrame.pack_propagate(0)

statusTimeVar = StringVar(ui, '00.00')
statusClock = Message(statusFrame, textvariable = statusTimeVar, width=72)
statusClock.pack(side='left')

statusVar = StringVar(ui, 'Hello!')
statusMessage = Message(statusFrame, textvariable = statusVar, width=200)
statusMessage.pack(side='left')

replayFrameSettings = {'side': 'top', 'expand': True, 'fill':'x'}
replayFrame = Frame(ui, height=32)
replayFrame.pack()

replayMessage = Label(replayFrame, text = 'Play again?')
replayMessage.pack(side='left')

replayButton1 = Button(replayFrame, text = '9×9', command = lambda: restartGame('easy'))
replayButton1.pack(side='left', padx=(4,0))

replayButton2 = Button(replayFrame, text = '16×16', command = lambda: restartGame('meh'))
replayButton2.pack(side='left', padx=(4,0))

replayButton3 = Button(replayFrame, text = '30×16', command = lambda: restartGame('hard'))
replayButton3.pack(side='left', padx=(4,0))

gameFrame = ''
drawingField = ''

home = pathlib.Path.home()
confDir = home / '.mines'
try:
    confDir.mkdir(parents=True, exist_ok=True)
except Exception as error:
    print ('Error: ', error)
highscoreFilePath =  confDir / 'highscores.txt'
highscores = readHighscores(highscoreFilePath)

setUp()

ui.mainloop()


