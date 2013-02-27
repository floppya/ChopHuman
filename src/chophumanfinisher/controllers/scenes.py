from PyQt4 import QtCore, QtGui


class ChopHumanGraphicsScene(QtGui.QGraphicsScene):
    mainwindow = None

    def mousePressEvent(self, event):
        super(ChopHumanGraphicsScene, self).mousePressEvent(event)
        self.mainwindow.delegate.onSceneMousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(ChopHumanGraphicsScene, self).mouseMoveEvent(event)
        self.mainwindow.delegate.onSceneMouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super(ChopHumanGraphicsScene, self).mouseReleaseEvent(event)
        self.mainwindow.delegate.onSceneMouseReleaseEvent(event)
