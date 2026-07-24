from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from pynput import keyboard
import math

# Connect to CoppeliaSim
client = RemoteAPIClient()
sim = client.require('sim')

# Robot joints
j1 = sim.getObject('/joint1_base')
j2 = sim.getObject('/joint2_arm')
j3 = sim.getObject('/joint3_gripper')
magnet = sim.getObject('/magnet')
piece = sim.getObject('/bluePiece0')   # jis piece ko calibrate karna hai
print("Connected to CoppeliaSim")

# Read current angles
a1 = math.degrees(sim.getJointPosition(j1))
a2 = math.degrees(sim.getJointPosition(j2))
a3 = math.degrees(sim.getJointPosition(j3))

print(f"Current Pose: ({a1:.1f}, {a2:.1f}, {a3:.1f})")

def attachPiece():

    pos = sim.getObjectPosition(magnet, -1)

    sim.setObjectPosition(piece, -1, pos)
    sim.setObjectParent(piece, magnet, True)
    print("Piece Attached")

def detachPiece():

    sim.setObjectParent(piece, -1, True)
    print("Piece Detached")

def on_press(key):
    global a1, a2, a3

    try:
        # Joint 1
        if key.char == 'q':
            a1 += 1
            sim.setJointPosition(j1, math.radians(a1))

        elif key.char == 'a':
            a1 -= 1
            sim.setJointPosition(j1, math.radians(a1))

        # Joint 2
        elif key.char == 'w':
            a2 += 1
            sim.setJointPosition(j2, math.radians(a2))

        elif key.char == 's':
            a2 -= 1
            sim.setJointPosition(j2, math.radians(a2))

        # Joint 3
        elif key.char == 'e':
            a3 += 1
            sim.setJointPosition(j3, math.radians(a3))

        elif key.char == 'd':
            a3 -= 1
            sim.setJointPosition(j3, math.radians(a3))
        elif key.char == 't':
            attachPiece()
        
        elif key.char == 'g':
            detachPiece()
        # Print current pose
        elif key.char == 'p':
            print(f"\nPOSE = ({a1:.1f}, {a2:.1f}, {a3:.1f})\n")

    except AttributeError:
        pass


print("\n========== CONTROLS ==========")
print("Q / A : Joint1 + / -")
print("W / S : Joint2 + / -")
print("E / D : Joint3 + / -")
print("P     : Print current pose")
print("Ctrl+C: Exit")
print("==============================\n")
print("T     : Attach Piece")
print("G     : Detach Piece")
listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()