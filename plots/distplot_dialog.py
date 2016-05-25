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
from plotly.tools import FigureFactory as FF
import tempfile
from utils import hex_to_rgb




FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/Distplot.ui'))

class DistPlotDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DistPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.Dist)

        # connect button to choose the file for local saving
        self.browseButton.clicked.connect(self.saveFile)

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
        self.traceTable.setItem(row, 3, QTableWidgetItem(str(self.colorButton.color().name())))

        self.index += 1


        # get layer and the selected fields (signals and update directly in the UI)


        # QgsVectorLayer
        lay1 = self.expField1.layer()
        # name of the field of the QgsVectorLayer
        lay1_f = self.expField1.currentText()


        # build the lists from the selected fields
        f1 = []

        # loop to use normal field or selected expression for first layer
        if self.expField1.currentField()[1] == False:
            for i in lay1.getFeatures():
                f1.append(i[lay1_f])
        else:
            filter1 = self.expField1.currentField()[0]
            exp1 = QgsExpression(filter1)
            for i in lay1.getFeatures():
                f1.append(exp1.evaluate(i, lay1.pendingFields()))


        # get the hex code from the button
        colorhex = self.colorButton.color().name()

        # convert the hex code to a rgb tuple
        colorrgb = hex_to_rgb(colorhex)


        # create dictionary with all the plot parameters (each time the button is clicked a ner dictionary is added as VALUE to the initial dictionary)

        self.plot_param = dict()
        self.plot_param["index"] = self.index
        self.plot_param["layer"] = self.LayerCombo.currentLayer()
        self.plot_param["Field"]= f1
        self.plot_param["Color"] = colorrgb
        self.plot_param["Name"] = self.expField1.currentText()


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


    def Dist(self):

        if self.rugCheck.isChecked():
            rug = True
        else:
            rug = False

        if self.histCheck.isChecked():
            set_hist = True
        else:
            set_hist = False

        if self.curveCheck.isChecked():
            set_curve = True
        else:
            set_curve = False

        size = self.binSize.value()

        set_curve_type = self.curveCombo.currentText()

        # Check if the table is empty, that is if any plot has been defined
        if self.traceTable.rowCount() == 0:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('''You don't have defined any Plot! \nPlease add a plot with the Add Trace button!'''))
            return


        # check if at least one of the checkbox is checked
        if not self.rugCheck.isChecked() and not self.histCheck.isChecked() and not self.curveCheck.isChecked():
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('''Be sure at least one of Curve, Rug or Histogram checkbox is checked!'''))
            return

        # Layout settings, these are the same for all the plots


        # initialize the dist plot
        trace = []

        # initialize the color list
        colors = []

        # initialize the label name list
        label = []

        # loop over the dictionary keys and add it to the list
        for key in self.superdict:
            x = self.superdict[key].get('Field')
            color = 'rgb' + str(self.superdict[key].get('Color'))
            name = self.superdict[key].get('Name')

            trace.append(x)
            colors.append(color)
            label.append(name)



        # build the final figure
        fig = FF.create_distplot(trace, label, colors = colors, show_rug = rug, show_curve = set_curve, show_hist = set_hist, bin_size = size, curve_type = set_curve_type)


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
