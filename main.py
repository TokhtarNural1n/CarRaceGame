# Importing various libraries
import threading
import tkinter
import random
import os
import simpleaudio as sa
from PIL import Image, ImageTk


# variables such as the size of the playing field, game status, game time, position of the player and enemies, etc.
VRM_WIDTH = 32
VRM_HEIGHT = 24

GAMESTATUS_TITLE = 0
GAMESTATUS_START = 1
GAMESTATUS_MAIN = 2
GAMESTATUS_MISS = 3
GAMESTATUS_OVER = 4

ENEMY_MAX = 5

gameStatus = GAMESTATUS_TITLE

gameTime = 0

KEY_LEFT = "Left"
KEY_RIGHT = "Right"
KEY_SPACE = "space"

basePath = os.path.abspath(os.path.dirname(__file__))

blankRow = [0] * VRM_WIDTH
vrm = [blankRow] * VRM_HEIGHT

indexOffset = 0
roadWidth = 12
roadX = 10
mx = 16
my = 20

ex = [0] * ENEMY_MAX
ey = [0] * ENEMY_MAX
ev = [0] * ENEMY_MAX
es = [0] * ENEMY_MAX

enemy_count = 0
score = 0

key = ""
keyOff = False


# processing pressing and releasing control keys.
def pressKey(e):
    global key, keyOff
    key = e.keysym
    keyOff = False
def releaseKey(e):
    global keyOff
    keyOff = True


# handles pressing the space bar to start the game.
def title():
    global gameStatus, gameTime, score, mx, my, roadWidth, roadX, enemy_count, vrm
    # Check if the spacebar was pressed
    if mouse_clicked:
        score = 0
        # Set the initial coordinates of the player
        mx = 16
        my = 20
        # Reset the statuses of all enemies
        for i in range(0, ENEMY_MAX):
            es[i] = 0
        enemy_count = 0
        roadWidth = 12
        roadX = 10
        # Update the playing field with empty values
        vrm = [blankRow] * VRM_HEIGHT
        # Set the game status to "game start"
        gameStatus = GAMESTATUS_START
        # Reset the game time to zero
        gameTime = 0

def mouse_click(event):
    global mouse_clicked
    mouse_clicked = True
mouse_clicked = False

# preparation for the start
def gameStart():
    global gameStatus, gameTime
    # If the game time is less than 24
    if gameTime < 24:
        # Generate the initial road, but don't move it
        generateRoad(False)

    # If exactly 50 game units of time have passed
    if gameTime == 50:
        # Set the game status to "main game"
        gameStatus = GAMESTATUS_MAIN
        # Reset the game time to zero
        gameTime = 0


# gameplay including road generation, player and enemy movement, and scoring.
def gameMain():
    global score

    generateRoad()
    movePlayer()
    moveEnemy()
    score = score + 1

# road generation
def generateRoad(isMove=True):
    global roadX, indexOffset

    if isMove == True:
        v = random.randint(0, 2) - 1
        if (roadX + v > 0 and roadX + v < VRM_WIDTH - roadWidth - 1):
            roadX = roadX + v

    newRow = [2] * VRM_WIDTH
    for w in range(roadWidth):
        newRow[roadX + w] = 0
    newRow[roadX - 1] = 1
    newRow[roadX + roadWidth] = 1

    indexOffset -= 1
    if indexOffset < 0:
        indexOffset = VRM_HEIGHT - 1

    vrm[indexOffset] = newRow

 # moving a car along the road
def movePlayer():
    global gameStatus, gameTime, mx

    if key == KEY_LEFT and mx > 0:
        mx -= 1

    if key == KEY_RIGHT and mx < VRM_WIDTH:
        mx += 1

    ty = indexOffset + my
    if ty > VRM_HEIGHT - 1:
        ty = ty - VRM_HEIGHT

    if vrm[ty][mx] > 0:
        gameStatus = GAMESTATUS_MISS
        gameTime = 0


# movement of enemy vehicles
def moveEnemy():
    global gameStatus, gameTime, enemy_count

    if enemy_count < ENEMY_MAX and gameTime % 150 == 0:
        enemy_count += 1

    for e in range(enemy_count):
        if es[e] > 0:
            if es[e] == 2 and ey[e] < 15:
                if ex[e] > mx:
                    ex[e] -= 1
                if ex[e] < mx:
                    ex[e] += 1
            ey[e] = ey[e] + 1
            if ey[e] > 23:
                es[e] = 0
            if abs(ex[e] - mx) < 2 and abs(ey[e] - my) < 2:
                gameStatus = GAMESTATUS_MISS
                gameTime = 0

        else:
            if gameTime > 100 and random.randint(0, 10) > 8:
                ex[e] = roadX + random.randint(0, roadWidth)
                ey[e] = 0
                ev[e] = 0
                es[e] = random.randint(1, 2)


# handles the case of a player colliding with an enemy.
def miss():
    global gameStatus, gameTime

    if gameTime > 25:
        gameStatus = GAMESTATUS_OVER
        gameTime = 0

# end of the game and handles post-game actions.
def gameover():
    global gameStatus, gameTime

    if (gameTime > 10 and key == KEY_SPACE) or gameTime > 50:
        gameStatus = GAMESTATUS_TITLE
        gameTime = 0


# display of various game elements
def drawScreen():
    global gameTime

    canvas.delete("TEXT1")
    canvas.delete("BG1")
    canvas.delete("PLAYER")
    canvas.delete("ENEMY")

    if gameStatus == GAMESTATUS_START or gameStatus == GAMESTATUS_MAIN or gameStatus == GAMESTATUS_MISS:
        for row in range(VRM_HEIGHT):
            vrow = row + indexOffset
            if vrow > VRM_HEIGHT - 1:
                vrow = vrow - VRM_HEIGHT
            for col in range(VRM_WIDTH):
                canvas.create_image(gPos(col), gPos(row), image=img_chr[vrm[vrow][col]], tag="BG1")

    if gameStatus == GAMESTATUS_MAIN:
        canvas.create_image(gPos(mx), gPos(my), image=img_mycar, tag="PLAYER")
        for e in range(enemy_count):
            if es[e] > 0:
                canvas.create_image(gPos(ex[e]), gPos(ey[e]), image=img_othercar, tag="ENEMY")
    if gameStatus == GAMESTATUS_MISS:
        canvas.create_image(gPos(mx), gPos(my), image=img_bang, tag="PLAYER")

    if gameStatus == GAMESTATUS_TITLE:
        canvas.create_rectangle(0, 0, gPos(VRM_WIDTH), gPos(VRM_HEIGHT), fill="Black")
        writeText(12, 6, "CAR RACE", "TEXT1")
        writeText(6, 20, "PROGRAMMED BY SE 2307", "TEXT1")
        if gameTime < 25:
            writeText(14, 14, "START", "TEXT1")
        if gameTime < 25:
            writeText(14, 16, "EXIT", "TEXT1")
        if gameTime == 50:
            gameTime = 0
    if gameStatus == GAMESTATUS_START:
        if gameTime > 30 and gameTime < 50:
            writeText(14, 13, "START", "TEXT1")
    if gameStatus == GAMESTATUS_OVER:
        writeText(12, 11, "GAME OVER", "TEXT1")

    writeText(0, 0, "SCORE " + "{:06}".format(score), "TEXT1")

# outputting text to the game canvas
def writeText(x, y, str, tag="text1"):
    str = str.upper()

    for i in range(len(str)):
        o = ord(str[i])
        if o >= 48 and o <= 57:
            canvas.create_image(gPos(x + i), gPos(y), image=img_font[o - 48], tag=tag)
        if o >= 65 and o <= 90:
            canvas.create_image(gPos(x + i), gPos(y), image=img_font[o - 55], tag=tag)

# Loads images from files on disk.
def loadImage(filePath):
    img = Image.open(filePath).convert("RGBA")
    return img.resize((img.width * 2, img.height * 2), Image.NEAREST)

# converting coordinates to pixels
def gPos(value):
    return value * 8 * 2 + 8

# playing background music
def play_background_music():
    filename = "/Users/tokhtar/PycharmProjects/CarRaceGame/Music/music.wav"
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    while True:
        play_obj.wait_done()
        play_obj = wave_obj.play()

music_thread = threading.Thread(target=play_background_music)
music_thread.daemon = True
music_thread.start()


# controls the game loop, updating the game state and displaying changes on the screen.
def main():
    global gameTime, roadWidth, roadX, mx, key, keyOff

    gameTime += 1

    if gameStatus == GAMESTATUS_TITLE:
        title()

    if gameStatus == GAMESTATUS_START:
        gameStart()

    if gameStatus == GAMESTATUS_MAIN:
        gameMain()

    if gameStatus == GAMESTATUS_MISS:
        miss()

    if gameStatus == GAMESTATUS_OVER:
        gameover()

    drawScreen()

    if keyOff == True:
        key = ""
        keyOff = False

    root.after(50, main)


# Loading images for game objects and characters from a font.
root = tkinter.Tk()
root.geometry(str(gPos(VRM_WIDTH) - 8) + "x" + str(gPos(VRM_HEIGHT) - 8))
root.title("Tiny Car Race")
root.bind("<KeyPress>", pressKey)
root.bind("<KeyRelease>", releaseKey)
root.bind("<Button-1>", mouse_click)

canvas = tkinter.Canvas(width=gPos(VRM_WIDTH) - 8, height=gPos(VRM_HEIGHT) - 8)
canvas.pack()

img_mycar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "mycar.png"))
img_othercar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "othercar.png"))
img_bang = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "bang.png"))
img_chr = [
    ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "road.png")),
    ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "block.png")),
    ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "green.png"))
]

img_allfont = loadImage(basePath + os.sep + "Images" + os.sep + "font.png")
img_font = []
for w in range(0, img_allfont.width, 16):
    img = ImageTk.PhotoImage(img_allfont.crop((w, 0, w + 16, 16)))
    img_font.append(img)

main()
root.mainloop()
