ChopHuman
=========

About
-----
ChopHuman is a collection of tools for speeding up the creation of
[2-D cutout-style](http://en.wikipedia.org/wiki/Cutout_animation) characters
from [MakeHuman](http://www.makehuman.org/) models.

It currently exists as the following tools:
* A [Blender](http://www.blender.org/) 2.6x plug-in which renders each body
part in isolation.
* A finishing application which is meant to simplify placement of bones, 
the trimming of limb images and the export of the rigged character to
popular animation software (currently only supports Spriter).

This is a real work-in-progress so using it will probably be touchy for awhile.
Apologies to anyone who wants to extend the finishing app as it was something
of an exercise in learning PyQt. Suggestions and code are always welcome.

ChopHuman is in no way endorsed or sponsored by MakeHuman. Nonetheless, ChopHuman
thinks MakeHuman is pretty cool.

Prerequisites
-------------
* The blender plugin (blender/addons/chophuman) must be installed and enabled.
* The finishing app requires python 2.7, PyQt4 and elementtree. There is a pip
requirements.txt alongside this readme.  

Usage
-----

Step 1: 3d -> 2d

* design a character in [MakeHuman](http://www.makehuman.org/)
* import it to [Blender](http://www.blender.org/) via the mhx format
* enter object mode and select the top-most scene item of the MakeHuman model
* The ChopHuman panel should be available in the Object properties pane
* First, click 'chop' which will create masks for each limb. This may take a
little bit of time to run.
* Now, click 'render'. After configuring the renderer output it will make
individual renderings of each limb. This also may take awhile.

Step 2: Clean-up and rig

The finishing program is incomplete, buggy and annoying to use, but can be
used to reskin existing skeletons and retarget their associated animations.
The retargeting feature requires an animation named 'rest' with two frames.
The first frame should be the reference pose for the other animations. The
second frame is the corrected mapping. The following instructions will walk
you through the creation of these.

* Start up the finishing program via the chophuman shell/batch scripts
* First, use 'File > Import Spriter' to *cross-your-fingers* import a SCML file.
* Make sure there's an animation named 'rest' which contains a reference pose as the first frame
and then add a second key by extending the animtion length, moving to the end of the timeline,
and clicking 'Add Key' (this makes new keyframe that reflects the current animation state).
* Choose 'File > Load Images' from the file menu and select all of the images rendered by the blender plugin.
The program will attempt to match up the images with the appropriate bones by name.
* Check 'Freeze skins' (this allows you to move the bones independently of the skins) and go into
'Place bone' mode (the tool with the hand icon).
* Bone by bone, drag the skeleton into place over the images
* Uncheck 'Freeze skins', click 'Retarget'
* Check the other animations to make sure it worked.

Now you may:
* continue to adjust the location of the bones
* trim the limb images
* pose the limbs to check placement
* export to SCML
* be frustrated by bugs and other limitations

NOTES
-----
* You must select the bone in the skeleton tree widget to trim/position it.
* You can switch amongst the different editing modes via the 'asdf' keys.
* In trim mode, left-mouse masks out the image and right-mouse unmasks.

License
-------
Code: MIT

Majority of the icons: Creative Commons (Attribution 3.0 Unported) 
Attribution: [Momenticons](http://momentumdesignlab.com)
They have a couple of large CC licensed icon sets worth checking out.

Bone icon: http://banzaitokyo.com CC Attribution 3.0

If the icon looks crappy, it's because it is a composite I made.
