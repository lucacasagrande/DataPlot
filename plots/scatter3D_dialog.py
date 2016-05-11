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
    os.path.dirname(__file__), '../ui/Scatter3D.ui'))

class Scatter3DPlotDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Scatter3DPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.Scatter3D)


    def Scatter3D(self):

        # get layer and the selected fields (signals and update directly in the UI)
        lay1 = self.expField1.layer()
        lay1_f = self.expField1.currentText()
        lay2 = self.expField2.layer()
        lay2_f = self.expField2.currentText()
        lay3 = self.expField3.layer()
        lay3_f = self.expField3.currentText()

        # layer for the point size
        # lay3 = self.Field3.layer()
        # lay3_f = self.Field3.currentField()


        # build the lists from the selected fields
        f1 = []
        f2 = []
        f3 = []

        # cicle to use normal field or selected expression for first layer
        if self.expField1.currentField()[1] == False:
            for i in lay1.getFeatures():
                f1.append(i[lay1_f])
        else:
            filter1 = self.expField1.currentField()[0]
            exp1 = QgsExpression(filter1)
            for i in lay1.getFeatures():
                f1.append(exp1.evaluate(i, lay1.pendingFields()))

        # cicle to use normal field or selected expression for second layer
        if self.expField2.currentField()[1] == False:
            for i in lay2.getFeatures():
                f2.append(i[lay2_f])
        else:
            filter2 = self.expField2.currentField()[0]
            exp2 = QgsExpression(filter2)
            for i in lay2.getFeatures():
                f2.append(exp2.evaluate(i, lay2.pendingFields()))


        # cicle to use normal field or selected expression for second layer
        if self.expField3.currentField()[1] == False:
            for i in lay3.getFeatures():
                f3.append(i[lay3_f])
        else:
            filter3 = self.expField3.currentField()[0]
            exp3 = QgsExpression(filter3)
            for i in lay3.getFeatures():
                f3.append(exp3.evaluate(i, lay3.pendingFields()))


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

        S = self.Size.value()


        # initialize the Bar plot with the first trace
        trace = go.Scatter3d(
        x = f1,
        y = f2,
        z = f3,
        mode = 'markers',
        name = 'nome in legenda',
        marker = dict(color = 'rgb' + str(colorrgb),
        size=S,
        opacity = (100 - alphavalue) / 100.0
        )
        )

        # build the data object
        data = [trace]

        # build the layout object
        layout = go.Layout(
        showlegend = legend,
        title = 'Titolo'
        )

        # build the final figure
        fig = go.Figure(data=data, layout=layout)

        # final function that draws the plot
        plotly.offline.plot(fig)
