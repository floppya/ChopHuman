# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Tue Feb 26 10:57:37 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ChopHumanMainWindow(object):
    def setupUi(self, ChopHumanMainWindow):
        ChopHumanMainWindow.setObjectName(_fromUtf8("ChopHumanMainWindow"))
        ChopHumanMainWindow.resize(830, 654)
        self.centralwidget = QtGui.QWidget(ChopHumanMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.skeletonTreeWidget = QtGui.QTreeWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skeletonTreeWidget.sizePolicy().hasHeightForWidth())
        self.skeletonTreeWidget.setSizePolicy(sizePolicy)
        self.skeletonTreeWidget.setAutoExpandDelay(-1)
        self.skeletonTreeWidget.setObjectName(_fromUtf8("skeletonTreeWidget"))
        self.skeletonTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.skeletonTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.skeletonTreeWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.sceneGraphicsView = QtGui.QGraphicsView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sceneGraphicsView.sizePolicy().hasHeightForWidth())
        self.sceneGraphicsView.setSizePolicy(sizePolicy)
        self.sceneGraphicsView.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.sceneGraphicsView.setObjectName(_fromUtf8("sceneGraphicsView"))
        self.horizontalLayout.addWidget(self.sceneGraphicsView)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        ChopHumanMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ChopHumanMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 830, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        ChopHumanMainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(ChopHumanMainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        ChopHumanMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.statusbar = QtGui.QStatusBar(ChopHumanMainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ChopHumanMainWindow.setStatusBar(self.statusbar)
        self.actionLoadImages = QtGui.QAction(ChopHumanMainWindow)
        self.actionLoadImages.setObjectName(_fromUtf8("actionLoadImages"))
        self.actionReset = QtGui.QAction(ChopHumanMainWindow)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))
        self.menuFile.addAction(self.actionLoadImages)
        self.menuFile.addAction(self.actionReset)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(ChopHumanMainWindow)
        QtCore.QMetaObject.connectSlotsByName(ChopHumanMainWindow)

    def retranslateUi(self, ChopHumanMainWindow):
        ChopHumanMainWindow.setWindowTitle(_translate("ChopHumanMainWindow", "ChopHuman-finisher", None))
        self.label.setText(_translate("ChopHumanMainWindow", "Skeleton", None))
        self.menuFile.setTitle(_translate("ChopHumanMainWindow", "File", None))
        self.toolBar.setWindowTitle(_translate("ChopHumanMainWindow", "toolBar", None))
        self.actionLoadImages.setText(_translate("ChopHumanMainWindow", "Load Images", None))
        self.actionReset.setText(_translate("ChopHumanMainWindow", "Reset", None))

