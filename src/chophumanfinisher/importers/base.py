

class ChopHumanImporter(object):
    """
    Base for other importers.
    """
    fileType = ('Base Importer', '*')
    version = '0.0'

    def importFile(self, filename):
        pass

    @classmethod
    def verboseName(cls):
        return 'Import %s' % (cls.fileType[0])
    
    @classmethod
    def fileFilter(cls):
        return '%s (*.%s)' % cls.fileType