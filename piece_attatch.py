def sysCall_init():
    sim = require('sim')

    self.magnet = sim.getObject('/magnet')
    self.piece = sim.getObject('/piece1')

    pos = sim.getObjectPosition(self.magnet, -1)
    sim.setObjectPosition(self.piece, -1, pos)
    sim.setObjectParent(self.piece, self.magnet, True)

def sysCall_actuation():
    pass

def sysCall_sensing():
    pass

def sysCall_cleanup():
    pass