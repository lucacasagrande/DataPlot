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
import time
from qgis.core import QgsMapLayer, QgsVectorLayer, QgsFeature, QgsField, QgsExpression
from PyQt4.QtCore import *
import plotly
import plotly.graph_objs as go
import tempfile

class DataPlotTrace(QObject):

    dataPlotTraceAdded = pyqtSignal(object)

    plot_id = None

    plot_layer = None

    plot_data = {}

    plot_type = 'pie'

    plot_properties = {}
    plot_layout = {}

    plot_alpha_value = 50

    plot_legend = False

    plot_title = u''

    plot_matrix = []

    plot_trace = None

    plot_path = None

    def __init__(
            self
        ):
        '''
        Initialize class instance
        '''
        QObject.__init__(self)

        self.plot_id = int(round(time.time() * 1000))


    def addLayer(self, layer):
        '''
        Add layer data source
        '''
        self.plot_layer = layer


    def setProperties(self, properties={}, **kwargs):
        '''
        Set all the plot properties
        '''
        self.plot_properties = properties


    def setLayout(self, layout={}, **kwargs):
        '''
        Set all the plot layout
        '''
        self.plot_layout = layout


    def setType(self, plot_type):
        '''
        Set plot type
        '''
        self.plot_type = plot_type


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


    def setAxisDataFromLayer(self, axis, **kwargs):
        '''
        Get data in plot.ly format from layer
        '''
        layer = self.plot_layer
        data = None

        if 'expression' in kwargs:
            exp = QgsExpression(kwargs['expression'])
            if not exp.hasParserError():
                exp.prepare(layer.pendingFields())
                data = [ exp.evaluate(feat) for feat in layer.getFeatures() ]
            else:
                return False

        if 'fieldName' in kwargs:
            data = [feat[kwargs['fieldName']] for feat in layer.getFeatures() ]

        self.plot_data[axis] = data


    def setMatrix(self):
        '''
        Set the matrix of X, Y and optional Z
        '''
        axis = ['x', 'y', 'z']
        self.plot_matrix = []
        for a in axis:
            if a in self.plot_data:
                self.plot_matrix.append(self.plot_data[a])


    def buildPlot(self):
        '''
        Build the instance of the plot
        '''

        pt = self.plot_type
        if pt == 'pie':

            # Add needed properties
            self.plot_properties['labels'] = self.plot_data['x']
            self.plot_properties['values'] = self.plot_data['y']

            # Add plot
            trace = go.Pie(self.plot_properties)
            self.plot_trace = trace

        elif pt == 'bar':

            # Add needed properties
            self.plot_properties['x'] = self.plot_data['x']
            self.plot_properties['y'] = self.plot_data['y']

            # Add plot
            trace = go.Bar(self.plot_properties)
            self.plot_trace = trace

        elif pt == 'scatter':

            # Add needed properties
            self.plot_properties['x'] = self.plot_data['x']
            self.plot_properties['y'] = self.plot_data['y']

            # Add plot
            trace = go.Scatter(self.plot_properties)
            self.plot_trace = trace

        elif pt == 'box':

            # Add needed properties
            self.plot_properties['x'] = self.plot_data['x']
            self.plot_properties['y'] = self.plot_data['y']

            # Add plot
            trace = go.Box(self.plot_properties)
            self.plot_trace = trace



        else:
            return

    def buildLayout(self):
        '''
        Build layout from layout dictionary
        '''
        layout = go.Layout( self.plot_layout )
        return layout
