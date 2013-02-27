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

    def onLimbSelected(self, current, previous):
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
    This is the delegate which is used by default. Allows highlighting of limbs.
    """
    delegateName = 'View'
    hotKey = 'a'

    def onLimbSelected(self, current, previous):
        self.updateUI()

    def updateUI(self):
        limbItem = self.window.selectedLimbItem
        if limbItem:
            self.window.highlightLimb(limbItem)
        else:
            self.window.unhighlightLimb()


class PlaceBonesDelegate(ChopHumanDelegate):
    """
    This mode is used to arrange the bones relative to the skins.
    """
    delegateName = 'Place bones'
    hotKey = 's'

    def enable(self):
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.editBone(True)
        self.window.pushCursor(QtCore.Qt.OpenHandCursor)

    def disable(self):
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.editBone(False)
        self.window.popCursor()

    def onLimbSelected(self, current, previous):
        if previous:
            previous.editBone(False)
        if current:
            current.editBone(True)
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
        if self.window.selectedLimbItem:
            self.window.highlightLimb(self.window.selectedLimbItem)
        else:
            self.window.unhighlightLimb()


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
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.editSkin(True)
        self.window.pushCursor(QtCore.Qt.CrossCursor)

    def disable(self):
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.editSkin(False)
        self.window.popCursor()

    def onLimbSelected(self, current, previous):
        if previous:
            previous.editSkin(False)
        if current:
            current.editSkin(True)
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
        if self.window.selectedLimbItem:
            self.window.highlightLimb(self.window.selectedLimbItem)
        else:
            self.window.unhighlightLimb()

    def onSceneMousePressEvent(self, event):
        selectedLimbItem = self.window.selectedLimbItem
        if selectedLimbItem and selectedLimbItem.skinItem:
            targetPos = event.scenePos() - selectedLimbItem.scenePos()
            self.isDragging = True
            self.isMasking = event.button() == QtCore.Qt.LeftButton
            selectedLimbItem.skinItem.addToMask(targetPos, 10, 10, unmask=not self.isMasking)
            self.window.scene.update()
        else:
            event.ignore()

    def onSceneMouseMoveEvent(self, event):
        if self.isDragging:
            selectedLimbItem = self.window.selectedLimbItem
            targetPos = event.scenePos() - selectedLimbItem.scenePos()
            selectedLimbItem.skinItem.addToMask(targetPos, 10, 10, unmask=not self.isMasking)
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
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.pose(True)
        self.window.pushCursor(QtCore.Qt.OpenHandCursor)

    def disable(self):
        if self.window.selectedLimbItem:
            self.window.selectedLimbItem.pose(False)
        # reset the skeleton to rest pose
        for _, limbItem in self.window._limbItemMap.items():
            limbItem.setRotation(0)
        self.window.popCursor()

    def onLimbSelected(self, current, previous):
        if previous:
            previous.pose(False)
        if current:
            current.pose(True)
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
        if self.window.selectedLimbItem:
            self.window.highlightLimb(self.window.selectedLimbItem)
        else:
            self.window.unhighlightLimb()
    