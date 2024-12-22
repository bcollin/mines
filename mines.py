from tkinter import *
import tkinter.font as font

gridWidth = 9
gridHeight = 9

gameState = 'playing' # Can receive clicks on the board.

levels = {'easy': 0.14, 'meh': 0.156, 'hard': 0.206}

def toggleReplayDialog():
    global gameState, replayFrame
    if gameState == 'playing':
        replayFrame.pack_forget()
    else:
        replayFrame.pack(side='left', expand = True)

def doWin():
    global statusVar, gameState, replayFrame
    gameState = 'waiting' # Player must initiate new game
    toggleReplayDialog()
    statusVar.set('You won!')

def doLose():
    global statusVar, uiTree, gameState, replayFrame
    gameState = 'waiting'
    toggleReplayDialog()
    statusVar.set('You lost...')
    # Reveal the bombs
    for y in range(len(uiTree)):
        for x in range(len(uiTree[y])):
            field = uiTree[y][x]
            field.elem.config(bd=0)
            if field.hasBomb:
                field.label.set('X')
            elif field.threatCount > 0:
                field.label.set(field.threatCount)
                field.elem.config(foreground='#999999')
            elif field.threatCount < 1:
                field.label.set(' ')
            else:
                # leave mistaken flags
                pass

class Field:
    global gameFrame, fieldsToClear
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = False
        self.hasFlag = False
        self.hasBomb = False
        self.threatCount = 0
        self.tileFont = font.Font(size = 10)

        self.label = StringVar(gameFrame, ' ')
        self.elem = Button(gameFrame,
                        textvariable = self.label,
                        borderwidth = 2,
                        width = 4,
                        height = 2,
                        font = self.tileFont
                        )
        self.elem.grid(row = y, column = x)
        command = lambda arg0 = None, arg1=x, arg2=y: leftClickField(event = arg0, x = arg1, y = arg2)
        self.elem.bind('<Button-1>', command)
        command = lambda arg0 = None, arg1=x, arg2=y: rightClickField(event = arg0, x = arg1, y = arg2)
        self.elem.bind('<Button-3>', command)
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
            self.elem.configure(relief='flat')
            if self.threatCount < 1:
                self.label.set(' ')
            else:
                self.label.set(str(self.threatCount))
                self.elem.config(foreground='#999999')
        else:
            # print('else', self.visible,x,y)
            pass
        # print ('Fields to clear:', fieldsToClear)
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

def neighboursWithBombs(x, y, uiTree):
    bombs = 0
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0) and inRange(x+i, 'hor') and inRange(y+j, 'ver'):
                if uiTree[y+j][x+i].hasBomb:
                    bombs = bombs + 1
    return bombs

def openNeighbours(x, y, grid):
    global uiTree
    # temp = [[0,0,0],[0,0,0],[0,0,0]]
    sum = 0
    testable = 8
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0):
                if inRange(x+i, 'hor') and inRange(y+j, 'ver'):
                    thisField = uiTree[y+j][x+i]
                    if not thisField.visible:
                        thisField.clearField()
                    if not thisField.hasBomb:
                        sum = sum + 1
                else:
                    testable = testable - 1
    grid[y][x] = 1
    if sum >= testable:
        for j in range(-1,2):
            for i in range(-1,2):
                if inRange(x+i, 'hor') and \
                   inRange(y+j, 'ver') and \
                   grid[y+j][x+i] != 1: 
                   openNeighbours(x+i, y+j, grid)
                   

def leftClickField(event, x, y):
    global uiTree, testGrid, gameState
    print(gameState)
    if gameState == 'waiting':
        return None
    if not uiTree[y][x].hasFlag:
        result = uiTree[y][x].test()
        if result:
            uiTree[y][x].clearField()
            openNeighbours(x, y, testGrid.copy())
            # Dirty hack, see https://stackoverflow.com/a/33128233
            uiTree[y][x].elem.config(bd=0)
        else:
            doLose()
        print('LMB:', event, x, y, vars(uiTree[y][x]))
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
    print('RMB:', event, x, y, vars(uiTree[y][x]))

def floor(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(inVal)

def ceil(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(floor(inVal)+1)
    

def plantBombs(uiTree, level='easy'):
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
        if not uiTree[y][x].hasBomb:
            uiTree[y][x].hasBomb = True
            # uiTree[y][x].label.set('X')
            bombsPlanted = bombsPlanted + 1
        attempts = attempts + 1
    print ('Bombs planted:', bombsPlanted)
    return bombsPlanted

def setUp(level='easy'):
    global uiTree, testGrid, gridWidth, gridHeight, bombsPlanted, fieldsToClear, statusVar, gameState, replayFrame, gameFrame

    if gameFrame != '':
        gameFrame.destroy()
    gameFrame = Frame()
    gameFrame.pack()


    uiTree = []
    testGrid  = []

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

    for y in range(gridHeight):
        uiTree.append([])
        testGrid.append([])
        for x in range(gridWidth):
            instance = Field(x, y)
            uiTree[y].append(instance)
            testGrid[y].append(0)

    bombsPlanted = plantBombs(uiTree, level)
    fieldsToClear = gridWidth * gridHeight - bombsPlanted

    for y in range(gridHeight):
        for x in range(gridWidth):
            uiTree[y][x].setNeighboursWithBombs(neighboursWithBombs(x, y, uiTree))

    statusVar.set('Hello!')
    gameState = 'playing'
    toggleReplayDialog()


def restartGame(level='easy'):
    global gameState
    if gameState == 'playing':
        # Needs to equal 'waiting' for the button to respond.
        return None
    setUp(level)
    gameState = 'playing'

ui = Tk()
ui.title('Mines')

statusFrame = Frame()
statusFrame.pack()
statusVar = StringVar(ui, 'Hello!')
statusMessage = Message(statusFrame, textvariable = statusVar)
statusMessage.pack(side='left', expand=True)
replayFrame = Frame(statusFrame)
replayFrame.pack(side='left', expand=True)
replayMessage = Label(replayFrame, text = 'Play again?')
replayMessage.pack(side='left', expand=True)
replayButton1 = Button(replayFrame, text = '9×9', command = lambda: restartGame('easy'))
replayButton1.pack(side='left', expand=True)
replayButton2 = Button(replayFrame, text = '16×16', command = lambda: restartGame('meh'))
replayButton2.pack(side='left', expand=True)
replayButton3 = Button(replayFrame, text = '30×16', command = lambda: restartGame('hard'))
replayButton3.pack(side='left', expand=True)
gameFrame = ''

setUp()

ui.mainloop()


