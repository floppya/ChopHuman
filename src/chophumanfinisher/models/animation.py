

class AnimationSet(object):
    """
    Contains a group of animations. The animations should all have the same
    shaped EntityState and refer to the same images.
    """
    def __init__(self):
        self.id = -1
        self.name = ''
        self.animations = []
        self.animationByName = {}

    def addAnimation(self, animation):
        self.animations.append(animation)
        self.animationByName[animation.name] = animation

    def renameAnimation(self, animation, newName):
        if animation.name != '':
            del self.animationByName[animation.name]
        animation.name = newName
        self.animationByName[animation.name] = animation

    def removeAnimation(self, animation):
        del self.animationByName[animation.name]
        self.animations.remove(animation)

    def cloneEntityState(self):
        if self.animations:
            return self.animations[0].cloneEntityState()
        return None
    
    def cloneAnimation(self):
        if self.animations:
            return self.animations[0].clone()
        return None
    
    @property
    def entityState(self):
        if self.animations:
            return self.animations[0].entityState
        return None

    def __str__(self):
        return unicode(self).encode()

    def __unicode__(self):
        out = []
        for animation in self.animations:
            out.append(unicode(animation))
        return 'AnimationSet: [%s]' % ', '.join(out)


class Animation(object):
    """
    An Animation is an ordered set of keyframes.
    """
    def __init__(self):
        self.id = -1
        self.name = ''
        self.length = 0
        self.looping = True
        self.keyframes = []

    def addKeyframe(self, keyframe):
        newT = keyframe.time
        prevFrame = None
        for otherFrame in self.keyframes:
            if otherFrame.time > newT:
                break
            prevFrame = otherFrame
        if prevFrame:
            keyframe.id = prevFrame.id + 1
            prevFrame.length = keyframe.time - prevFrame.time
        else:
            keyframe.id = 0
        self.keyframes.insert(keyframe.id, keyframe)
        # set length of new keyframe
        nextIndex = keyframe.id + 1
        if nextIndex < len(self.keyframes):
            nextKeyframe = self.keyframes[nextIndex]
            nextT = nextKeyframe.time
            # update the ids of the other keyframes
            while nextIndex < len(self.keyframes):
                self.keyframes[nextIndex].id += 1
                nextIndex += 1
        else:
            nextT = self.length
        keyframe.length = nextT - keyframe.time

    def removeKeyframe(self, keyframe):
        prevKeyframe = self.getPrevKeyframe(keyframe, noLooping=True)
        nextKeyframe = self.getNextKeyframe(keyframe, noLooping=True)
        if prevKeyframe != keyframe:
            if nextKeyframe != keyframe:
                nextT = nextKeyframe.time
            else:
                nextT = self.length
            prevKeyframe.length = nextT - prevKeyframe.time
        index = self.keyframes.index(keyframe)
        self.keyframes.remove(keyframe)
        while index < len(self.keyframes):
            self.keyframes[index].id = index 
            index += 1

    def getKeyframe(self, keyframeId):
        return self.keyframes[keyframeId]

    def getKeyframeAt(self, t):
        result = None
        for keyframe in self.keyframes:
            if keyframe.time > t:
                break
            result = keyframe
        return result

    def getPrevKeyframe(self, keyframe, noLooping=False):
        looping = not noLooping and self.looping
        prevId = keyframe.id - 1
        if prevId < 0:
            if looping:
                prevId = len(self.keyframes) - 1
            else:
                prevId = 0
        return self.keyframes[prevId]

    def getNextKeyframe(self, keyframe, noLooping=False):
        looping = not noLooping and self.looping
        nextId = keyframe.id + 1
        if nextId >= len(self.keyframes):
            if looping:
                nextId = 0
            else:
                nextId = keyframe.id
        return self.keyframes[nextId]

    def updateEntityState(self, state, t):
        key0 = self.getKeyframeAt(t)
        key1 = self.getNextKeyframe(key0)
        if key0 == key1:
            state.copy(key0.entityState)
        else:
            relativeT = (t - key0.time) * key0.inverseLength
            state.interpolate(key0.entityState, key1.entityState, relativeT)

    def cloneEntityState(self):
        if self.keyframes:
            return self.keyframes[0].entityState.clone()
        return None

    @property
    def entityState(self):
        if self.keyframes:
            return self.keyframes[0].entityState
        return None
    
    def clone(self):
        animation = Animation()
        animation.name = self.name
        animation.length = self.length
        animation.looping = self.looping
        for keyframe in self.keyframes:
            animation.addKeyframe(keyframe.clone())
        return animation

    def __unicode__(self):
        return 'Animation(%s)' % self.name


class Keyframe(object):
    """
    Keyframe represents a pose at a specific time in an Animation.
    """
    def __init__(self, keyframeId, time, entityState):
        self.id = keyframeId
        self.time = time
        self.spin = 0
        self.length = 0.0
        self.entityState = entityState

    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, val):
        self._length = val
        if val != 0:
            self.inverseLength = 1.0 / val
        else:
            self.inverseLength = 0.0
        return val

    def clone(self):
        keyframe = Keyframe(self.id, self.time, self.entityState.clone())
        keyframe.spin = self.spin
        return keyframe


class EntityState(object):
    """
    EntityState describes the orientation of a skeleton and its skin.
    """
    def __init__(self):
        self.skins = []
        self.bones = []
        self.skinByName = {}
        self.boneByName = {}

    def addBone(self, bone, boneId=-1):
        if boneId == -1:
            bone.id = len(self.bones)
        else:
            bone.id = boneId
        while len(self.bones) <= bone.id:
            self.bones.append(None)
        self.bones[bone.id] = bone
        if bone.name != '':
            self.boneByName[bone.name] = bone

    def addSkin(self, skin):
        skin.id = len(self.skins)
        self.skins.append(skin)
        if skin.name != '':
            self.skinByName[skin.name] = skin

    def rootBone(self):
        if self.bones:
            return self.bones[0]
        return None

    def clone(self):
        state = EntityState()
        for bone in self.bones:
            newBone = bone.clone()
            state.addBone(newBone)
        for skin in self.skins:
            newSkin = skin.clone()
            state.addSkin(newSkin)
        return state

    def copy(self, other):
        for thisBone, otherBone in zip(self.bones, other.bones):
            thisBone.copy(otherBone)
        for thisSkin, otherSkin in zip(self.skins, other.skins):
            thisSkin.copy(otherSkin)

    def interpolate(self, state0, state1, t, shortest=False):
        for thisBone, state0Bone, state1Bone in zip(self.bones, state0.bones, state1.bones):
            thisBone.interpolate(state0Bone, state1Bone, t, shortest)
        for thisSkin, state0Skin, state1Skin in zip(self.skins, state0.skins, state1.skins):
            thisSkin.interpolate(state0Skin, state1Skin, t, shortest)

    def combineSelf(self, state0, shortest=False):
        self.combine(self, state0, shortest)
#        for thisBone, state0Bone in zip(self.bones, state0.bones):
#            thisBone.combine(state0Bone, state1Bone, shortest)
#        for thisSkin, state0Skin in zip(self.skins, state0.skins):
#            thisSkin.combine(state0Skin, state1Skin, shortest)

    def combine(self, state0, state1, shortest=False):
        for thisBone, state0Bone, state1Bone in zip(self.bones, state0.bones, state1.bones):
            thisBone.combine(state0Bone, state1Bone, shortest)
        for thisSkin, state0Skin, state1Skin in zip(self.skins, state0.skins, state1.skins):
            thisSkin.combine(state0Skin, state1Skin, shortest)

    def difference(self, state0, state1, shortest=False):
        for thisBone, state0Bone, state1Bone in zip(self.bones, state0.bones, state1.bones):
            thisBone.difference(state0Bone, state1Bone, shortest)
        for thisSkin, state0Skin, state1Skin in zip(self.skins, state0.skins, state1.skins):
            thisSkin.difference(state0Skin, state1Skin, shortest)

    def flatten(self, targetState):
        """
        NOTE: Unlike many of the other methods on EntityState, flatten uses 
        the targetState parameter as an output.
        """
        for thisBone, targetBone in zip(self.bones, targetState.bones):
            targetBone.copy(thisBone)
            if targetBone.parent != -1:
                parent = targetState.bones[targetBone.parent]
                targetBone.transform.applyTransform(parent.transform)
        for thisSkin, targetSkin in zip(self.skins, targetState.skins):
            targetSkin.copy(thisSkin)
            if targetSkin.parent != -1:
                parent = targetState.bones[targetSkin.parent]
                targetSkin.transform.applyTransform(parent.transform)
