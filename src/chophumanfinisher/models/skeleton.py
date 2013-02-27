""" 
Various, skeleton-related models.
NOTE: At this point, only the Limb class and its skeletal definitions are used. 
"""
from PyQt4 import QtCore, QtGui


class Transform2d(object):
    x = 0
    y = 0
    angle = 0.0
    scaleX = 1.0
    scaleY = 1.0
        
    
class SceneObject(object):
    id = None
    name = ''
    parent = None
    children = None
    transform = None

    def __init__(self):
        self.children = []
        self.transform = Transform2d()

    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def removeChild(self, child):
        self.children.remove(child)
        child.parent = None

    def childCount(self):
        return len(self.children)

    def indexOf(self, child):
        self.children.index(child)

    def row(self):
        if self.parent:
            return self.parent.indexOf(self)
        return 0

    def data(self, column):
        return self.name

    def columnCount(self):
        return 1


class Bone(SceneObject):
    pass


class Skin(SceneObject):
    diffusemap = None
    normalmap = None
    mask = None
    pivotX = 0.0
    pivotY = 0.0
    opacity = 1.0
    zIndex = 0


class Limb(object):
    id = -1
    name = ''
    parent = None
    skin = None
    bone = None
    children = None

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        
    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def removeChild(self, child):
        self.children.remove(child)
        child.parent = None

    def childCount(self):
        return len(self.children)

    def indexOf(self, child):
        self.children.index(child)

    def row(self):
        if self.parent:
            return self.parent.indexOf(self)
        return 0

    @classmethod
    def stubSkeletonFromConfig(cls, limb_config):
        return _getStubLimbs('root', limb_config)

    @classmethod
    def stubHumanSkeleton(cls):
        return _getStubLimbs('root', HUMAN_LIMB_CONFIG)


HUMAN_LIMB_CONFIG = {
    'torso': {
        'head': {},
        'left_arm': {
            'left_hand': {}
        },
        'right_arm': {
            'right_hand': {}
        },
        'left_upper_leg': {
            'left_lower_leg': {
                'left_foot': {}
            }
        },
        'right_upper_leg': {
            'right_lower_leg': {
                'right_foot': {}
            }
        }
    }
}

HUMAN_LIMB_ORDER = (
    'left_arm', 'left_hand',
    'left_upper_leg', 'left_lower_leg', 'left_foot',
    'head',
    'torso',
    'right_upper_leg', 'right_lower_leg', 'right_foot',
    'right_arm', 'right_hand'
)

TORSO_LIMB_ORDER = (
    ('left_arm', 'left_upper_leg', 'head'), # behind torso
    ('right_upper_leg', 'right_arm') # front of torso
)
        

def _getStubLimbs(name, children):
    limb = Limb(name)
    for childName, childChildren in children.items():
        child = _getStubLimbs(childName, childChildren)
        limb.addChild(child)
    return limb


class SkeletonModel(QtCore.QAbstractItemModel):
    rootBone = None
    
    def __init__(self, rootBone, parent=None):
        self.rootBone = rootBone
        super(SkeletonModel, self).__init__(parent)

    def data(self, index, role):
        pass

    def flags(self, index):
        pass

    def headerData(self, section, orientation, role):
        pass

    def index(self, row, column, parent):
        pass

    def parent(self, index):
        pass

    def rowCount(self, parent):
        pass

    def columnCount(self, parent):
        passs
