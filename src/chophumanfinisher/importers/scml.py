from collections import defaultdict
import math
import os
import elementtree.ElementTree as ET
from chophumanfinisher.models.animation import AnimationSet, Animation, Keyframe, EntityState
from chophumanfinisher.models.skeleton import Bone, Skin
from .base import ChopHumanImporter


class SCMLImporter(ChopHumanImporter):
    """
    Imports SCML (sortof)
    """
    fileType = ('Spriter', 'scml')
    version = '0.00001'
    
    def importFile(self, inputFilepath):
        inputDirectory, inputFilename = os.path.split(inputFilepath)
        tree = ET.parse(inputFilepath)
        root = tree.getroot()
        animationSets = []
        self.fileDataTable = defaultdict(dict)
        self.skinFileMap = {}
        for folderNode in root.findall('folder'):
            folderId = int(folderNode.get('id'))
            folderName = folderNode.get('name')
            basePath = inputDirectory
            for fileNode in folderNode.findall('file'):
                fileId = int(fileNode.get('id'))
                name = fileNode.get('name')
                data = dict(
                    id=fileId,
                    folderId=folderId,
                    name=name,
                    filename=os.path.join(basePath, name),
                    width=int(fileNode.get('width')),
                    height=int(fileNode.get('height'))
                )
                self.fileDataTable[folderId][fileId] = data

        for entityNode in root.findall('entity'):
            animationSet = self._importEntity(entityNode)
            animationSets.append(animationSet)

        return animationSets, self.skinFileMap
    
    def _importEntity(self, node):
        animationSet = AnimationSet()
        animationSet.name = node.get('name')
        for animationNode in node.findall('animation'):
            animation = self._importAnimation(animationNode)
            animationSet.addAnimation(animation)
        return animationSet

    def _importAnimation(self, node):
        animation = Animation()
        animation.id = int(node.get('id'))
        animation.name = node.get('name')
        animation.length = int(node.get('length'))
        animation.looping = node.get('looping', 'true') == 'true'

        timelineSkinMap = {}
        lastKey = None
        # mainline
        for keyNode in node.findall('mainline/key'):
            timelineBoneMap = {}
            time = int(keyNode.get('time', 0))
            entityState = EntityState()
            keyframe = Keyframe(int(keyNode.get('id')), time, entityState)
            if lastKey:
                lastKey.length = time - lastKey.time
            for refNode in keyNode.findall('bone_ref'):
                bone = Bone()
                boneId = int(refNode.get('id'))
                timelineId = int(refNode.get('timeline'))
                timelineBoneMap[boneId] = timelineId
                bone.parent = int(refNode.get('parent', -1))
                if bone.parent != -1:
                    bone.parent = timelineBoneMap[bone.parent]
                keyframe.entityState.addBone(bone, timelineId)
            for refNode in keyNode.findall('object_ref'):
                skin = Skin()
                skinId = int(refNode.get('id'))
                skin.parent = int(refNode.get('parent', -1))
                if skin.parent != -1:
                    skin.parent = timelineBoneMap[skin.parent]
                skin.zIndex = int(refNode.get('z_index'))
                keyframe.entityState.addSkin(skin)
                timelineId = int(refNode.get('timeline'))
                timelineSkinMap[timelineId] = skinId
            animation.addKeyframe(keyframe)
            lastKey = keyframe
        lastKey.length = animation.length - lastKey.time
        # timelines
        for timelineNode in node.findall('timeline'):
            timelineId = int(timelineNode.get('id'))
            timelineName = timelineNode.get('name', '')
            lastKey = None
            for keyNode in timelineNode.findall('key'):
                keyId = int(keyNode.get('id'))
                spin = -int(keyNode.get('spin', 1))
                keyframe = animation.getKeyframe(keyId)
                # is this a skin?
                if timelineId in timelineSkinMap:
                    skin = keyframe.entityState.skins[timelineSkinMap[timelineId]]
                    skinNode = keyNode.find('object')
                    transform = skin.transform
                    skin.name = timelineName
                    folderId = int(skinNode.get('folder'))
                    fileId = int(skinNode.get('file'))
                    fileData = self.fileDataTable[folderId][fileId]
                    self.skinFileMap[skin.id] = fileData
                    skin.pivotX = float(skinNode.get('pivot_x', 0.0))
                    skin.pivotY = 1.0 - float(skinNode.get('pivot_y', 1.0))
                    skin.opacity = float(skinNode.get('opacity', 1.0))
                    transform.x = float(skinNode.get('x'))
                    transform.y = -float(skinNode.get('y'))
                    transform.angle = -float(skinNode.get('angle', 0.0))
                    transform.scaleX = float(skinNode.get('scale_x', 1.0))
                    transform.scaleY = float(skinNode.get('scale_y', 1.0))
                    transform.spin = spin
                else:
                    # this node is a bone
                    bone = keyframe.entityState.bones[timelineId]
                    boneNode = keyNode.find('bone')
                    transform = bone.transform
                    bone.name = timelineName
                    transform.x = float(boneNode.get('x'))
                    transform.y = -float(boneNode.get('y'))
                    transform.angle = -float(boneNode.get('angle', 0.0))
                    transform.scaleX = float(boneNode.get('scale_x', 1.0))
                    transform.scaleY = float(boneNode.get('scale_y', 1.0))
                    transform.spin = spin
                keyframe.entityState = keyframe.entityState.clone() # fixup names
                lastKey = keyframe
        return animation
    

        