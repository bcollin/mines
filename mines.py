from tkinter import *
import tkinter.font as font

gridWidth = 8
gridHeight = 8

levels = {'easy': 0.14, 'meh': 0.16, 'hard': 0.2}

def doWin():
    global statusVar
    statusVar.set('You won!')

def doLose():
    global statusVar, uiTree
    statusVar.set('You lost...')
    # Reveal the bombs
    for y in range(len(uiTree)):
        for x in range(len(uiTree[y])):
            field = uiTree[y][x]
            field.elem.config(bd=0)
            if field.hasBomb:
                field.label.set('*')
            elif field.threatCount > 0:
                field.label.set(field.threatCount)
                field.elem.config(foreground='#999999')
            elif field.threatCount < 1:
                field.label.set(' ')
            else:
                # leave mistaken flags
                pass

class Field:
    global gameFrame, tileFont, fieldsToClear
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = False
        self.hasFlag = False
        self.hasBomb = False
        self.threatCount = 0
        
        self.label = StringVar(gameFrame, ' ')
        self.elem = Button(gameFrame,
                        textvariable = self.label,
                        borderwidth = 2,
                        width = 4,
                        height = 2
                        )
        self.elem.grid(row = y, column = x)
        command = lambda arg0 = None, arg1=x, arg2=y: leftClick(event = arg0, x = arg1, y = arg2)
        self.elem.bind('<Button-1>', command)
        command = lambda arg0 = None, arg1=x, arg2=y: rightClick(event = arg0, x = arg1, y = arg2)
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
                   

def leftClick(event, x, y):
    global uiTree, testGrid
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

def rightClick(event, x, y):
    global uiTree
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
    

def plantBombs(uiTree):
    import random
    global gridWidth, gridHeight, levels
    difficulty = levels['easy']

    tileMax = gridWidth * gridHeight
    bombMax = ceil(difficulty * tileMax)

    bombsPlanted = 0
    attempts = 0
    while bombsPlanted < bombMax and attempts < 1000:
        x = random.randint(1, gridWidth) - 1
        y = random.randint(1, gridHeight) - 1
        if not uiTree[y][x].hasBomb:
            uiTree[y][x].hasBomb = True
            # uiTree[y][x].label.set('*')
            bombsPlanted = bombsPlanted + 1
            print ('Bombs planted:', bombsPlanted)
        attempts = attempts + 1
    return bombsPlanted

ui = Tk()
uiTree = []
testGrid  = []
tileFont = font.Font(size = 32)

statusFrame = Frame()
statusFrame.pack()
statusVar = StringVar(ui, 'Hello!')
statusMessage = Message(statusFrame, textvariable = statusVar)
statusMessage.pack()
gameFrame = Frame()
gameFrame.pack()

for y in range(gridHeight):
    uiTree.append([])
    testGrid.append([])
    for x in range(gridWidth):
        instance = Field(x, y)
        uiTree[y].append(instance)
        testGrid[y].append(0)

bombsPlanted = plantBombs(uiTree)
fieldsToClear = gridWidth * gridHeight - bombsPlanted

for y in range(gridHeight):
    for x in range(gridWidth):
        uiTree[y][x].setNeighboursWithBombs(neighboursWithBombs(x, y, uiTree))
