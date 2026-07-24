import math

def sysCall_init():
    sim = require('sim')

    # Joints
    self.j1 = sim.getObject('/joint1_base')
    self.j2 = sim.getObject('/joint2_arm')
    self.j3 = sim.getObject('/joint3_gripper')

    # Magnet and Piece
    self.magnet = sim.getObject('/magnet')
    self.piece = sim.getObject('/piece1')
    moveRobot(self,20,60,10)
    attachPiece(self)
def moveRobot(self, j1, j2, j3):
    sim = require('sim')

    sim.setJointPosition(self.j1, math.radians(j1))
    sim.setJointPosition(self.j2, math.radians(j2))
    sim.setJointPosition(self.j3, math.radians(j3))
def attachPiece(self):
    sim = require('sim')

    pos = sim.getObjectPosition(self.magnet, -1)
    sim.setObjectPosition(self.piece, -1, pos)
    sim.setObjectParent(self.piece, self.magnet, True)
def detachPiece(self):
    sim = require('sim')

    sim.setObjectParent(self.piece, -1, True)