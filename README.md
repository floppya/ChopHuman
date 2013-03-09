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

ChopHuman is in no way endorsed or sponsored by MakeHuman.

This is a real work-in-progress so using it will probably be touchy for awhile.
Apologies to anyone who wants to extend the finishing app as I've not very
experienced with PyQt. Suggestions and code are always welcome.

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

* Start up the finishing program via the chophuman shell/batch scripts or just run src/main.py
* First, use 'File > Import Spriter' to import a skeleton and animations from an SCML file.
* Then choose 'File > Load Images' from the file menu and select all of the images rendered by the blender plugin.
The program will attempt to match up the images with the appropriate bones by name.
* Choose the 'rest' animation, change the animation duration to 2ms or something.
* Move to the end of the animation and click 'add key' to add a new keyframe
* Ensure 'Freeze skins' is checked (this allows you to move the bones relative to the skins) and
'Pose' mode is enabled
* Move the skeleton into place over the images
* Uncheck 'Freeze skins', click 'Retarget'

Now you may:
* adjust the location of the bones
* trim the limb images
* pose the limbs to check placement
* export to Spriter

NOTES
* You must select the bone in the skeleton tree widget to trim/position it.
* You can switch amongst the different editing modes via the 'asdf' keys.
* In trim mode, left-mouse masks out the image and right-mouse unmasks.

License
-------
MIT
