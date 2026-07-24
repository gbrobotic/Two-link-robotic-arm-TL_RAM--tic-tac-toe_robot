from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import time
import cv2
import numpy as np
from ai import (
    HUMAN,
    ROBOT,
    EMPTY,
    countThreats,
    findWinningMove,
    findForkMove,
    getCandidates,
    FindBestMove,
    minimax,
    Winner,
    evaluate,
)
from pose import *
import json
import os
# ==========================================================
# Connect to CoppeliaSim
# ==========================================================

client = RemoteAPIClient()
sim = client.require('sim')

# ==========================================================
# Robot Handles
# ==========================================================

j1 = sim.getObject('/joint1_base')
j2 = sim.getObject('/joint2_arm')
j3 = sim.getObject('/joint3_gripper')

magnet = sim.getObject('/magnet')
# piece = sim.getObject('/piece1')

camera = sim.getObject('/camera')
redPieces = []
bluePieces = []

for i in range(13):
    redPieces.append(sim.getObject(f'/redPiece{i}'))
    bluePieces.append(sim.getObject(f'/bluePiece{i}'))

nextRedPiece = 0
nextBluePiece = 0
# ==========================================================
# Pose Dictionaries
# ==========================================================

CELL_POSES = {

    (0,0): CELL00,
    (0,1): CELL01,
    (0,2): CELL02,
    (0,3): CELL03,
    (0,4): CELL04,

    (1,0): CELL10,
    (1,1): CELL11,
    (1,2): CELL12,
    (1,3): CELL13,
    (1,4): CELL14,

    (2,0): CELL20,
    (2,1): CELL21,
    (2,2): CELL22,
    (2,3): CELL23,
    (2,4): CELL24,

    (3,0): CELL30,
    (3,1): CELL31,
    (3,2): CELL32,
    (3,3): CELL33,
    (3,4): CELL34,

    (4,0): CELL40,
    (4,1): CELL41,
    (4,2): CELL42,
    (4,3): CELL43,
    (4,4): CELL44
}

STORAGE_POSES = {

    0: STORAGE00,
    1: STORAGE01,
    2: STORAGE02,
    3: STORAGE03,
    4: STORAGE04,
    5: STORAGE05,
    6: STORAGE06,

    7: STORAGE10,
    8: STORAGE11,
    9: STORAGE12,
    10: STORAGE13,
    11: STORAGE14,
    12: STORAGE15,
    13: STORAGE16
}

CELL_POSITIONS = {

    (0,0): (0.04781, -0.07686, 0.00932),
    (0,1): (0.02381, -0.07686, 0.00932),
    (0,2): (-0.00019, -0.07686, 0.00932),
    (0,3): (-0.02419, -0.07686, 0.00932),
    (0,4): (-0.04819, -0.07686, 0.00932),

    (1,0): (0.04781, -0.05286, 0.00932),
    (1,1): (0.02381, -0.05286, 0.00932),
    (1,2): (-0.00019, -0.05286, 0.00932),
    (1,3): (-0.02419, -0.05286, 0.00932),
    (1,4): (-0.04819, -0.05286, 0.00932),

    (2,0): (0.04781, -0.02886, 0.00932),
    (2,1): (0.02381, -0.02886, 0.00932),
    (2,2): (-0.00019, -0.02886, 0.00932),
    (2,3): (-0.02419, -0.02886, 0.00932),
    (2,4): (-0.04819, -0.02886, 0.00932),

    (3,0): (0.04781, -0.00486, 0.00932),
    (3,1): (0.02381, -0.00486, 0.00932),
    (3,2): (-0.00019, -0.00486, 0.00932),
    (3,3): (-0.02419, -0.00486, 0.00932),
    (3,4): (-0.04819, -0.00486, 0.00932),

    (4,0): (0.04781,  0.01914, 0.00932),
    (4,1): (0.02381,  0.01914, 0.00932),
    (4,2): (-0.00019,  0.01914, 0.00932),
    (4,3): (-0.02419,  0.01914, 0.00932),
    (4,4): (-0.04819,  0.01914, 0.00932),
}
# ==========================================================
# Robot Motion
# ==========================================================
bluePieceIndex = 0
def moveTo(target):

    current = [

        math.degrees(sim.getJointPosition(j1)),
        math.degrees(sim.getJointPosition(j2)),
        math.degrees(sim.getJointPosition(j3))

    ]

    step = 1

    while True:

        finished = True

        for i in range(3):

            if abs(target[i] - current[i]) > step:

                finished = False

                if target[i] > current[i]:
                    current[i] += step
                else:
                    current[i] -= step

            else:
                current[i] = target[i]

        sim.setJointPosition(j1, math.radians(current[0]))
        sim.setJointPosition(j2, math.radians(current[1]))
        sim.setJointPosition(j3, math.radians(current[2]))

        time.sleep(0.03)

        if finished:
            break


# ==========================================================
# Magnet Control
# ==========================================================

def attachPiece(piece):

    pos = sim.getObjectPosition(magnet, -1)

    sim.setObjectPosition(piece, -1, pos)
    sim.setObjectParent(piece, magnet, True)


def detachPiece(piece):

    sim.setObjectParent(piece, -1, True)


# ==========================================================
# Pick From Storage
# ==========================================================

def pickFromStorage(storagePose,piece):

    moveTo(storagePose)

    pickPose = (

        storagePose[0],
        storagePose[1],
        -10

    )

    moveTo(pickPose)

    attachPiece(piece)

    moveTo(storagePose)


# ==========================================================
# Place On Board
# ==========================================================

def placeAt(cellPose,piece):

    moveTo(cellPose)

    placePose = (

        cellPose[0],
        cellPose[1],
        -10

    )

    moveTo(placePose)

    detachPiece(piece)

    moveTo(cellPose)

def robotMove(row, col):

    global bluePieceIndex

    if bluePieceIndex >= 14:
        print("No blue pieces left!")
        return
    piece = bluePieces[bluePieceIndex]
    storagePose = STORAGE_POSES[bluePieceIndex]
    cellPose = CELL_POSES[(row, col)]

    # Storage se piece uthao
    pickFromStorage(storagePose,piece)

    # Board par rakho
    placeAt(cellPose,piece)

    bluePieceIndex += 1
import numpy as np
import cv2

def showWinner(winner):

    img = np.ones((250, 500, 3), dtype=np.uint8) * 255

    if winner == ROBOT:
        text = "ROBOT WINS!"
        color = (255, 0, 0)      # Blue

    elif winner == HUMAN:
        text = "HUMAN WINS!"
        color = (0, 0, 255)      # Red

    else:
        text = "DRAW!"
        color = (0, 150, 0)      # Green

    cv2.putText(
        img,
        text,
        (40, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        color,
        3
    )

    cv2.imshow("Game Result", img)

    cv2.waitKey(0)
def moveJoint3(targetAngle):

    current = math.degrees(sim.getJointPosition(j3))

    step = 1

    while abs(current - targetAngle) > step:

        if targetAngle > current:
            current += step
        else:
            current -= step

        sim.setJointPosition(j3, math.radians(current))

        time.sleep(0.03)

    sim.setJointPosition(j3, math.radians(targetAngle))
# ==========================================================
# Vision System
# ==========================================================
def placeHumanPiece(row, col):

    global nextRedPiece

    if nextRedPiece >= len(redPieces):
        print("No Red Pieces Left")
        return

    piece = redPieces[nextRedPiece]

    sim.setObjectPosition(
        piece,
        -1,
        CELL_POSITIONS[(row, col)]
    )

    nextRedPiece += 1
clickedPoints = []
cellCenters = []
selectedCell = None
def getClickedCell(x, y):
    if len(cellCenters) != 25:
        print("Cell centers not ready!")
        return None
    minDist = 100000

    bestCell = None

    for row in range(5):
        for col in range(5):

            cx, cy = cellCenters[row * 5 + col]

            d = (cx - x) ** 2 + (cy - y) ** 2

            if d < minDist:
                minDist = d
                bestCell = (row, col)

    return bestCell
def mouseCallback(event, x, y, flags, param):

    global clickedPoints
    global selectedCell
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if len(clickedPoints) < 4:

            clickedPoints.append((x, y))

            print(f"Point {len(clickedPoints)} : ({x}, {y})")
         
            if len(clickedPoints) == 4:
                saveCalibration()   
    else:
        selectedCell = getClickedCell(x, y)
def saveCalibration():

    data = {
        "clickedPoints": clickedPoints
    }

    with open("calibration.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Calibration Saved.")
def loadCalibration():

    global clickedPoints

    if os.path.exists("calibration.json"):

        with open("calibration.json", "r") as f:

            data = json.load(f)

        clickedPoints = [tuple(p) for p in data["clickedPoints"]]

        print("Calibration Loaded.")

    else:

        print("No Calibration File Found.")
# ----------------------------------------------------------

def captureFrame():

    img, res = sim.getVisionSensorImg(camera)

    frame = np.frombuffer(img, dtype=np.uint8)

    frame = frame.reshape(res[1], res[0], 3)

    frame = cv2.flip(frame, 0)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    return frame


# ----------------------------------------------------------

def detectBoard(frame):

    board = [[' ' for _ in range(5)] for _ in range(5)]

    # Calibration not done
    if len(clickedPoints) != 4:
        cv2.imshow("Board", frame)
        return board

    cellCenters.clear()

    TL = np.array(clickedPoints[0], dtype=float)
    TR = np.array(clickedPoints[1], dtype=float)
    BL = np.array(clickedPoints[2], dtype=float)
    BR = np.array(clickedPoints[3], dtype=float)

    roiSize = 50

    for row in range(5):

        left = TL + (BL - TL) * (row / 4)
        right = TR + (BR - TR) * (row / 4)

        for col in range(5):

            center = left + (right - left) * (col / 4)

            x = int(center[0])
            y = int(center[1])

            cellCenters.append((x, y))

            # ROI Coordinates
            x1 = max(0, x - roiSize // 2)
            y1 = max(0, y - roiSize // 2)

            x2 = min(frame.shape[1], x + roiSize // 2)
            y2 = min(frame.shape[0], y + roiSize // 2)

            roi = frame[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            # Circular Mask
            mask = np.zeros(roi.shape[:2], dtype=np.uint8)

            cv2.circle(
                mask,
                (roi.shape[1] // 2, roi.shape[0] // 2),
                10,
                255,
                -1
            )

            # Average Color
            b, g, r, _ = cv2.mean(roi, mask=mask)

            # -------------------------
            # Piece Detection
            # -------------------------

            if r > 150 and g < 100 and b < 100:

                board[row][col] = 'X'

            elif b > 120 and r < 100 and g < 100:

                board[row][col] = 'O'

            else:

                board[row][col] = ' '

            # Draw only X/O
            cv2.putText(
                frame,
                board[row][col],
                (x - 10, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

    cv2.imshow("Board", frame)

    return board

# ----------------------------------------------------------

def getBoardState():

    moveTo(HOME)

    time.sleep(0.3)

    frame = captureFrame()

    board = detectBoard(frame)
    return board    


candidates = []


# def isValidPos(r, c):
#     return 0 <= r < 5 and 0 <= c < 5


# def getCandidates(board):

#     global candidates

#     candidates = []

#     hasPlayed = False

#     visited = [[False for _ in range(5)] for _ in range(5)]

#     for i in range(5):
#         for j in range(5):

#             if board[i][j] != EMPTY:

#                 hasPlayed = True

#                 for di in range(-1, 2):
#                     for dj in range(-1, 2):

#                         ni = i + di
#                         nj = j + dj

#                         if (
#                             isValidPos(ni, nj)
#                             and board[ni][nj] == EMPTY
#                             and not visited[ni][nj]
#                         ):

#                             visited[ni][nj] = True
#                             candidates.append((ni, nj))

#     if not hasPlayed:
#         candidates.append((2, 2))

#     return candidates
# ==========================================================
# Main
# ==========================================================

print("Starting Robot...")

cv2.namedWindow("Board")
cv2.setMouseCallback("Board", mouseCallback)
loadCalibration()
print("-------------------------------------")
print("Mouse Calibration")
print("-------------------------------------")
print("Click in this order:")
print("1 -> Cell (0,0)")
print("2 -> Cell (0,4)")
print("3 -> Cell (4,0)")
print("4 -> Cell (4,4)")
print("")
print("Press R to reset calibration")
print("Press ESC to exit")
print("-------------------------------------")

board = [[' ']*5 for _ in range(5)]

while True:

    key=cv2.waitKey(20)&0xFF

    frame=captureFrame()

    detectBoard(frame)    
    if selectedCell is not None:

        row, col = selectedCell
    
        placeHumanPiece(row, col)

        board = getBoardState()

        winner = Winner(board)

        if winner != EMPTY:
            print("Game Over!", winner)
            selectedCell = None
            continue
        
        move = FindBestMove(board)

        print("AI Move =", move)

        if move is not None:
        
            aiRow, aiCol = move

            robotMove(aiRow, aiCol)

            board = getBoardState()

            winner = Winner(board)

            if winner != EMPTY:
                showWinner(winner)
                print("Game Over! WINNER:", winner)
                break
        selectedCell = None
    if key==ord('c'):

        board=getBoardState()
        print(Winner(board))
        for row in board:
            print(row)

    elif key==27:
        break

cv2.destroyAllWindows()


