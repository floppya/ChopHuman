import math
import os
from collections import defaultdict
import elementtree.ElementTree as ET
from chophumanfinisher.models.skeleton import HUMAN_LIMB_ORDER, normalizeAngle
from .base import ChopHumanExporter


class SCMLExporter(ChopHumanExporter):
    """
    Exports to SCML. 
    """
    fileType = ('Spriter', 'scml')
    version = '0.00001'
    
    def export(self, animationSet, skinItemMap, outputFilepath):
        self.animationSet = animationSet
        self.skinItemMap = skinItemMap
    
        root = ET.Element('spriter_data')
        root.set('scml_version', '1.0')
        root.set('generator', 'ChopHuman SCML Exporter')
        root.set('generator_version', self.version)
        
        outputPath, fileName = os.path.split(outputFilepath)
        self.outputPath = outputPath

        projectName, _ = fileName.split('.')
        self.outputPath = outputPath
        self.projectName = projectName
        self.folder = folder = ET.SubElement(root, 'folder')
        folder.set('id', '0')
        folder.set('name', projectName)
        try:
            os.mkdir(os.path.join(outputPath, projectName))
        except OSError:
            pass # already exists

        entity = ET.SubElement(root, 'entity')
        entity.set('id', '0')
        entity.set('name', projectName)
        
        boneSkinMap = self.prepareSkins()

        for animation in animationSet.animations:
            animationNode = ET.SubElement(entity, 'animation')
            animationNode.set('id', str(animation.id))
            animationNode.set('name', str(animation.name))
            animationNode.set('length', str(animation.length))
            if animation.looping:
                animationNode.set('looping', 'true')
            else:
                animationNode.set('looping', 'false')

            boneTimelines = {}
            objectTimelines = {}
            mainlineNode = ET.SubElement(animationNode, 'mainline')    
            for keyframe in animation.keyframes:
                keyNode = ET.SubElement(mainlineNode, 'key')
                keyNode.set('id', str(keyframe.id))
                keyNode.set('time', str(keyframe.time))
                for bone in keyframe.entityState.bones:
                    boneRefNode = ET.SubElement(keyNode, 'bone_ref')
                    boneRefNode.set('id', str(bone.id))
                    if bone.parent != -1:
                        boneRefNode.set('parent', str(bone.parent))
                    boneRefNode.set('timeline', str(bone.id))
                    boneRefNode.set('key', str(keyframe.id))
                    timelineNode = boneTimelines.get(bone.id, None)
                    if not timelineNode:
                        timelineNode = ET.SubElement(animationNode, 'timeline')
                        timelineNode.set('id', str(bone.id))
                        timelineNode.set('name', str(bone.name))
                        boneTimelines[bone.id] = timelineNode
                    bt = bone.transform
                    boneKeyNode = ET.SubElement(timelineNode, 'key')
                    boneKeyNode.set('id', str(keyframe.id))
                    boneKeyNode.set('spin', str(bt.spin))
                    boneKeyNode.set('time', str(keyframe.time))
                    boneNode = ET.SubElement(boneKeyNode, 'bone')
                    boneNode.set('x', str(bt.x))
                    boneNode.set('y', str(-bt.y))
                    boneNode.set('angle', str(-normalizeAngle(bt.angle)))
                    boneNode.set('scale_x', str(bt.scaleX))
                    boneNode.set('scale_y', str(bt.scaleY))
                    
                baseObjectId = bone.id + 1
                objectId = 0
                for skin in keyframe.entityState.skins:
                    bone = keyframe.entityState.bones[skin.parent]
                    boneSkins = boneSkinMap[bone.name]
                    for fileId, name, filename, boneName, item, offset in boneSkins:
                        timelineId = objectId + baseObjectId
                        objRefNode = ET.SubElement(keyNode, 'object_ref')
                        objRefNode.set('id', str(objectId))
                        objRefNode.set('parent', str(skin.parent))
                        objRefNode.set('timeline', str(timelineId))
                        objRefNode.set('key', str(keyframe.id))
                        objRefNode.set('z_index', str(objectId))
                        timelineNode = objectTimelines.get(objectId, None)
                        if not timelineNode:
                            timelineNode = ET.SubElement(animationNode, 'timeline')
                            timelineNode.set('id', str(timelineId))
                            timelineNode.set('name', str(name))
                            objectTimelines[objectId] = timelineNode
                        ot = skin.transform
                        objKeyNode = ET.SubElement(timelineNode, 'key')
                        objKeyNode.set('id', str(keyframe.id))
                        objKeyNode.set('spin', str(ot.spin))
                        objKeyNode.set('time', str(keyframe.time))
                        objNode = ET.SubElement(objKeyNode, 'object')
                        objNode.set('folder', '0')
                        objNode.set('file', str(fileId))
                        ca = math.cos(ot.angleRadians)
                        sa = math.sin(ot.angleRadians)
                        tmpX = offset.x()
                        tmpY = offset.y()
                        offsetX = tmpX * ca - tmpY * sa
                        offsetY = tmpX * sa + tmpY * ca 
                        objNode.set('x', str(ot.x + offsetX))
                        objNode.set('y', str(-(ot.y + offsetY)))
                        objNode.set('angle', str(normalizeAngle(-ot.angle)))
                        objectId += 1
            tree = ET.ElementTree(root)
            tree.write(outputFilepath, encoding='utf-8')

    def prepareSkins(self):
        boneSkinMap = defaultdict(list)
        nextFileId = 0
        for boneName, skinItem in self.skinItemMap.items():
            items = []
            normalItem = skinItem.normalItem
            if normalItem:
                itemName = '%s_n' % boneName
                filename = self._relativeFilename(itemName + '.png')
                pixmap, offset = normalItem.getClippedPixmap()
                pixmap.save(os.path.join(self.outputPath, filename))
                data = (nextFileId, itemName, filename, boneName, normalItem, offset)
                boneSkinMap[boneName].append(data)
                items.append(data)
                nextFileId += 1
            diffuseItem = skinItem.diffuseItem
            if diffuseItem:
                itemName = '%s_d' % boneName
                filename = self._relativeFilename(itemName + '.png')
                pixmap, offset = diffuseItem.getClippedPixmap()
                pixmap.save(os.path.join(self.outputPath, filename))
                data = (nextFileId, itemName, filename, boneName, diffuseItem, offset)
                boneSkinMap[boneName].append(data)
                items.append(data)
                nextFileId += 1
            # add the file nodes to the folder
            for data in items:
                fileId, name, filename, boneName, item, offset = data
                elFile = ET.SubElement(self.folder, 'file')
                elFile.set('id', str(fileId))
                elFile.set('name', filename)
                itemBounds = item.boundingRect()
                elFile.set('width', str(int(itemBounds.width())))
                elFile.set('height', str(int(itemBounds.height())))
        return boneSkinMap
    
    def _relativeFilename(self, filename):
        return os.path.join(self.projectName, filename)


