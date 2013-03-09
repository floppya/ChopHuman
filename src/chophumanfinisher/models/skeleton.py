""" 
Various, skeleton-related models.
NOTE: At this point, only the Limb class and its skeletal definitions are used. 
"""
import math
from PyQt4 import QtCore


TWO_PI = 2 * math.pi
DEGREE_TO_RADIAN = math.pi / 180.0
RADIAN_TO_DEGREE = 180.0 / math.pi
FULL_CIRCLE = 360.0
HALF_CIRCLE = 180.0


def normalizeAngle(angle):
    angle %= FULL_CIRCLE
    if angle < 0:
        angle += FULL_CIRCLE
    return angle


def _lerp(v0, v1, t):
    return v0 + t * (v1 - v0)


def _lerpAngle(a0, a1, t, spin):
    angle = 0.0
    if spin != 0:
        if spin > 0 and a0 > a1:
            angle = _lerp(a0, a1 + FULL_CIRCLE, t)
        elif spin < 0 and a0 < a1:
            angle = _lerp(a0, a1 - FULL_CIRCLE, t)
        else:
            angle = _lerp(a0, a1, t)
    else:
        if abs(a0 - a1) > HALF_CIRCLE:
            a1 += FULL_CIRCLE
        angle = _lerp(a0, a1, t)
    return angle


class Transform(object):
    x = 0
    y = 0
    angle = 0.0
    scaleX = 1.0
    scaleY = 1.0
    spin = 0
    
    @property
    def angleRadians(self):
        return self.angle * DEGREE_TO_RADIAN
    
    def copy(self, other):
        self.x = other.x
        self.y = other.y
        self.angle = other.angle
        self.scaleX = other.scaleX
        self.scaleY = other.scaleY
        self.spin = other.spin

    def clone(self):
        transform = Transform()
        transform.copy(self)
        return transform

    def interpolate(self, transform0, transform1, t, shortest=False):
        self.x = _lerp(transform0.x, transform1.x, t)
        self.y = _lerp(transform0.y, transform1.y, t)
        self.spin = transform0.spin
        if shortest:
            spin = 0
        else:
            spin = self.spin
        self.angle = _lerpAngle(transform0.angle, transform1.angle, t, spin)
        self.scaleX = _lerp(transform0.scaleX, transform1.scaleX, t)
        self.scaleY = _lerp(transform0.scaleY, transform1.scaleY, t)

    def applyTransform(self, other):
        self.x *= other.scaleX
        self.y *= other.scaleY 
        pc = math.cos(other.angle * DEGREE_TO_RADIAN)
        ps = math.sin(other.angle * DEGREE_TO_RADIAN)
        newX = other.x + self.x * pc - self.y * ps
        newY = other.y + self.x * ps + self.y * pc
        self.x = newX
        self.y = newY
        self.angle += other.angle
        self.scaleX *= other.scaleX
        self.scaleY *= other.scaleY
        return self
    
    def invert(self):
        t = Transform()
        t.scaleX = 1.0 / self.scaleX
        t.scaleY = 1.0 / self.scaleY
        t.angle = -self.angle
        t.x = -self.x
        t.y = -self.y
        return t
    
    def add(self, t0, t1):
        self.x = t1.x + t0.x
        self.y = t1.y + t0.y
        self.angle = t1.angle + t0.angle
        self.scaleX = t1.scaleX + t0.scaleX
        self.scaleY = t1.scaleY + t0.scaleY
        self.spin = 0 # TODO: what to do with spin?
    
    def subtract(self, t0, t1):
        self.x = t1.x - t0.x
        self.y = t1.y - t0.y
        self.angle = t1.angle - t0.angle
        self.scaleX = t1.scaleX - t0.scaleX
        self.scaleY = t1.scaleY - t0.scaleY
        self.spin = 0 # TODO: what to do with spin?



class SceneObject(object):
    id = None
    name = ''
    parent = None
    children = None
    transform = None

    def __init__(self):
        self.children = []
        self.transform = Transform()

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

    def copy(self, other):
        self.parent = other.parent
        self.name = other.name
        self.transform.copy(other.transform)

    def clone(self):
        pass
    
    def interpolate(self, obj0, obj1, t, shortest=False):
        self.parent = obj0.parent
        self.name = obj0.name
        self.transform.interpolate(obj0.transform, obj1.transform, t, shortest)

    def combineSelf(self, other, shortest=False):
        self.combine(self, other, shortest)

    def combine(self, obj0, obj1, shortest=False):
        self.transform.add(obj0.transform, obj1.transform)

    def difference(self, obj0, obj1, shortest=False):
        self.transform.subtract(obj0.transform, obj1.transform)


class Bone(SceneObject):
    def copy(self, other):
        super(Bone, self).copy(other)

    def clone(self):
        bone = Bone()
        bone.copy(self)
        return bone


class Skin(SceneObject):
    diffusemap = None
    normalmap = None
    mask = None
    pivotX = 0.0
    pivotY = 0.0
    opacity = 1.0
    zIndex = 0

    def copy(self, other):
        super(Skin, self).copy(other)
        self.pivotX = other.pivotX
        self.pivotY = other.pivotY
        self.opacity = other.opacity
        self.zIndex = other.zIndex

    def clone(self):
        skin = Skin()
        skin.copy(self)
        return skin

    def interpolate(self, skin0, skin1, t, shortest=False):
        super(Skin, self).interpolate(skin0, skin1, t, shortest)
        self.pivotX = _lerp(skin0.pivotX, skin1.pivotX, t)
        self.pivotY = _lerp(skin0.pivotY, skin1.pivotY, t)
        self.opacity = _lerp(skin0.opacity, skin1.opacity, t)
        self.zIndex = skin0.zIndex

    def combine(self, obj0, obj1, shortest=False):
        super(Skin, self).combine(obj0, obj1, shortest)
        self.pivotX = obj1.pivotX + obj0.pivotX
        self.pivotY = obj1.pivotY + obj0.pivotY
        self.opacity = obj1.opacity + obj0.opacity

    def difference(self, obj0, obj1, shortest=False):
        super(Skin, self).difference(obj0, obj1, shortest)
        self.pivotX = obj1.pivotX - obj0.pivotX
        self.pivotY = obj1.pivotY - obj0.pivotY
        self.opacity = obj1.opacity - obj0.opacity


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
        pass
