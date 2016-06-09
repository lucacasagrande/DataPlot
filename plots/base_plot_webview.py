#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import QUrl
from qgis.utils import iface
from qgis.core import QgsFeature, QgsFeatureRequest, QgsExpression, QgsMapLayer,QgsVectorLayer
import json

loadTest = """
plotWebView.log('Page loaded !');
"""

class plotWebView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(plotWebView, self).__init__(parent)

        self.page().mainFrame().addToJavaScriptWindowObject("plotWebView", self)

        self.loadFinished.connect(self.on_loadFinished)
        self.iface = iface

    @QtCore.pyqtSlot(str)
    def log(self, data):
        print data

    @QtCore.pyqtSlot(str, str)
    def processData(self, action, data):
        '''
        Process data sent by javascript
        '''
        if not data:
            return

        pdata = self.json_decode(data)
        if action == 'log':
            self.log(pdata)

        if action == 'select':
            self.selectFeatureInLayer(pdata)


    def selectFeatureInLayer(self, pdata):
        '''
        Select features in source layer corresponding on passed data
        '''
        a = pdata['properties']
        b = a['name'].split('|')
        # Get layer
        lid = b[0]
        layer = self.getQgisLayerById(lid)
        if not layer:
            return

        # Get passed field and val
        field = b[2]
        if a['type'] == 'pie':
            val = pdata['label']
        else:
            val = pdata['x']
        if not isinstance(val, (long, int)):
            val = "'%s'" % val

        exp = '"%s" IN ( %s )' % (
            field,
            val
        )
        #print exp
        expr = QgsExpression(exp)
        it = layer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        layer.setSelectedFeatures( ids )


    def getQgisLayerById(self, myId):
        '''Get a QgsLayer by its Id'''
        for layer in self.iface.legendInterface().layers():
            if myId == layer.id():
                return layer
        return None

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
