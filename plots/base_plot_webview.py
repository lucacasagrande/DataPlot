#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import QUrl
import json

loadTest = """
plotWebView.log('Page loaded !');
"""

class plotWebView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(plotWebView, self).__init__(parent)

        self.page().mainFrame().addToJavaScriptWindowObject("plotWebView", self)

        self.loadFinished.connect(self.on_loadFinished)

    @QtCore.pyqtSlot(str)
    def log(self, data):
        print "log"
        print data

    @QtCore.pyqtSlot()
    def on_loadFinished(self):
        self.page().mainFrame().evaluateJavaScript(loadTest)

    def loadHtml(self, html):
        self.setHtml(html)

    def loadUrl(self, url):
        self.load(QUrl(url))

    @QtCore.pyqtSlot(str)
    def json_encode(self, jsobj):
        return json.dumps(jsobj)

    @QtCore.pyqtSlot()
    def json_decode(self, jsstr):
        return json.loads(jsstr)
