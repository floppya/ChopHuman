#!/usr/bin/env python
import os
import subprocess


def build_ui(filename, targetDir):
    print 'Building %s' % filename
    targetFilename = os.path.join(
        targetDir, 'ui_%s.py' % filename[:-len('.ui')]
    )
    cmd = 'pyuic4 %s > %s' % (
        filename, targetFilename
    )
    os.system(cmd)


def build_qrc(filename, targetDir):
    print 'Building %s' % filename
    targetFilename = os.path.join(
        targetDir, '%s_rc.py' % filename[:-len('.qrc')]
    )
    cmd = 'pyrcc4 %s > %s' % (
        filename, targetFilename
    )
    os.system(cmd)


RESOURCE_ACTIONS = {
    '.ui': build_ui,
    '.qrc': build_qrc
}


def main(sourceDir='.', targetDir='../src/chophumanfinisher/ui'):
    for filename in os.listdir(sourceDir):
        for extension, action in RESOURCE_ACTIONS.items():            
            if filename.endswith(extension):
                action(filename, targetDir)


if __name__ == '__main__':
    main()