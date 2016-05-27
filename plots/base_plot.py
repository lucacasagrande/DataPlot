# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Plot
                                 A QGIS plugin
 High level charts
                             -------------------
        begin                : 2016-04-27
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Matteo Ghetta
        email                : matteo.ghetta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.core import QgsMapLayer, QgsVectorLayer, QgsFeature, QgsField, QgsExpression
from PyQt4.QtCore import QVariant

class basePlot():

    plot_layer = None

    plot_data = {}

    plot_type = 'pie'

    plot_properties = {}

    plot_alpha_value = None

    plot_legend = False

    plot_title = u''

    def __init__(
            self
        ):
        '''
        Initialize class instance
        '''
        print u"Initialize plot"

    def addLayer(self, layer):
        '''
        Add layer data source
        '''
        self.plot_layer = plot_layer


    def setProperties(self, properties={}, kwargs**):
        '''
        Set all the plot properties
        '''
        self.plot_properties[prop] = val


    def setType(self, plot_type):
        '''
        Set plot type
        '''
        self.plot_type = plot_type


    def setAlpha(self, plot_alpha_value):
        '''
        Set plot alpha value
        '''
        self.plot_alpha_value = plot_alpha_value


    def setLegend(self, plot_legend):
        '''
        Set plot legend active or not
        '''
        self.plot_legend = plot_legend


    def setTitle(self, plot_title):
        '''
        Set plot title
        '''
        self.plot_title = plot_title


    def setMarkerSize(self, size):
        '''
        Set plot marker size
        '''
        return True


    def setDataFromLayer(self, axis, fieldName=None, expression=None):
        '''
        Get data in plot.ly format from layer
        '''
        if expression:
            exp = QgsExpression(expression)
            if exp.isValid():
                data = [ exp.evaluate(feat, lay1.pendingFields() ) for feat in layer.getFeatures() ]
            else:
                return False

        if fieldName:
            data = [feat[fieldName] for feat in layer.getFeatures() ]

        self.plot_data[axis] = data

