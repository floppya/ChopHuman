import os
import elementtree.ElementTree as ET
from chophumanfinisher.models.skeleton import HUMAN_LIMB_ORDER
from .base import ChopHumanExporter


class SCMLExporter(ChopHumanExporter):
    """
    Exports to SCML.
    """
    fileType = ('Spriter', 'scml')
    version = '0.00001'
    
    def export(self, window, outputFilepath):
        self.window = window
        root = ET.Element('spriter_data')
        root.set('scml_version', '1.0')
        root.set('generator', 'ChopHuman SCML Exporter')
        root.set('generator_version', self.version)
        
        outputPath, fileName = os.path.split(outputFilepath)
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
        self.animation = animation = ET.SubElement(entity, 'animation')
        animation.set('id', '0')
        animation.set('name', 'rest')
        animation.set('length', '1')
        animation.set('looping', 'false')
        mainline = ET.SubElement(animation, 'mainline')
        self.mainlineKey = ET.SubElement(mainline, 'key')
        self.mainlineKey.set('id', '0')
        
        self.timelineId = 0
        self._exportBoneTimelines()
        self._exportSkinTimelines()

        tree = ET.ElementTree(root)
        tree.write(outputFilepath)

    def _exportBoneTimelines(self):
        self._exportBoneTimeline(self.window.rootLimb)
        
    def _exportBoneTimeline(self, limb, parent=None):
        item = self.window._limbItemMap.get(limb.name, None)
        #if item:
        #    item = item.boneItem
        lid = limb.id = str(self.timelineId)
        self.timelineId += 1
        ref = ET.SubElement(self.mainlineKey, 'bone_ref')
        ref.set('id', lid)
        ref.set('timeline', lid)
        ref.set('key', '0')            
        timeline = self._makeTimelineKey(lid, limb.name)
        bone = ET.SubElement(timeline, 'bone')
        if item:
            boneItem = item.boneItem
            rotation = boneItem.rotation()
            if parent and parent.boneItem:
                pos = item.mapToItem(parent.boneItem, boneItem.pos())
                rotation -= parent.boneItem.rotation()
            else:
                pos = boneItem.pos()
            bone.set('x', str(pos.x()))
            bone.set('y', str(-pos.y()))
            bone.set('angle', str(-rotation))
        else:
            bone.set('x', '0')
            bone.set('y', '0')
            bone.set('angle', '0')
        bone.set('scale_x', '1')
        bone.set('scale_y', '1')
        if limb.parent:
            ref.set('parent', limb.parent.id)
        for child in limb.children:
            self._exportBoneTimeline(child, parent=item)

    def _exportSkinTimelines(self):
        objectId = 0
        for limbName in HUMAN_LIMB_ORDER:
            limb = self.window._limbMap[limbName]
            limbName = limb.name
            limbItem = self.window._limbItemMap[limbName]
            # Crop and save the skin items for this limb
            items = []
            diffuseItem = limbItem.diffuseItem
            if diffuseItem:
                itemname = '%s_d' % limbName
                filename = self._relativeFilename(itemname + '.png')
                pixmap, offset = diffuseItem.getClippedPixmap()
                pixmap.save(os.path.join(self.outputPath, filename))
                items.append((itemname, filename, objectId, diffuseItem, offset))
                objectId += 1
            normalItem = limbItem.normalItem
            if normalItem:
                itemname = '%s_n' % limbName
                filename = self._relativeFilename(itemname + '.png')
                pixmap, offset = normalItem.getClippedPixmap()
                pixmap.save(os.path.join(self.outputPath, filename))
                items.append((itemname, filename, objectId, normalItem, offset))
                objectId += 1
            # add the xml for whatever items we prepared for this limb
            for name, filename, objId, item, offset in items:
                elFile = ET.SubElement(self.folder, 'file')
                elFile.set('id', str(objId))
                elFile.set('name', filename)
                itemBounds = item.boundingRect()
                elFile.set('width', str(int(itemBounds.width())))
                elFile.set('height', str(int(itemBounds.height())))
                
                timelineId = self.timelineId
                self.timelineId += 1
                ref = ET.SubElement(self.mainlineKey, 'object_ref')
                ref.set('id', str(objId))
                ref.set('z_index', str(objId))
                ref.set('key', '0')
                ref.set('timeline', str(timelineId))
                if limb.id != -1:
                    ref.set('parent', str(limb.id))

                thisKey = self._makeTimelineKey(timelineId, name)
                obj = ET.SubElement(thisKey, 'object')
                obj.set('folder', '0')
                obj.set('file', str(objId))
                boneItem = limbItem.boneItem
                rotation = boneItem.rotation()
                pos = item.pos() + offset
                pos = limbItem.mapToItem(boneItem, pos)
                obj.set('x', str(pos.x()))
                obj.set('y', str(-pos.y()))
                obj.set('angle', str(rotation))
            

    def _makeTimelineKey(self, timelineId, name):
        thisTimeline = ET.SubElement(self.animation, 'timeline')
        thisTimeline.set('id', str(timelineId))
        thisTimeline.set('name', name)
        thisKey = ET.SubElement(thisTimeline, 'key')
        thisKey.set('id', '0')
        thisKey.set('spin', '0')
        return thisKey
    
    def _relativeFilename(self, filename):
        return os.path.join(self.projectName, filename)
        