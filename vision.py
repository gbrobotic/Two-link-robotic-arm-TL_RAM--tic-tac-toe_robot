import cv2
import numpy as np
def captureFrame():
    img, res = sim.getVisionSensorImg(camera)

    frame = np.frombuffer(img, dtype=np.uint8)
    frame = frame.reshape(res[1], res[0], 3)

    frame = cv2.flip(frame, 0)          # CoppeliaSim image upside-down hoti hai
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    return frame

def readBoard():

    # Robot must always read board from HOME
    # moveTo(HOME)
    # time.sleep(0.5)

    frame = captureFrame()

    # Board matrix

    board = detectBoard(frame)


    return board
def detectBoard(frame):

    board = [[' ' for _ in range(5)] for _ in range(5)]

    h, w = frame.shape[:2]

    # Approximate board region (baad me calibrate karenge)
    startX = 75
    startY = 40

    boardWidth = 360
    boardHeight = 360

    cellW = boardWidth // 5
    cellH = boardHeight // 5

    for row in range(5):
        for col in range(5):

            x = startX + col * cellW
            y = startY + row * cellH

            cv2.rectangle(
                frame,
                (x, y),
                (x + cellW, y + cellH),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{row},{col}",
                (x + 10, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

    cv2.imshow("Board", frame)

    return board