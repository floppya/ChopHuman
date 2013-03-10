import math
import os
from PyQt4 import QtCore, QtGui
from chophumanfinisher.exporters.scml import SCMLExporter
from chophumanfinisher.importers.scml import SCMLImporter
from chophumanfinisher.models.animation import EntityState
from chophumanfinisher.models.skeleton import normalizeAngle 
from chophumanfinisher.ui.ui_mainwindow import Ui_ChopHumanMainWindow
from .scenes import ChopHumanGraphicsScene
from .widgets import BoneGraphicsItem, MaskedSkinItem, SkinGraphicsItem
from .window_delegates import (
    DefaultDelegate, PlaceBonesDelegate, TrimSkinsDelegate, PoseDelegate
)


class ChopHumanMainWindow(QtGui.QMainWindow, Ui_ChopHumanMainWindow):
    """
    This does practically everything; what a *great* class!
    """
    PLAYBACK_TIMER_INTERVAL = 10 # ms
    changesCreateNewKeyframe = True 
    # sends the current state and its flattened version
    entityStateChanged = QtCore.pyqtSignal(EntityState, EntityState)
    
    def __init__(self, parent=None):
        super(ChopHumanMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.animationSet = None
        self.currentAnimation = None
        self.entityState = None
        self.animationItemMap = {}
        self.boneItemMap = {}
        self.boneTreeItemMap = {}
        self.skinItemMap = {}
        self.skinTreeItemMap = {}

        self.scene = ChopHumanGraphicsScene()
        self.scene.mainwindow = self
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.sceneGraphicsView.setScene(self.scene)

        self.playbackTimer = QtCore.QTimer(self)

        self._wireEvents()
        self.reset()

        self._createDelegates()
        self._createImporters()
        self._createExporters()
        
    def _wireEvents(self):
        """Connect up all the event handlers here. Looks great!"""
        self.actionLoadImages.triggered.connect(self.onLoadImages)
        self.actionReset.triggered.connect(self.onReset)
        self.skeletonTreeWidget.currentItemChanged.connect(self.onBoneSelected)
        self.animationListWidget.currentItemChanged.connect(self.onAnimationChanged)
        @self.animationListWidget.itemChanged.connect
        def onAnimationNameChanged(item):
            animation = self.animationItemMap[item]
            self.animationSet.renameAnimation(animation, unicode(item.text()))
        self.playbackSlider.valueChanged.connect(self.onAnimationTimeChanged)
        self.spinAnimationLength.valueChanged.connect(self.onAnimationLengthChanged)
        @self.butZeroPlayback.clicked.connect
        def onGoToStartOfPlayback():
            self.playbackSlider.setValue(0.0)
        @self.butEndOfPlayback.clicked.connect
        def onGoToEndOfPlayback():
            self.playbackSlider.setValue(self.playbackSlider.maximum())
        self.butTogglePlay.clicked.connect(self.onTogglePlayback)
        @self.playbackTimer.timeout.connect
        def onPlaybackTick():
            if not self.currentAnimation:
                return
            currentSliderVal = self.playbackSlider.value()
            playbackInterval = self.playbackTimer.interval()
            delta = playbackInterval / float(self.currentAnimation.length)
            maxVal = self.playbackSlider.maximum()
            newVal = currentSliderVal + delta * maxVal
            if newVal >= maxVal:
                if self.currentAnimation.looping: 
                    newVal -= maxVal
                else:
                    newVal = maxVal
                    self.butTogglePlay.click()
            self.playbackSlider.setValue(newVal)
        self.entityStateChanged.connect(self.updateModelItems)
        @self.chkHighlightSelected.stateChanged.connect
        def onToggleHighlightSelected(state):
            pass # TODO: change the current view to reflect the new state
        @self.actionFreezeSkins.triggered.connect
        def onToggleFreezeSkin(val):
            if not self.actionFreezeSkins.isChecked():
                self.copySkinTransforms()
        @self.butLooping.clicked.connect
        def onToggleLooping(val):
            if not self.currentAnimation:
                return
            self.currentAnimation.looping = bool(self.butLooping.isChecked())
        @self.butNewAnimation.clicked.connect
        def onNewAnimation():
            if not self.animationSet:
                return
            animation = self.animationSet.cloneAnimation()
            if not animation:
                return
            baseName = 'New animation'
            name = baseName
            uid = 0
            while name in self.animationSet.animationByName:
                uid += 1
                name = baseName + str(uid)
            animation.name = name
            self.animationSet.addAnimation(animation)
            self.animationListWidget.addItem(self._makeAnimationListItem(animation))                
        @self.butCloneAnimation.clicked.connect
        def onCloneAnimation():
            if not self.currentAnimation:
                return
            animation = self.currentAnimation.clone()
            animation.name = 'Clone of %s' % animation.name
            self.animationSet.addAnimation(animation)
            self.animationListWidget.addItem(self._makeAnimationListItem(animation))
        @self.butDeleteAnimation.clicked.connect
        def onDeleteAnimation():
            selectedItems = self.animationListWidget.selectedItems()
            if not selectedItems:
                return
            choice = QtGui.QMessageBox.question(
                self, 'Delete Animation?', 'Do you really want to delete this animation?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No
            )
            if choice != QtGui.QMessageBox.Yes:
                return
            for item in selectedItems:
                animation = self.animationItemMap[item]
                self.animationSet.removeAnimation(animation)
                self.animationListWidget.takeItem(self.animationListWidget.row(item))
        @self.butRetargetAnimation.clicked.connect
        def onRetargetAnimation():
            self.retargetAnimation()
        @self.butAddKeyframe.clicked.connect
        def onAddKeyframe():
            self._createKeyframeFromStateNow()
        @self.butMoveToPrevKeyframe.clicked.connect
        def onMoveToPrevKeyframe():
            keyframe = self.currentKeyframe
            if not keyframe:
                return
            if keyframe.time == self.frameTime:
                keyframe = self.currentAnimation.getPrevKeyframe(keyframe)
            if keyframe:
                self.playbackSlider.setValue(keyframe.time)
        @self.butMoveToNextKeyframe.clicked.connect
        def onMoveToNextKeyframe():
            keyframe = self.currentKeyframe
            if not keyframe:
                return
            if keyframe.time == self.frameTime:
                keyframe = self.currentAnimation.getNextKeyframe(keyframe)
            if keyframe:
                self.playbackSlider.setValue(keyframe.time)
        @self.butDeleteKeyframe.clicked.connect
        def onDeleteKeyframe():
            keyframe = self.currentKeyframe
            if keyframe:
                self.currentAnimation.removeKeyframe(keyframe)
                self.updateAnimationState()
    
    @property
    def currentKeyframe(self):
        if not self.currentAnimation:
            return None
        return self.currentAnimation.getKeyframeAt(self.frameTime)

    @property
    def frameTime(self):
        if not self.currentAnimation:
            return 0
        return int(self.t * self.currentAnimation.length)

    def onTogglePlayback(self):
        isPlaying = self.butTogglePlay.isChecked()
        if isPlaying:
            if self.currentAnimation:
                label = 'Stop' 
                self.playbackTimer.start(self.PLAYBACK_TIMER_INTERVAL)
            else:
                label = 'Play'
                self.butTogglePlay.setChecked(False)    
        else:
            label = 'Play'
            self.playbackTimer.stop()
        #self.butTogglePlay.setText(label)
    
    def _createDelegates(self):
        self._delegate = None
        DELEGATE_CLASSES = (
            DefaultDelegate, PlaceBonesDelegate, TrimSkinsDelegate
        )
        self.delegates = []
        self.delegateActionGroup = QtGui.QActionGroup(self)
        self.delegateActionGroup.setExclusive(True)
        for delegate_class in DELEGATE_CLASSES:
            delegate = delegate_class(self)
            self.delegates.append(delegate)
            action = delegate.getEnableAction()
            self.delegateActionGroup.addAction(action)
        self.toolToolbar.addActions(self.delegateActionGroup.actions())
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

    def _createImporters(self):
        IMPORTER_CLASSES = (SCMLImporter,)
        self.importerActionGroup = QtGui.QActionGroup(self)
        for importerClass in IMPORTER_CLASSES:
            action = QtGui.QAction(importerClass.verboseName(), None)
            def onImport():
                self.onImport(importerClass)
            action.triggered.connect(onImport)
            self.importerActionGroup.addAction(action)
        self.menuFile.addSeparator()
        self.menuFile.addActions(self.importerActionGroup.actions())
        
    def onExport(self, exporterClass):
        filename, _ = QtGui.QFileDialog.getSaveFileNameAndFilter(
            self, exporterClass.verboseName(), '', exporterClass.fileFilter()
        )
        if not filename:
            return
        filename = unicode(filename)
        exporter = exporterClass()
        exporter.export(self.animationSet, self.skinItemMap, filename)
    
    def onImport(self, importerClass):
        filename, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(
            self, importerClass.verboseName(), '', importerClass.fileFilter()
        )
        if not filename:
            return        
        filename = unicode(filename)
        importer = importerClass()
        animationSets, skinFileMap = importer.importFile(filename)
        # TODO: only clear the animation set if the imported animations are of different shapes.
        # TODO: otherwise, add them to the current animationSet
        
        self.reset()
        
        self.animationListWidget.clear()
        self.animationSet = animationSets[0] # HACK
        for animation in self.animationSet.animations:
            animationListItem = self._makeAnimationListItem(animation)
            self.animationListWidget.addItem(animationListItem)
        # create the requisite bone items 
        entityState = self.animationSet.entityState
        currentRoot = None
        boneTreeItemMap = self.boneTreeItemMap
        for bone in entityState.bones:
            boneItem = BoneGraphicsItem()
            boneItem.bone = bone.clone()
            boneItem.boneChanged.connect(self.onBoneChanged)
            self.scene.addItem(boneItem)
            self.boneItemMap[bone.name] = boneItem
            thisBoneTreeItem = QtGui.QTreeWidgetItem([bone.name])
            boneTreeItemMap[bone.name] = thisBoneTreeItem
            if bone.parent != -1:
                parentBone = entityState.bones[bone.parent]
                parentItem = boneTreeItemMap[parentBone.name]
                parentItem.addChild(thisBoneTreeItem)
            else:
                if currentRoot:
                    self.skeletonTreeWidget.addTopLevelItem(currentRoot)
                    currentRoot = None
            if not currentRoot:
                currentRoot = thisBoneTreeItem
        if currentRoot:
            self.skeletonTreeWidget.addTopLevelItem(currentRoot)

        self.skeletonTreeWidget.expandAll()
        self.animationListWidget.setCurrentRow(0) # set up us the bones
        # load up the images
        filenames = [d['filename'] for d in skinFileMap.values()]
        self.loadImages(filenames)
        self.updateAnimationState()
    
    def _makeAnimationListItem(self, animation):
        listItem = QtGui.QListWidgetItem(animation.name)
        listItem.setFlags(listItem.flags() | QtCore.Qt.ItemIsEditable)
        self.animationItemMap[listItem] = animation
        return listItem

    def reset(self):
        self.scene.clear()

        self._cursorState = []
        # TODO: clean up bones
        for key, value in self.boneItemMap.items():
            pass
        self.boneItemMap = {}
        self.boneTreeItemMap = {}
        # TODO: clean up skins
        for key, value in self.skinItemMap.items():
            pass
        self.skinItemMap = {}
        self.skinTreeItemMap = {}
        
        self.selectedBoneItem = None

        self.skeletonTreeWidget.clear()
        
        self.animationSets = None
        self.animationListWidget.clear()
        self.t = 0.0
        self.currentAnimation = None
        self.entityState = None
        self.playbackTimer.stop()

    def onReset(self):
        self.reset()

    def onBoneSelected(self, current, previous):
        previousBoneItem = self.selectedBoneItem
        self.selectedSkeletonItem = current
        if current:
            currentName = unicode(current.data(0, QtCore.Qt.DisplayRole).toString())
            self.selectedBoneItem = self.boneItemMap.get(currentName, None)
        else:
            if self.selectedBoneItem:
                self.selectedBoneItem = None
        self.delegate.onBoneSelected(self.selectedBoneItem, previousBoneItem)    

    def onLoadImages(self):
        if not self.currentAnimation:
            QtGui.QMessageBox.information(self, 'Sorry, this menu item should be lower.', 'You will need to load some animations first.')
            return
        filenames, _ = QtGui.QFileDialog.getOpenFileNamesAndFilter(
            self, 'Choose images', 'c:/tmp/', 'Image files (*.png *.jpg *.jpeg *.gif *.tga)'
        )
        if not filenames:
            return
        self.pushCursor(QtCore.Qt.WaitCursor)
        self.loadImages(filenames, positionFromImage=True)
        self.copySkinTransforms()
        self.popCursor()

    def loadImages(self, filenames, positionFromImage=False):
        for filename in filenames:
            filename = unicode(filename)
            pixmap = QtGui.QPixmap()
            pixmap.load(filename)
            fullWidth = pixmap.width()
            fullHeight = pixmap.height()
            pixmapItem = MaskedSkinItem(pixmap)
            # cut out all the wasted space and position what remains
            opaqueArea = pixmapItem.opaqueArea()
            clippedPixmap = pixmap.copy(opaqueArea.boundingRect().toRect())
            clippedPixmapItem = MaskedSkinItem(clippedPixmap)
            pos = opaqueArea.boundingRect().topLeft()
            pixmapItem = clippedPixmapItem
            skinFileName = os.path.split(filename)[-1]
            skinBaseName = skinFileName.replace('_normal_material', '')
            bone = self._findBoneByName(skinBaseName)
            skin = self._findSkinByBoneName(skinBaseName)
            if not skin:
                print('no skin for ' + skinBaseName)
            if not bone:
                print('no bone for ' + skinBaseName)
            skinItem = self.skinItemMap.get(bone.name, None)
            if not skinItem:
                skinItem = SkinGraphicsItem()
                skinItem.setZValue(skin.zIndex)
                self.skinItemMap[bone.name] = skinItem
                self.scene.addItem(skinItem)
                positionFromImage = True
            if positionFromImage:
                offset = QtCore.QPointF(0.5 * fullWidth, fullHeight)
                pos -= offset
                skinItem.setPos(pos)
            if 'normal' in skinFileName:
                skinItem.normalItem = pixmapItem
            else:
                skinItem.diffuseItem = pixmapItem
        # move bones to the front
        for item in self.boneItemMap.values():
            item.setZValue(1000.0)
            
    def highlightBone(self, boneItem, hiddenOpacity=0.05):
        for _, item in self.boneItemMap.items():
            if item == boneItem or not self.chkHighlightSelected.isChecked():
                item.show()
            else:
                item.hide(opacity=hiddenOpacity)

    def unhighlightBone(self):
        for _, item in self.boneItemMap.items():
            item.show()

    def pushCursor(self, cursor):
        self._cursorState.append(self.cursor())
        self.setCursor(cursor)

    def popCursor(self):
        if self._cursorState:
            cursor = self._cursorState.pop()
            self.setCursor(cursor)

    def _findSkinByBoneName(self, name):
        if not self.entityState:
            return
        for skin in self.entityState.skins:
            bone = self.entityState.bones[skin.parent]
            if bone.name in name:
                return skin
        return None

    def _findBoneByName(self, name):
        if not self.entityState:
            return
        for bone in self.entityState.bones:
            if bone.name in name:
                return bone
        return None

    def onAnimationChanged(self, current, previous):
        if not current:
            return
        animation = self.currentAnimation = self.animationItemMap[current]#self.animationSet.animationByName[unicode(current.text())]
        self.entityState = animation.cloneEntityState()
        self.flatEntityState = self.entityState.clone()
        self.spinAnimationLength.setValue(animation.length)
        self.playbackSlider.setMaximum(animation.length - 1)
        self.butLooping.setChecked(animation.looping)
        prevT = float(self.playbackSlider.value())
        if prevT != 0.0:
            self.playbackSlider.setValue(0.0);
        else:
            self.updateAnimationState()

    def onAnimationLengthChanged(self, value):
        if not self.currentAnimation:
            return
        self.currentAnimation.length = int(value)
        self.playbackSlider.setMaximum(int(value) - 1)
        self.onAnimationTimeChanged(self.playbackSlider.value())

    def onAnimationTimeChanged(self, newT):
        if not self.currentAnimation:
            return
        self.t = newT / float(self.currentAnimation.length)
        self.updateAnimationState()

    def updateAnimationState(self):
        if not self.currentAnimation:
            self.spinAnimationLength.setValue(0)
            return
        animation = self.currentAnimation
        frameT = int(self.t * animation.length)
        self.labelCurrentFrame.setText(str(frameT + 1))
        animation.updateEntityState(self.entityState, frameT)
        self.entityState.flatten(self.flatEntityState)
        self.entityStateChanged.emit(self.entityState, self.flatEntityState)
    
    def updateModelItems(self, entityState, flatEntityState):
        entityState = flatEntityState
        for bone in entityState.bones:
            boneItem = self.boneItemMap.get(bone.name, None)
            if not boneItem:
                continue
            boneItem.setRotation(bone.transform.angle)
            boneItem.setPos(bone.transform.x, bone.transform.y)
        if not self.actionFreezeSkins.isChecked():
            for skin in entityState.skins:
                bone = entityState.bones[skin.parent]
                skinItem = self.skinItemMap.get(bone.name, None)
                if not skinItem:
                    continue
                skinItem.setRotation(skin.transform.angle)
                skinItem.setPos(skin.transform.x, skin.transform.y)

    def onBoneChanged(self):
        if not self.currentAnimation:
            return
        boneItem = self.selectedBoneItem
        bone = boneItem.bone
        pos = boneItem.pos()
        rotation = boneItem.rotation()
        if bone.parent != -1:
            parentBone = self.entityState.bones[bone.parent]
            parentBoneItem = self.boneItemMap[parentBone.name]
            pos = parentBoneItem.mapFromScene(pos)
            rotation -= normalizeAngle(parentBoneItem.rotation())
        bone.transform.x = pos.x()
        bone.transform.y = pos.y()
        bone.transform.angle = rotation
        frameTime = int(self.t * self.currentAnimation.length)
        keyframe = self.currentAnimation.getKeyframeAt(frameTime)
        if self.changesCreateNewKeyframe and keyframe.time != frameTime:
            newKeyframe = self._createKeyframeFromStateNow()
        else:
            keyframe.entityState.boneByName[bone.name].copy(bone)
        self.updateAnimationState()
    
    def _createKeyframeFromStateNow(self):
        if not self.currentAnimation:
            return
        frameTime = int(self.t * self.currentAnimation.length)
        keyframe = self.currentAnimation.getKeyframeAt(frameTime)
        # does a keyframe already exist for this frame?
        if keyframe.time == frameTime:
            return keyframe
        newKeyframe = keyframe.clone()
        newKeyframe.entityState.copy(self.entityState)
        newKeyframe.time = int(frameTime)
        self.currentAnimation.addKeyframe(newKeyframe)
        return newKeyframe

    def copySkinTransforms(self):
        """
        Update the relative locations
        """
        keyframe = self.currentKeyframe
        if not keyframe:
            return
        for skin in keyframe.entityState.skins:
            bone = keyframe.entityState.bones[skin.parent]
            boneItem = self.boneItemMap[bone.name]
            skinItem = self.skinItemMap.get(bone.name, None)
            if not skinItem:
                continue
            bonePos = boneItem.scenePos()
            boneRotation = boneItem.rotation()
            if bone.parent != -1:
                parentBone = keyframe.entityState.bones[bone.parent]
                parentBoneItem = self.boneItemMap[parentBone.name]
                bonePos = parentBoneItem.mapFromScene(bonePos)
                boneRotation -= parentBoneItem.rotation()            
            bone.transform.x = bonePos.x()
            bone.transform.y = bonePos.y()
            bone.transform.angle = boneRotation
            pos = boneItem.mapFromScene(skinItem.scenePos())
            skin.transform.x = pos.x()
            skin.transform.y = pos.y()
            skin.transform.angle = skinItem.rotation() - boneItem.rotation()
        self.updateAnimationState()

    def retargetAnimation(self):
        """
        Setup
        -----
        Make sure there is an animation named 'rest' with 2 keyframes:
        the original rest pose, followed by the new rest pose.
        """
        # TODO: if any of this fails, show a dialog that has some instructions
        if not self.animationSet:
            return
        restAnimation = self.animationSet.animationByName.get('rest', None)
        if not restAnimation:
            return
        # compare the original pose with the target (new) pose
        originalKeyframe = restAnimation.keyframes[0]
        targetKeyframe = restAnimation.keyframes[1]
        originalEntityState = originalKeyframe.entityState
        targetEntityState = targetKeyframe.entityState
        diffEntityState = targetEntityState.clone()
        diffEntityState.difference(originalEntityState, targetEntityState, True)
        for animation in self.animationSet.animations:
            if animation.name == 'rest':
                animation.keyframes[0].entityState.combineSelf(diffEntityState, True)
                continue
            for keyframe in animation.keyframes:
                keyframe.entityState.combineSelf(diffEntityState, True)

        self.updateAnimationState()
        QtGui.QMessageBox.information(self, 'Retargeting complete', 'Retargeting is complete.')

    