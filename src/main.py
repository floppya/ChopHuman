#!/usr/bin/env python

from PyQt4 import QtGui
from chophumanfinisher.controllers.mainwindow import ChopHumanMainWindow


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = ChopHumanMainWindow()
    app.setActiveWindow(window)
    window.show()
    app.exec_()
