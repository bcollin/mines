# Mines
#
# Copyright 2025, Branko Collin

from tkinter import *
import tkinter.font as font
import time, pathlib, datetime, json

gridWidth = 9
gridHeight = 9
clock = 0
gameState = 'playing' # Can receive clicks on the board.
levels = {'easy': 0.14, 'meh': 0.156, 'hard': 0.206}
colours = {
    'black': 'black', # Do not use colours['black'], just write 'black'.
    'white': 'white', # Id.
    'anthracite': '#606060',
    'dark grey': '#808080',
    'middle grey': '#a5a5a5',
    'light grey': '#c6c6c6',
    'signal bad': '#cc0000',
    'signal good': '#00cc00',
    }

# Retrieve the level of the current game.
def getLevel():
    global gridWidth
    if gridWidth < 10:
        return 'easy'
    elif gridWidth > 25:
        return 'hard'
    else:
        return 'meh'

# Read highscores from a file.
def readHighscores(path):
    try:
        with open(path, 'r') as f:
            h = json.load(f)
            return h
    except Exception as error:
        print ('Error: ', error)
        return {}

# Read configuration from a file.
def readConfiguration(path):
    try:
        with open(path, 'r') as f:
            d = json.load(f)
            return d
    except Exception as error:
        print ('Error: ', error)
        return {}

# Store highscores in a file.
def saveHighscores(path):
    global highscores
    try:
        with open(path, 'w') as f:
            json.dump(highscores, f)
    except Exception as error:
        print('Error: highscores werent saved because of:', error)

# Add the winning score to a highscores list.
# Warning: the outer list (i.e. 'hs') may or may not be a copy,
# but the lists and dictonaries inside are not and are the same
# objects as the children of the 'highscores' global.
# This is probably fine, but if you change any children,
# you should be aware of the side-effects.
def extendScoreslist(hs, score, today):
    if score == {}:
        return (False, hs)
    if ('level' not in score) or ('time' not in score):
        return (False, hs)
    improvement = False
    level = score['level']
    time = score['time']
    if score['level'] not in hs:
        hs[level] = []
    hs[level].append({'score': time, 'date': today})
    hs[level] = sorted(hs[level], key=lambda d: d['date'])
    hs[level] = sorted(hs[level], key=lambda d: d['score'])
    if len(hs[level]) > 5:
        hs[level].pop()
    return (True, hs)

# Add the current score to the highscores list and save if needed.
def addHighscore(score={}):
    global highscores
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    result, temp = extendScoreslist(highscores, score, today)
    if not result:
        # Score could not be added to highscores, no need to save.
        return None
    saveHighscores(highscoreFilePath)

# Show the passed time in the status bar.
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

# Toggle the replay dialog.
def toggleReplayDialog():
    global gameState, replayFrame, replayFrameSettings
    if gameState == 'playing':
        replayFrame.pack_forget()
        replayDecoLeft.pack(side='left')
    else:
        replayFrame.pack(**replayFrameSettings)
        replayDecoLeft.pack_forget()

# Change the visible appearance of cell to that of one that has been
# cleared.
def drawFieldClear(field):
    global drawingField
    drawingField.itemconfig(field.elem[0], fill=colours['middle grey'])
    drawingField.itemconfig(field.elem[1], fill=colours['dark grey'])
    x1, y1, x2, y2 = drawingField.coords(field.elem[2])
    if int(x2-x1) == 34:
        drawingField.coords(field.elem[2])
        drawingField.coords(field.elem[2], x1-2, y1-2, x2+2, y2+2)
    if field.threatCount < 1:
        drawingField.itemconfig(field.elem[3], text = ' ') 
    else:
        drawingField.itemconfig(field.elem[3], text = field.threatCount, fill='#808080') 

# Used upon game end, hence the 'reason': the revelation of the
# bomb locations works slightly different for wins and losses.
def markAllBombs(reason = 'win'):
    if reason not in ['win', 'loss']:
        return None
    for y in range(len(uiTree)):
        for x in range(len(uiTree[y])):
            field = uiTree[y][x]
            if field.hasBomb:
                if reason == 'win':
                    drawingField.itemconfig(field.elem[3], text = 'P')
                else: 
                    drawingField.itemconfig(field.elem[3], text = 'X')
            elif reason == 'loss':
                drawFieldClear(field)

# Execute what is needed upon a win.
# If necessary, tear-down could be added to this function.
def doWin():
    global gameState, uiTree, statusMessage, statusVar, drawingField 
    if gameState == 'waiting':
        return None
    gameState = 'waiting' # Player must initiate new game
    toggleReplayDialog()
    statusVar.set('You won!')
    statusMessage.config(fg=colours['signal good'], font="-weight bold")
    addHighscore({'level': getLevel(), 'time': statusTimeVar.get()})
    # Flag the bombs.
    markAllBombs(reason = 'win')

# Execute what is needed upon a loss.
# If necessary, tear-down could be added to this function.
def doLose():
    global gameState, statusMessage, statusVar, uiTree, drawingField 
    gameState = 'waiting'
    toggleReplayDialog()
    statusVar.set('You la-la-lost...')
    statusMessage.config(fg=colours['signal bad'], font= "-weight bold")
    # Reveal the bombs.
    markAllBombs(reason = 'loss')

# Creates the visual representation of a single cell.
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
    sq1 = drawingField.create_polygon(x1, y1, x2, y1, x1, y2, fill='white', outline='')

    # Represents bottom and right edge
    sq2 = drawingField.create_polygon(x1, y2, x2, y2, x2, y1, fill=colours['anthracite'], outline='')

    # The clickable center.
    sq3 = drawingField.create_rectangle(x1+3, y1+3, x2-3, y2-3, fill=colours['light grey'], outline='')

    # Option to render a bomb symbol, a flag or a threat count.
    sq4 = drawingField.create_text(xt, yt, text = label, font=font)

    out = [sq1, sq2, sq3, sq4]

    return out

# Defines the state of a single cell and sets up the
# representation of the cell in the GUI.
class Field:
    def __init__(self, x, y):
        global gameFrame, drawingField
        self.x = x
        self.y = y
        self.visible = False
        self.hasFlag = False
        self.hasBomb = False
        self.threatCount = 0

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
        return (self.x, self.y)
    def setNeighboursWithBombs(self, num):
        self.threatCount = num
    def clearField(self):
        global fieldsToClear
        if not self.visible and \
        not self.hasFlag and \
        not self.hasBomb:
            fieldsToClear = fieldsToClear - 1
            self.visible = True
            drawFieldClear(self)
        if fieldsToClear < 1:
            doWin()
    # End of class Field.

# Returns True if a coordinate is on the board.
def inRange(value, direction = 'hor'):
    global gridWidth, gridHeight
    if direction == 'hor':
        if 0 <= value < gridWidth:
            return True
    if direction == 'ver':
        if 0 <= value < gridHeight:
            return True
    return False

# Count the number of neighbouring cells that have bombs.
def neighboursWithBombs(x, y, board):
    bombs = 0
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0) and inRange(x+i, 'hor') and inRange(y+j, 'ver'):
                if board[y+j][x+i].hasBomb:
                    bombs = bombs + 1
    return bombs

# Clear neihbouring cells if they are clearable.
# This seems to use a different definition of
# 'clearable' than other games of the same type.
def openNeighbours(x, y, grid):
    global uiTree
    grid[y][x] = 1
    for j in range(-1,2):
        for i in range(-1,2):
            if not (i == 0 and j == 0):
                if inRange(x+i, 'hor') and inRange(y+j, 'ver') and grid[y+j][x+i] != 1:
                    thisField = uiTree[y+j][x+i]
                    if not thisField.visible:
                        thisField.clearField()
                    if uiTree[y+j][x+i].threatCount == 0:
                        openNeighbours(x+i, y+j, grid)

# Callback for the LMB.
def leftClickField(event, x, y):
    global ui, uiTree, testGrid, gameState, clock
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

# Callback for the RMB.
def rightClickField(event, x, y):
    global uiTree, gameState
    if gameState == 'waiting':
        return None
    field = uiTree[y][x]
    if not field.visible:
        field.toggleFlag()
        if field.hasFlag:
            drawingField.itemconfig(field.elem[3], text='P')
        else:
            drawingField.itemconfig(field.elem[3], text=' ')

# Rounds float inVal down, e.g. 3.9 => 3.
def floor(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(inVal)

# Rounds float inVal up, e.g. 3.1 => 4
def ceil(inVal):
    if not isinstance(inVal, float):
        inVal = float(inVal)
    return int(floor(inVal)+1)
    
# Randomly add a number of bombs to a hithertofore empty board.
#
# This function can be greatly improved. Currently it just
# generates 1000 random coordinates and adds a bomb to them
# until the number of bombs has reached the limit for the
# difficulty level. Theoretically it may happen that the
# 1000 coordinate count has been reached before the limit
# for the difficulty level has been reached. Also generating
# 1000 coordinates is a bit overkill for the smaller
# boards.
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
            bombsPlanted = bombsPlanted + 1
        attempts = attempts + 1
    return bombsPlanted

# Game set-up at the start of a round.
def setUp(level='easy'):
    global uiTree, gameFrame, drawingField, testGrid, gridWidth, gridHeight, fieldsToClear, statusVar, gameState, statusMessage, clock, statusTimeVar, highscores

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
    statusMessage.config(fg='black', font="-weight normal")
    gameState = 'playing'
    toggleReplayDialog()
    clock = 0
    statusTimeVar.set('00.00')

# Pre-set-up after a round. I am not sure if this needs
# to exist if we already run either doWin() or doLose() and
# follow it up by setUp().
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

replayFrameWrapper = Frame(ui, height=32, bd=0)
replayFrameWrapper.pack(expand=True, fill=BOTH, side=TOP)

replayDecoLeftImg = PhotoImage(file='assets/decoration-1-32-left-trans.png')
replayDecoLeft = Label(replayFrameWrapper, image=replayDecoLeftImg, bd=0)
replayDecoLeft.pack(side='left')

replayDecoRightImg = PhotoImage(file='assets/decoration-1-32-right-trans.png')
replayDecoRight = Label(replayFrameWrapper, image=replayDecoRightImg, bd=0)
replayDecoRight.pack(side='right')

replayFrameSettings = {'side': 'top', 'expand': True, 'fill': 'x'}
replayFrame = Frame(replayFrameWrapper, height=32)
replayFrame.pack(replayFrameSettings)

replayMessage = Label(replayFrame, text = 'Play again?')
replayMessage.pack(side='left')

replayButton1 = Button(replayFrame, text = '9×9', command = lambda: restartGame('easy'))
replayButton1.pack(side='left', padx=(4,0), pady=2)

replayButton2 = Button(replayFrame, text = '16×16', command = lambda: restartGame('meh'))
replayButton2.pack(side='left', padx=(4,0), pady=2)

replayButton3 = Button(replayFrame, text = '30×16', command = lambda: restartGame('hard'))
replayButton3.pack(side='left', padx=(4,0), pady=2)

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

confFilePath = confDir / 'user.conf'
conf = readConfiguration(confFilePath)

start_level = 'easy'
if 'level' in conf:
    temp = conf['level']
    if temp in levels:
        start_level = temp

setUp(start_level)

if __name__=='__main__':
    ui.mainloop()


