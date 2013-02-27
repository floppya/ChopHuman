import os
from PyQt4 import QtCore, QtGui
from chophumanfinisher.exporters.scml import SCMLExporter
from chophumanfinisher.models.skeleton import Limb, HUMAN_LIMB_ORDER
from chophumanfinisher.ui.ui_mainwindow import Ui_ChopHumanMainWindow
from .scenes import ChopHumanGraphicsScene
from .widgets import LimbGraphicsItem, MaskedSkinItem
from .window_delegates import (
    DefaultDelegate, PlaceBonesDelegate, TrimSkinsDelegate, PoseDelegate
)


class ChopHumanMainWindow(QtGui.QMainWindow, Ui_ChopHumanMainWindow):
    """
    This does everything; what a *great* class!
    """
    def __init__(self, parent=None):
        super(ChopHumanMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.rootLimb = None
        self.scene = ChopHumanGraphicsScene()
        self.scene.mainwindow = self
        self.sceneGraphicsView.setScene(self.scene)
        self.reset()
        # delegate related
        self.actionLoadImages.triggered.connect(self.onLoadImages)
        self.actionReset.triggered.connect(self.onReset)
        self.skeletonTreeWidget.currentItemChanged.connect(self.onLimbSelected)
        self._createDelegates()
        self._createExporters()
        self._wheelPosition = 0
        
    def _createDelegates(self):
        self._delegate = None
        DELEGATE_CLASSES = (
            DefaultDelegate, PlaceBonesDelegate, TrimSkinsDelegate, PoseDelegate
        )
        self.delegates = []
        self.delegateActionGroup = QtGui.QActionGroup(self)
        self.delegateActionGroup.setExclusive(True)
        for delegate_class in DELEGATE_CLASSES:
            delegate = delegate_class(self)
            self.delegates.append(delegate)
            action = delegate.getEnableAction()
            self.delegateActionGroup.addAction(action)
        self.toolBar.addActions(self.delegateActionGroup.actions())
        self.delegate = self.delegates[0]
        self.delegateActionGroup.actions()[0].setChecked(True)

    @property
    def delegate(self):
        return self._delegate
    
    @delegate.setter
    def delegate(self, value):
        if self._delegate:
            self._delegate.disable()
        self._delegate = value
        self._delegate.enable()
        
    def _createExporters(self):
        EXPORTER_CLASSES = (SCMLExporter,)
        self.exporterActionGroup = QtGui.QActionGroup(self)
        for exporterClass in EXPORTER_CLASSES:
            action = QtGui.QAction(exporterClass.verboseName(), None)
            def onExport():
                self.onExport(exporterClass)
            action.triggered.connect(onExport)
            self.exporterActionGroup.addAction(action)
        self.menuFile.addSeparator()
        self.menuFile.addActions(self.exporterActionGroup.actions())
        
    def onExport(self, exporterClass):
        filename, _ = QtGui.QFileDialog.getSaveFileNameAndFilter(
            self, exporterClass.verboseName(), '', exporterClass.fileFilter()
        )
        if not filename:
            return
        filename = unicode(filename)
        exporter = exporterClass()
        exporter.export(self, filename)

    def reset(self):
        self.scene.clear()
        self.rootLimb = Limb.stubHumanSkeleton()

        self._cursorState = []
        self._limbItemMap = {}
        self._limbMap = {}

        self.rootLimbItem = self._createLimbTreeItem(self.rootLimb)
        self._createLimbMap(self.rootLimb)
        
        self.selectedSkeletonItem = None
        self.selectedLimbItem = None

        self.skeletonTreeWidget.clear()
        self.skeletonTreeWidget.addTopLevelItem(self.rootLimbItem)
        self.skeletonTreeWidget.expandAll()

    def onReset(self):
        self.reset()

    def onLimbSelected(self, current, previous):
        previousLimbItem = self.selectedLimbItem
        self.selectedSkeletonItem = current
        if current:
            currentName = unicode(current.data(0, QtCore.Qt.DisplayRole).toString())
            self.selectedLimbItem = self._limbItemMap.get(currentName, None)
        else:
            if self.selectedLimbItem:
                self.selectedLimbItem = None
        self.delegate.onLimbSelected(self.selectedLimbItem, previousLimbItem)    

    def onSceneMouseRelease(self, event):
        self.delegate.onSceneMouseRelease(event)

    def onLoadImages(self):
        filenames, _ = QtGui.QFileDialog.getOpenFileNamesAndFilter(
            self, 'Choose images', 'c:/tmp/', 'Image files (*.png *.jpg *.jpeg *.gif *.tga)'
        )
        if not filenames:
            return
        self.pushCursor(QtCore.Qt.WaitCursor)
        for filename in filenames:
            filename = unicode(filename)
            pixmap = QtGui.QPixmap()
            pixmap.load(filename)
            pixmapItem = MaskedSkinItem(pixmap)
            # cut out all the wasted space and position what's left
            opaqueArea = pixmapItem.opaqueArea()
            clippedPixmap = pixmap.copy(opaqueArea.boundingRect().toRect())
            clippedPixmapItem = MaskedSkinItem(clippedPixmap)
            pos = opaqueArea.boundingRect().topLeft()
            pixmapItem = clippedPixmapItem
            skinFileName = os.path.split(filename)[-1]
            skinBaseName = filename.replace('_normal_material', '')
            limbItem = self._findLimbItemBySkinName(skinBaseName)
            limbItem.setPos(pos)
            if 'normal' in skinFileName:
                limbItem.normalItem = pixmapItem
            else:
                limbItem.diffuseItem = pixmapItem
        # Now, impose the skeletal hierarchy and correct z-order
        self._fixHierarchy(self.rootLimb)
        self._fixZOrder()
        
        self.popCursor()

    def wheelEvent(self, event):
        """ Scrolls through the limbs. Also, doesn't quite work correctly. """
        numDegrees = event.delta() / 8.0
        numSteps = numDegrees / 15.0
        self._wheelPosition += numSteps
        if numSteps > 0:
            fnMove = self.skeletonTreeWidget.itemAbove
        else:
            fnMove = self.skeletonTreeWidget.itemBelow
        for _ in range(0, int(abs(numSteps) + 0.5)):
            if self.skeletonTreeWidget.selectedItems():
                selectedItem = self.skeletonTreeWidget.selectedItems()[0]
                nextItem = fnMove(selectedItem)
                if nextItem:
                    self.skeletonTreeWidget.setCurrentItem(nextItem)
            else:
                self.skeletonTreeWidget.setCurrentItem(self.skeletonTreeWidget.invisibleRootItem())
        event.accept()
            
    def _fixZOrder(self):
        for z, limbName in enumerate(HUMAN_LIMB_ORDER):
            try:
                limbItem = self._limbItemMap[limbName]
            except KeyError:
                pass
            else:
                limbItem.setZValue(z)

    def _fixHierarchy(self, rootLimb):
        """
        Appropriately assign and align graphics item parentage.
        """
        if rootLimb.parent:
            item = self._limbItemMap.get(rootLimb.name, None)
            parentItem = self._limbItemMap.get(rootLimb.parent.name, None)
            if item and parentItem:
                dp = parentItem.scenePos()
                item.translate(-dp.x(), -dp.y())
                item.setParentItem(parentItem)
        for child in rootLimb.children:
            self._fixHierarchy(child)

    def highlightLimb(self, limbItem, hiddenOpacity=0.05):
        for _, item in self._limbItemMap.items():
            if item == limbItem:
                item.show()
            else:
                item.hide(opacity=hiddenOpacity)

    def unhighlightLimb(self):
        for _, item in self._limbItemMap.items():
            item.show()

    def pushCursor(self, cursor):
        self._cursorState.append(self.cursor())
        self.setCursor(cursor)

    def popCursor(self):
        if self._cursorState:
            cursor = self._cursorState.pop()
            self.setCursor(cursor)

    def _findLimbItemBySkinName(self, skinName):
        for limbName, limb in self._limbItemMap.items():
            if limbName in skinName:
                return limb
        return None

    def _createLimbMap(self, limb):
        self._limbMap[limb.name] = limb
        if limb.name != 'root':
            self._limbItemMap[limb.name] = limbItem = LimbGraphicsItem()
            self.scene.addItem(limbItem)
#            if limb.parent and limb.parent.name != 'root':
#                parentItem = self._limbItemMap[limb.parent.name]
#                limbItem.setParentItem(parentItem)
        for child in limb.children:
            self._createLimbMap(child)

    def _createLimbTreeItem(self, limb):
        limbItem = QtGui.QTreeWidgetItem([limb.name])
        for childLimb in limb.children:
            childItem = self._createLimbTreeItem(childLimb)
            limbItem.addChild(childItem)
        return limbItem
