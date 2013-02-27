#!/usr/bin/env python
import os
import subprocess


def main(sourceDir='.', targetDir='../src/chophumanfinisher/ui', targetExtension='.ui'):
    for filename in os.listdir(sourceDir):
        if filename.endswith(targetExtension):
            print 'Building %s' % filename
            targetFilename = os.path.join(
                targetDir, 'ui_%s.py' % filename[:-len(targetExtension)]
            )
            cmd = 'pyuic4 %s > %s' % (
                filename, targetFilename
            )
            os.system(cmd)


if __name__ == '__main__':
    main()