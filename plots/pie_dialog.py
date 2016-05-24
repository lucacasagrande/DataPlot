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
from qgis.gui import *
from qgis.core import QgsExpression, QgsVectorLayer
import plotly
import plotly.graph_objs as go
import tempfile


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/Pie.ui'))

class PiePlotDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PiePlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.Pie)

        # connect button to choose the file for local saving
        self.browseButton.clicked.connect(self.saveFile)

        # filter only vector layers in the QgsMapLayerComboBox
        self.LayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # get the initial index value for future iterations
        self.index = 1

        # initialize the dictionary that will store all the plot values
        self.superdict = dict()



    # function to store the path of the opened folder when saving the plot
    def saveFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName())



    def Pie(self):


        # QgsVectorLayer
        lay1 = self.expField1.layer()
        # name of the field of the QgsVectorLayer
        lay1_f = self.expField1.currentText()
        # QgsVectorLayer
        lay2 = self.expField2.layer()
        # name of the field of the QgsVectorLayer
        lay2_f = self.expField2.currentText()


        # build the lists from the selected fields
        f1 = []
        f2 = []

        # loop to use normal field or selected expression for first layer
        if self.expField1.currentField()[1] == False:
            for i in lay1.getFeatures():
                f1.append(i[lay1_f])
        else:
            filter1 = self.expField1.currentField()[0]
            exp1 = QgsExpression(filter1)
            for i in lay1.getFeatures():
                f1.append(exp1.evaluate(i, lay1.pendingFields()))

        # loop to use normal field or selected expression for second layer
        if self.expField2.currentField()[1] == False:
            for i in lay2.getFeatures():
                f2.append(i[lay2_f])
        else:
            filter2 = self.expField2.currentField()[0]
            exp2 = QgsExpression(filter2)
            for i in lay2.getFeatures():
                f2.append(exp2.evaluate(i, lay2.pendingFields()))



        # value of the slider for the alpha channel
        alphavalue = self.alpha.value()


        # Layout settings, these are the same for all the plots

        # legend checkbox (default is checked = True)
        if self.legendCheck.isChecked():
            legend = True
        else:
            legend = False


        # initialize the scatter plot with the first trace
        trace = []

        trace.append(go.Pie(
        labels = f1,
        values = f2,
        opacity = (100 - alphavalue) / 100.0
        ))


        # build the data object with all the traces added
        data = trace

        # build the layout object
        layout = go.Layout(
        showlegend = legend
        )


        # build the final figure
        fig = go.Figure(data=data, layout=layout)


        # name of the local temporary file (cross platform)
        t = tempfile.gettempdir()

        if self.filePath.text() == 'Temporary file':
            name = t + u'/temp_plotly_plot.html'
            name = str(name)
        else:
            name = self.filePath.text() + '.html'
            name = str(name)

        print self.filePath.text()

        # final function that draws the plot
        plotly.offline.plot(fig, filename=name)
