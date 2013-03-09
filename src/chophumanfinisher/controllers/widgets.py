import math
from PyQt4 import QtCore, QtGui
from chophumanfinisher.models.skeleton import Bone, Skin


class LimbGraphicsItem(QtGui.QGraphicsItem):
    _boneItem = None
    _skinItem = None

    def __init__(self, parent=None):
        super(LimbGraphicsItem, self).__init__(parent)
        self.skinItem = SkinGraphicsItem()
        self.boneItem = BoneGraphicsItem()

    @property
    def bonePos(self):
        return self.boneItem.pos()
    
    @property
    def boneRotation(self):
        return self.boneItem.rotation()
    
    @property
    def mapToBone(self, item, pos):
        self.mapToItem(item, pos)

    @property
    def boneItem(self):
        return self._boneItem
    
    @boneItem.setter
    def boneItem(self, boneItem):
        self._boneItem = boneItem
        boneItem.setParentItem(self)
    
    @property
    def skinItem(self):
        return self._skinItem
    
    @skinItem.setter
    def skinItem(self, skinItem):
        self._skinItem = skinItem
        skinItem.setParentItem(self)
    
    @property
    def diffuseItem(self):
        return self.skinItem._diffuseItem
    
    @diffuseItem.setter
    def diffuseItem(self, diffuseItem):
        self.skinItem.diffuseItem = diffuseItem

    @property
    def normalItem(self):
        return self.skinItem.normalItem

    @normalItem.setter
    def normalItem(self, normalItem):
        self.skinItem.normalItem = normalItem

    def show(self):
        self.showBone()
        self.showSkin()

    def hide(self, opacity=0):
        self.hideBone(opacity=opacity)
        self.hideSkin(opacity=opacity)

    def showSkin(self):
        self.skinItem.show()

    def hideSkin(self, opacity=0):
        self.skinItem.hide(opacity=opacity)

    def showBone(self):
        self.boneItem.show()

    def hideBone(self, opacity=0):
        self.boneItem.hide(opacity=opacity)

    def editBone(self, isEditable):
        self.boneItem.isEditable = isEditable

    def pose(self, isPosing):
        self.boneItem.isEditable = isPosing
        self.boneItem.isPosing = isPosing

    def editSkin(self, isEditable):
        self.skinItem.isEditable = isEditable

    def paint(self, painter, option, widget):
        pass

    def boundingRect(self):
        skinBounds = self.skinItem.boundingRect()
        boneBounds = self.boneItem.boundingRect()
        return skinBounds.united(boneBounds)


class SkinGraphicsItem(QtGui.QGraphicsItemGroup):
    """
    This serves as a container for a limb's skins.
    """
    _diffuseItem = None
    _normalItem = None
    _clippingPath = None
    _isEditable = False

    def __init__(self, parent=None):
        super(SkinGraphicsItem, self).__init__(parent)
        self._clippingPath = QtGui.QPainterPath()
        self.setFlag(QtGui.QGraphicsItem.ItemClipsChildrenToShape, True)

    def shape(self):
        return self._clippingPath

    @property
    def diffuseItem(self):
        return self._diffuseItem
    
    @diffuseItem.setter
    def diffuseItem(self, diffuseItem):
        self._clippingPath = diffuseItem.opaqueArea()
        self._diffuseItem = diffuseItem
        diffuseItem.setParentItem(self)
        self.addToGroup(diffuseItem)
    
    @property
    def normalItem(self):
        return self._normalItem
    
    @normalItem.setter
    def normalItem(self, normalItem):
        self._normalItem = normalItem
        normalItem.setParentItem(self)
        self.addToGroup(normalItem)
    
    @property
    def isEditable(self):
        return self._isEditable

    @isEditable.setter
    def isEditable(self, newVal):
        self._isEditable = newVal

    def show(self, opacity=1):
        self.setVisible(True)
        self.setOpacity(opacity)

    def hide(self, opacity=0):
        if opacity == 0:
            self.setVisible(False)
        else:
            self.setOpacity(opacity)

    def addToMask(self, pos, width, height, unmask=False):
        halfWidth = width * 0.5
        halfHeight = height * 0.5
        thisPath = QtGui.QPainterPath()
        thisPath.addEllipse(pos, width, height)
        if unmask:
            self._clippingPath = self._clippingPath.united(thisPath)
        else:
            self._clippingPath = self._clippingPath.subtracted(thisPath)
        x = pos.x()
        y = pos.y()
        targetRect = QtCore.QRectF(x - halfWidth, y - halfHeight, x + halfWidth, y + halfHeight)
        if self.diffuseItem:
            self.diffuseItem.update(targetRect)
        if self.normalItem:
            self.normalItem.update(targetRect)


class MaskedSkinItem(QtGui.QGraphicsPixmapItem):
    """    
    Looks to its parent for a clip path.
    """
    def getClippedPixmap(self):
        """
        Returns a clipped copy of this image and and offset from the
        original, full image.
        TODO: I imagine there is a one or two-liner of Qt that can 
        replace this. 
        """
        clipPath = QtGui.QPainterPath(self.parentItem()._clippingPath)
        clipRect = clipPath.boundingRect()
        offset = clipRect.topLeft()
        clipPath.translate(-offset)
        clippedPix = QtGui.QPixmap(clipRect.size().toSize())
        clippedPix.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter()
        if painter.begin(clippedPix):
            painter.setClipPath(clipPath)
            painter.drawPixmap(QtCore.QPointF(), self.pixmap(), clipRect)
            painter.end()
        else:
            print('Failed to start painting MaskedSkinItem')
        return clippedPix, offset


class BoneGraphicsItem(QtGui.QGraphicsObject):
    """
    Here lies a hackfest of a QGraphicsItemGroup that graphically represents a bone.
    You can drag the pivot around and rotate/scale the tail. 
    """
    bone = None
    originPivotItem = None
    directionItem = None
    isDragging = False
    isRotating = False
    isEditable = False
    _isPosing = False
    pivotRadius = 20

    boneChanged = QtCore.pyqtSignal()

    def __init__(self, bone=None, parent=None):
        super(BoneGraphicsItem, self).__init__(parent)
        self.bone = bone
        self.setFlag(self.ItemIsMovable, True)
        pivotRadius = self.pivotRadius
        pivotRect = QtCore.QRectF(0, 0, pivotRadius, pivotRadius)
        self.originPivotItem = QtGui.QGraphicsEllipseItem(pivotRect)
        self.originPivotItem.translate(-0.5 * pivotRadius, -0.5 * pivotRadius)
        self.originPivotItem.setParentItem(self)

        self.directionItem = QtGui.QGraphicsRectItem()
        self.updateDirectionSize(50, pivotRadius * 0.5)
        self.directionItem.setParentItem(self)

    @property
    def isPosing(self):
        return self._isPosing
    
    @isPosing.setter
    def isPosing(self, val):
        self.isEditable = self._isPosing = val
        return val

    def updateDirectionSize(self, width, height):
        rect = QtCore.QRectF(0.0, -height * 0.5, width, height)
        self.directionItem.setRect(rect)

    def updateDirectionLength(self, length):
        self.updateDirectionSize(length, self.directionItem.rect().height())

    def mousePressEvent(self, event):
        """
        Drag or rotate and scale, depending on the distance from the pivot.
        """
        if self.isEditable:
            epos = event.pos()
            distance = epos.x() * epos.x() + epos.y() * epos.y()
            self.isDragging = distance < self.pivotRadius * self.pivotRadius
            self.isRotating = not self.isDragging
        else:
            event.ignore()
        super(BoneGraphicsItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isDragging = False
        self.isRotating = False
        super(BoneGraphicsItem, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.isDragging:
            super(BoneGraphicsItem, self).mouseMoveEvent(event)
            self.boneChanged.emit()
        elif self.isRotating:
            targetPos = self.mapFromScene(event.scenePos())
            targetDistance = math.sqrt(targetPos.x() ** 2 + targetPos.y() ** 2)
            if not self.isPosing:
                self.updateDirectionLength(targetDistance)
            if targetDistance != 0:
                angle = math.atan2(targetPos.y(), targetPos.x())
                angle = angle * 180 / math.pi
                self.setRotation(angle + self.rotation())
                #self.bone.transform.angle += angle
            self.boneChanged.emit()

    def show(self, opacity=1):
        self.setVisible(True)
        self.setOpacity(opacity)

    def hide(self, opacity=0):
        if opacity == 0:
            self.setVisible(False)
        else:
            self.setOpacity(opacity)

    def boundingRect(self):
        return self.directionItem.boundingRect().united(self.originPivotItem.boundingRect())
    
    def paint(self, *args, **kwargs):
        pass

    def updateFromBone(self):
        """Update the item transform from the bone"""
        pass
    
    def updateBone(self):
        """Update the bone from the item transform"""
        pass

    