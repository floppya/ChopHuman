

class ChopHumanExporter(object):
    """
    Base for other exporters.
    """
    fileType = ('Base Exporter', '*')
    version = '0.0'

    def export(self, animationSet, skinItemMap, filename):
        pass

    @classmethod
    def verboseName(cls):
        return 'Export %s' % (cls.fileType[0])
    
    @classmethod
    def fileFilter(cls):
        return '%s (*.%s)' % cls.fileType