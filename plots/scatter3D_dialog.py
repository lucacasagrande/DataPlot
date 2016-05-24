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
from utils import hex_to_rgb


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

        # connect button to choose the file for local saving
        self.browseButton.clicked.connect(self.saveFile)

        # method to connect the changing layer to data defined button
        self.LayerCombo.layerChanged.connect(self.updateData)

        # filter only vector layers in the QgsMapLayerComboBox
        self.LayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # connect button to signals
        self.addTrace.clicked.connect(self.addNewTrace)
        self.deleteTrace.clicked.connect(self.removeTrace)

        # get the initial index value for future iterations
        self.index = 1

        # initialize the dictionary that will store all the plot values
        self.superdict = dict()



    # function to store the path of the opened folder when saving the plot
    def saveFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName())


    # slot of data defined receive signal of MapLayerComboBox
    @pyqtSlot(QgsVectorLayer)
    def updateData(self, layer):
        self.dataDefined.init(layer)



    def addNewTrace(self):
        '''
        fill the table with the parameters added in the dialog
        '''
        row = self.traceTable.rowCount()
        self.traceTable.insertRow(row)

        # fill the table with each paramter entered
        self.traceTable.setItem(row, 0, QTableWidgetItem(str(self.index)))
        self.traceTable.setItem(row, 1, QTableWidgetItem(str(self.LayerCombo.currentText())))
        self.traceTable.setItem(row, 2, QTableWidgetItem(str(self.expField1.currentText())))
        self.traceTable.setItem(row, 3, QTableWidgetItem(str(self.expField2.currentText())))
        self.traceTable.setItem(row, 4, QTableWidgetItem(str(self.expField3.currentText())))
        if self.dataDefined.isActive():
            self.traceTable.setItem(row, 5, QTableWidgetItem(str(self.dataDefined.getField())))
        else:
            self.traceTable.setItem(row, 5, QTableWidgetItem(str(self.Size.value())))
        self.traceTable.setItem(row, 6, QTableWidgetItem(str(self.colorButton.color().name())))
        self.traceTable.setItem(row, 7, QTableWidgetItem(str(self.alpha.value())))

        self.index += 1


        # get layer and the selected fields (signals and update directly in the UI)

        # get layer and the selected fields (signals and update directly in the UI)
        lay1 = self.expField1.layer()
        lay1_f = self.expField1.currentText()
        lay2 = self.expField2.layer()
        lay2_f = self.expField2.currentText()
        lay3 = self.expField3.layer()
        lay3_f = self.expField3.currentText()


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


        # get the hex code from the button
        colorhex = self.colorButton.color().name()

        # convert the hex code to a rgb tuple
        colorrgb = hex_to_rgb(colorhex)


        # value of the slider for the alpha channel
        alphavalue = self.alpha.value()

        # size settings
        if self.dataDefined.isActive() == False:
            markSize = self.Size.value()
        else:
            markSize = []
            if self.dataDefined.useExpression() == True:
                sizefilter = self.dataDefined.getExpression()
                sizeexp = QgsExpression(sizefilter)
                for i in self.LayerCombo.currentLayer().getFeatures():
                    markSize.append(sizeexp.evaluate(i, self.LayerCombo.currentLayer().pendingFields()))
            else:
                for i in self.LayerCombo.currentLayer().getFeatures():
                    markSize.append(i[self.dataDefined.getField()])



        # create dictionary with all the plot parameters (each time the button is clicked a ner dictionary is added as VALUE to the initial dictionary)

        self.plot_param = dict()
        self.plot_param["index"] = self.index
        self.plot_param["layer"] = (self.LayerCombo.currentLayer())
        self.plot_param["X"]= f1
        self.plot_param["Y"] = f2
        self.plot_param["Z"] = f3
        self.plot_param["Size"]= markSize
        self.plot_param["Color"] = colorrgb
        self.plot_param["Transparency"] = alphavalue
        self.plot_param["Name"] = self.expField2.currentText()


        # add the dictionary with plot values to the initial dictionary
        self.superdict[row] = self.plot_param


    def removeTrace(self):
        '''
        remove the selected rows in the table and delete the plot parameters from the dictionary
        '''
        selection = self.traceTable.selectionModel()
        rows = selection.selectedRows()

        for row in reversed(rows):
            index = row.row()
            self.traceTable.removeRow(row.row())
            del self.superdict[row.row()]




    def Scatter3D(self):

        # Layout settings, these are the same for all the plots


        # legend checkbox (default is checked = True)
        if self.legendCheck.isChecked():
            legend = True
        else:
            legend = False


        # plot title
        plotTitle = self.pltTitle.text()

        # initialize the scatter plot with the first trace
        trace = []

        # loop over the dictionary keys and add it to the list
        for key in self.superdict:
            x = self.superdict[key].get('X')
            y = self.superdict[key].get('Y')
            z = self.superdict[key].get('Z')
            size = self.superdict[key].get('Size')
            color = self.superdict[key].get('Color')
            transparency = self.superdict[key].get('Transparency')
            name = self.superdict[key].get('Name')


            # initialize the Bar plot with the first trace
            trace.append(go.Scatter3d(
            x = x,
            y = y,
            z = z,
            mode = 'markers',
            name = name,
            marker = dict(color = 'rgb' + str(color),
            size = size,
            opacity = (100 - transparency) / 100.0
            )))

        # build the data object with all the traces added
        data = trace

        # build the layout object
        layout = go.Layout(
        showlegend = legend,
        title = plotTitle
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
