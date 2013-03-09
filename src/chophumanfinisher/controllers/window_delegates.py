"""
ChopHumanDelegate subclasses define different modes of operation for the main window
and is the primary means of adding functionality to the program.
For now, they must also be configured in the main window.
"""

from PyQt4 import QtCore, QtGui


class ChopHumanDelegate(object):
    """
    Subclass this to add different editing modes.
    """
    delegateName = 'ChopHuman delegate'
    hotKey = 'a'

    def __init__(self, window):
        self.window = window
        self.action = None

    def enable(self):
        self.updateUI()

    def disable(self):
        pass

    def getEnableAction(self):
        if not self.action:
            self.action = action = QtGui.QAction(self.window)
            action.setCheckable(True)
            action.setChecked(False)
            action.setText(self.delegateName)
            action.triggered.connect(self._onEnableAction)
            if self.hotKey:
                action.setShortcut(self.hotKey)
        return self.action

    def _onEnableAction(self):
        self.window.delegate = self

    def onBoneSelected(self, current, previous):
        pass

    def onSceneMousePressEvent(self, event):
        pass

    def onSceneMouseMoveEvent(self, event):
        pass

    def onSceneMouseReleaseEvent(self, event):
        pass

    def updateUI(self):
        pass


class DefaultDelegate(ChopHumanDelegate):
    """
    This is the delegate which is used by default. Allows highlighting of Bones.
    """
    delegateName = 'View'
    hotKey = 'a'

    def onBoneSelected(self, current, previous):
        self.updateUI()

    def updateUI(self):
        item  = self.window.selectedBoneItem
        if item:
            self.window.highlightBone(item)
        else:
            self.window.unhighlightBone()


class PlaceBonesDelegate(ChopHumanDelegate):
    """
    This mode is used to arrange the bones relative to the skins.
    """
    delegateName = 'Place bones'
    hotKey = 's'

    def enable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(self.window.selectedBoneItem, None)
        self.window.pushCursor(QtCore.Qt.OpenHandCursor)

    def disable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(None, self.window.selectedBoneItem)
        self.window.popCursor()

    def onBoneSelected(self, current, previous):
        if previous:
            previous.isEditable = False
        if current:
            current.isEditable = True
        self.updateUI()

    def updateUI(self):
        skeletonItem = self.window.selectedSkeletonItem
        # update the skeleton tree view
        if skeletonItem:
            if not skeletonItem in self.window.skeletonTreeWidget.selectedItems():
                self.window.skeletonTreeWidget.clearSelection()
            skeletonItem.setSelected(True)
        else:
            self.window.skeletonTreeWidget.clearSelection()
        # update limb visibility
        if self.window.selectedBoneItem:
            self.window.highlightBone(self.window.selectedBoneItem)
        else:
            self.window.unhighlightBone()


class TrimSkinsDelegate(ChopHumanDelegate):
    """
    This mode facilitates trimming of limb skins.
    Holding the left mouse button masks out parts of the skin.
    Pressing the right button reveals area.
    """
    delegateName = 'Trim skins'
    isDragging = False
    isMasking = True
    hotKey = 'd'

    def enable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(self.window.selectedBoneItem, None)
        self.window.pushCursor(QtCore.Qt.CrossCursor)

    def disable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(None, self.window.selectedBoneItem)
        self.window.popCursor()

    def onBoneSelected(self, current, previous):
        if previous:
            previous.isEditing = False
        if current:
            current.isEditing = True
        self.updateUI()

    def updateUI(self):
        skeletonItem = self.window.selectedSkeletonItem
        # update the skeleton tree view
        if skeletonItem:
            if not skeletonItem in self.window.skeletonTreeWidget.selectedItems():
                self.window.skeletonTreeWidget.clearSelection()
            skeletonItem.setSelected(True)
        else:
            self.window.skeletonTreeWidget.clearSelection()
        # update limb visibility
        if self.window.selectedBoneItem:
            self.window.highlightBone(self.window.selectedBoneItem)
        else:
            self.window.unhighlightBone()

    def onSceneMousePressEvent(self, event):
        selectedBoneItem = self.window.selectedBoneItem
        if selectedBoneItem:
            skinItem = self.window.skinItemMap.get(selectedBoneItem.bone.name, None)
            if skinItem:
                targetPos = skinItem.mapFromScene(event.scenePos())
                self.isDragging = True
                self.isMasking = event.button() == QtCore.Qt.LeftButton
                skinItem.addToMask(targetPos, 10, 10, unmask=not self.isMasking)
                self.window.scene.update()
        else:
            event.ignore()

    def onSceneMouseMoveEvent(self, event):
        if self.isDragging:
            selectedBoneItem = self.window.selectedBoneItem
            if selectedBoneItem:
                skinItem = self.window.skinItemMap.get(selectedBoneItem.bone.name, None)
                if skinItem:
                    targetPos = skinItem.mapFromScene(event.scenePos())
                    #targetPos = event.scenePos() - selectedBoneItem.scenePos()
                    skinItem.addToMask(targetPos, 10, 10, unmask=not self.isMasking)
            self.window.scene.update()

    def onSceneMouseReleaseEvent(self, event):
        self.isDragging = False


class PoseDelegate(ChopHumanDelegate):
    """
    This delegate allows the user to pose the skeleton by
    dragging the bones around.
    """
    delegateName = 'Pose'
    hotKey = 'f'

    def enable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(self.window.selectedBoneItem, None)
        self.window.pushCursor(QtCore.Qt.OpenHandCursor)

    def disable(self):
        if self.window.selectedBoneItem:
            self.onBoneSelected(None, self.window.selectedBoneItem)
        self.window.popCursor()

    def onBoneSelected(self, current, previous):
        if previous:
            previous.isPosing = False
        if current:
            current.isPosing = True
        self.updateUI()

    def onBoneTransformChanged(self):
        boneItem = self.window.selectedBoneItem
        flatBone = self.window.flatEntityState.boneByName(boneItem.boneName)
        pos = boneItem
        if flatBone.parent != -1:
            flatParentBone = self.window.flatEntityState.bones[flatBone.parent]

    def updateUI(self):
        skeletonItem = self.window.selectedSkeletonItem
        # update the skeleton tree view
        if skeletonItem:
            if not skeletonItem in self.window.skeletonTreeWidget.selectedItems():
                self.window.skeletonTreeWidget.clearSelection()
            skeletonItem.setSelected(True)
        else:
            self.window.skeletonTreeWidget.clearSelection()
        # update bone visibility
        if self.window.selectedBoneItem:
            self.window.highlightBone(self.window.selectedBoneItem)
        else:
            self.window.unhighlightBone()
