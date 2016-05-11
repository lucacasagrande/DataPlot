# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotDialog
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

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebView
from qgis.gui import *
from qgis.core import QgsExpression
import matplotlib.colors as colors
import plotly
import plotly.graph_objs as go


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/Histogram.ui'))

class HistogramPlotDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(HistogramPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.Histogram)


    def Histogram(self):

        # get layer and the selected fields (signals and update directly in the UI)
        # lay1 = self.Field1.layer()
        lay1 = self.expField.layer()
        # lay1_f = self.Field1.currentField()
        lay1_f = self.expField.currentText()



        # build the lists from the selected fields
        f1 = []


        # cicle to use normal field or selected expression
        if self.expField.currentField()[1] == False:
            for i in lay1.getFeatures():
                f1.append(i[lay1_f])
        else:
            filter = self.expField.currentField()[0]
            exp = QgsExpression(filter)
            for i in lay1.getFeatures():
                f1.append(exp.evaluate(i, lay1.pendingFields()))

        # get the color button and the hex raw color code of the selected color
        colbutton = self.colorButton
        colorhex = colbutton.color().name()

        # convert the hex color code to rgb code
        colorrgb = colors.hex2color(colorhex)


        # value of the slider for the alpha channel
        alphavalue = self.alpha.value()


        # legend checkbox (default is checked = True)
        if self.legendCheck.isChecked():
            legend = True
        else:
            legend = False

        # initialize the Bar plot with the first trace
        trace = go.Histogram(
        x = f1,
        # build the dictionary for the style (color, ecc..)
        # color should be built by creating an unique string
        marker = dict(color = 'rgb' + str(colorrgb)
        ),
        opacity = (100 - alphavalue) / 100.0
        )

        # build the data object
        data = [trace]

        # build the layout object
        layout = go.Layout(
        showlegend = legend
        )

        # build the final figure
        fig = go.Figure(data=data, layout=layout)

        # final function that draws the plot
        plotly.offline.plot(fig)
