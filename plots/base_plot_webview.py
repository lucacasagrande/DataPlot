#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import QUrl

getJsValue = """

myWindow.showMessage('initial color ' + document.body.style.background);
function changeBodyBackground(color){
    document.body.style.background = color;
    myWindow.showMessage('color changed into ' + color);
}
"""

class plotWebView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(plotWebView, self).__init__(parent)

        self.page().mainFrame().addToJavaScriptWindowObject("plotWebView", self)

        self.loadFinished.connect(self.on_loadFinished)

    @QtCore.pyqtSlot(str)
    def showMessage(self, message):
        print "Message from website:", message

    @QtCore.pyqtSlot()
    def on_loadFinished(self):
        self.page().mainFrame().evaluateJavaScript(getJsValue)

    def changeBodyBackground(self, color):
        self.page().mainFrame().evaluateJavaScript( "changeBodyBackground('%s')" % color )

    def loadHtml(self, html):
        self.setHtml(html)

    def loadUrl(self, url):
        self.load(QUrl(url))
