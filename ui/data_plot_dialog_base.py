# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data_plot_dialog_base.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(527, 251)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(320, 200, 176, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.scatterButton = QtGui.QPushButton(Dialog)
        self.scatterButton.setGeometry(QtCore.QRect(10, 20, 98, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.scatterButton.setFont(font)
        self.scatterButton.setMouseTracking(False)
        self.scatterButton.setStyleSheet(_fromUtf8("text-align: top;"))
        self.scatterButton.setDefault(False)
        self.scatterButton.setFlat(False)
        self.scatterButton.setObjectName(_fromUtf8("scatterButton"))
        self.boxplotButton = QtGui.QPushButton(Dialog)
        self.boxplotButton.setGeometry(QtCore.QRect(140, 20, 85, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.boxplotButton.setFont(font)
        self.boxplotButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.boxplotButton.setIconSize(QtCore.QSize(128, 128))
        self.boxplotButton.setObjectName(_fromUtf8("boxplotButton"))
        self.barplotButton = QtGui.QPushButton(Dialog)
        self.barplotButton.setGeometry(QtCore.QRect(10, 70, 91, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.barplotButton.sizePolicy().hasHeightForWidth())
        self.barplotButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.barplotButton.setFont(font)
        self.barplotButton.setStyleSheet(_fromUtf8("text-align: top;"))
        self.barplotButton.setIconSize(QtCore.QSize(80, 100))
        self.barplotButton.setObjectName(_fromUtf8("barplotButton"))
        self.histogramplotButton = QtGui.QPushButton(Dialog)
        self.histogramplotButton.setGeometry(QtCore.QRect(240, 10, 87, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.histogramplotButton.setFont(font)
        self.histogramplotButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.histogramplotButton.setIconSize(QtCore.QSize(64, 64))
        self.histogramplotButton.setObjectName(_fromUtf8("histogramplotButton"))
        self.pieplotButton = QtGui.QPushButton(Dialog)
        self.pieplotButton.setGeometry(QtCore.QRect(130, 70, 121, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pieplotButton.setFont(font)
        self.pieplotButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.pieplotButton.setIconSize(QtCore.QSize(64, 64))
        self.pieplotButton.setObjectName(_fromUtf8("pieplotButton"))
        self.scatter3DButton = QtGui.QPushButton(Dialog)
        self.scatter3DButton.setGeometry(QtCore.QRect(270, 60, 123, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.scatter3DButton.setFont(font)
        self.scatter3DButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.scatter3DButton.setObjectName(_fromUtf8("scatter3DButton"))
        self.distplotButton = QtGui.QPushButton(Dialog)
        self.distplotButton.setGeometry(QtCore.QRect(10, 120, 123, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.distplotButton.setFont(font)
        self.distplotButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.distplotButton.setIconSize(QtCore.QSize(128, 128))
        self.distplotButton.setObjectName(_fromUtf8("distplotButton"))
        self.polarButton = QtGui.QPushButton(Dialog)
        self.polarButton.setGeometry(QtCore.QRect(150, 120, 123, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.polarButton.setFont(font)
        self.polarButton.setStyleSheet(_fromUtf8("text-align: top"))
        self.polarButton.setIconSize(QtCore.QSize(128, 128))
        self.polarButton.setObjectName(_fromUtf8("polarButton"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.scatterButton.setText(_translate("Dialog", "Scatter Plot", None))
        self.boxplotButton.setText(_translate("Dialog", "Box Plot", None))
        self.barplotButton.setText(_translate("Dialog", "Bar Plot", None))
        self.histogramplotButton.setText(_translate("Dialog", "Histogram", None))
        self.pieplotButton.setText(_translate("Dialog", "Pie Chart", None))
        self.scatter3DButton.setText(_translate("Dialog", "3D Scatter Plot", None))
        self.distplotButton.setText(_translate("Dialog", "Distibution Plot", None))
        self.polarButton.setText(_translate("Dialog", "Polar Plot", None))

import resources_rc
