"""
This script takes as input a target SCML file with a single rest pose animation
and a different SCML file which contains a reference rest pose and a number of
additional animations which are to be mapped to the target file.
NOTE: doesn't yet do any of that
"""
import sys
from chophumanfinisher.importers.scml import SCMLImporter


if __name__ == '__main__':
    targetFilename = sys.argv[-1]
    print('importing %s' % targetFilename)
    targetImporter = SCMLImporter()
    animationSets = targetImporter.importFile(targetFilename)
    print('%s' % animationSets[0])
    