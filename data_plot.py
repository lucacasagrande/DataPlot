# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlot
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QUrl, Qt
from PyQt4.QtGui import QAction, QIcon, QVBoxLayout, QTableWidgetItem

# Import the code for the dialog
from data_plot_dialog import DataPlotDialog
from data_plot_figure import DataPlotFigure
from data_plot_trace import DataPlotTrace
import os.path
import tempfile
import time
from qgis.gui import QgsMapLayerProxyModel
from DataPlot.plots.base_plot_webview import plotWebView
from DataPlot.plots.utils import *

import plotly
from plotly import tools
import plotly.graph_objs as go


class DataPlot:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DataPlot_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = DataPlotDialog()

        # Add data to plotTypeCombo
        self.plot_types = {
            'pie': self.tr('Pie chart'),
            'box': self.tr('Box plot'),
            'histogram': self.tr('Histogram'),
            'bar': self.tr('Bar Chart'),
            'distribution': self.tr('Distribution plot'),
            'scatter': self.tr('Scatter plot'),
            'scatter3d': self.tr('Scatter plot 3D')
        }
        self.dlg.plotTypeCombo.clear()
        for k,v in self.plot_types.items():
            self.dlg.plotTypeCombo.addItem(v, k)

        self.plot_types_widgets = {
            self.dlg.LayerCombo: ['all'],
            self.dlg.LayerCombo_label: ['all'],
            self.dlg.expFieldX: ['all'],
            self.dlg.expFieldY: ['all'],
            self.dlg.legendCheck: ['all'],
            self.dlg.plotTitle: ['all'],
            self.dlg.alpha: ['all'],
            self.dlg.alpha_label: ['all'],
            self.dlg.alphaBox: ['all'],

            self.dlg.colorButton: ['all_but_pie'],
            self.dlg.colorButton_label: ['all_but_pie'],
            self.dlg.xAxisCheck: ['all_but_pie'],
            self.dlg.xAxisText: ['all_but_pie'],
            self.dlg.yAxisCheck: ['all_but_pie'],
            self.dlg.yAxisText: ['all_but_pie'],

            self.dlg.colorButton2: ['bar', 'box'],
            self.dlg.colorButton2_label: ['bar', 'box'],
            self.dlg.widthBox: ['bar', 'box'],
            self.dlg.widthBox_label: ['bar', 'box'],
            self.dlg.barCombo: ['bar'],
            self.dlg.barCombo_label: ['bar'],
            self.dlg.orientationCombo: ['bar'],
            self.dlg.orientationCombo_label: ['bar'],

            self.dlg.histCombo: ['histogram'],

            self.dlg.outlierCombo: ['box'],
            self.dlg.outlierCombo_label: ['box'],
            self.dlg.statCombo: ['box'],
            self.dlg.statCombo_label: ['box'],

            self.dlg.rugCheck: ['distribution'],
            self.dlg.histCheck: ['distribution'],
            self.dlg.curveCheck: ['distribution'],
            self.dlg.binSize: ['distribution'],
            self.dlg.curveCombo: ['distribution'],

            self.dlg.regressionCheck: ['scatter'],
            self.dlg.equationCheck: ['scatter'],
            self.dlg.rangeCheck: ['scatter'],
            self.dlg.logXCheck: ['scatter'],
            self.dlg.logYCheck: ['scatter'],
            self.dlg.symbolCombo: ['scatter','scatter3d'],
            self.dlg.symbolCombo_label: ['scatter','scatter3d'],
            self.dlg.Size: ['scatter','scatter3d'],
            self.dlg.Size_label: ['scatter','scatter3d'],
            self.dlg.dataDefined: ['scatter'],

            self.dlg.expFieldZ: ['scatter3d'],
            self.dlg.expFieldZ_label: ['scatter3d'],
            self.dlg.dataDefined: ['scatter3d'],
            self.dlg.zAxisCheck: ['scatter3d'],
            self.dlg.zAxisText: ['scatter3d']
        }

        # Add data to vertical/horizontal combo
        self.orientations = {
            'v': self.tr('Vertical'),
            'h': self.tr('Horizontal')
        }
        self.dlg.orientationCombo.clear()
        for k,v in self.orientations.items():
            self.dlg.orientationCombo.addItem(v, k)

        # Add data to symbol type combo
        self.symbolType = {
            'markers': self.tr('Points'),
            'lines': self.tr('Lines'),
            'markers+lines': self.tr('Points and Lines')
        }
        self.dlg.symbolCombo.clear()
        for k,v in self.symbolType.items():
            self.dlg.symbolCombo.addItem(v, k)

        # Add data to vertical/horizontal combo
        self.figureTypes = {
            'classic': self.tr(u'Classic'),
            'subplots': self.tr(u'Subplots with shared axis')
        }

        # Add data for the showing statistics type (box plot only)
        self.statType = {
            True: self.tr('Mean'),
            'sd': self.tr('Standard Deviation'),
            False: self.tr('No Statistics')
        }
        self.dlg.statCombo.clear()
        for k,v in self.statType.items():
            self.dlg.statCombo.addItem(v, k)

        # Add data for the showing outliers (box plot only)
        self.outlierType = {
            False: self.tr('No Outliers'),
            'all': self.tr('Show All Outliers'),
            'suspectedoutliers': self.tr('Only Suspected Outliers'),
            'outliers': self.tr('Outliers')

        }
        self.dlg.outlierCombo.clear()
        for k,v in self.outlierType.items():
            self.dlg.outlierCombo.addItem(v, k)


        # Add overlaying mode for bars
        self.overlaying = {
            'overlay': self.tr('Overlay'),
            'stack': self.tr('Stacked')
        }
        self.dlg.histCombo.clear()
        for k,v in self.overlaying.items():
            self.dlg.histCombo.addItem(v, k)


        #
        self.dlg.figureTypeCombo.clear()
        for k,v in self.figureTypes.items():
            self.dlg.figureTypeCombo.addItem(v, k)

        self.dataPlotTraces = {}
        self.dataPlotFigures = []


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Data Plot')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DataPlot')
        self.toolbar.setObjectName(u'DataPlot')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DataPlot', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(
            self.plugin_dir,
            'icon.png'
        )
        self.add_action(
            icon_path,
            text=self.tr(u'Plots'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Connect signals/slots
        # filter only vector layers in the QgsMapLayerComboBox
        self.dlg.LayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.dlg.addPlotButton.clicked.connect(self.addTrace)
        self.dlg.removePlotButton.clicked.connect(self.removeTrace)
        self.dlg.renderFigureButton.clicked.connect(self.renderFigures)

        self.dlg.plotTypeCombo.currentIndexChanged.connect(self.refreshPlotWidgets)

        w = plotWebView()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(w)
        w.show()
        self.webview = w
        self.dlg.webViewPage.setLayout(layout)


    def log(self, message, title="", clear=False):
        '''
        Log messages
        '''
        if not title:
            title = str( int(round(time.time() * 1000)) )
        if clear:
            self.dlg.logText.clear()

        self.dlg.logText.appendPlainText(u'%s' % str(title).upper())
        self.dlg.logText.appendPlainText(u'%s' % str(message))
        self.dlg.logText.appendPlainText(u'' )


    def refreshPlotWidgets(self, idx):
        '''
        Hide of show widgets specific to
        current plot type
        '''
        cb = self.dlg.plotTypeCombo
        ptype = cb.itemData(idx)

        for k,v in self.plot_types_widgets.items():
            active = ptype in v or 'all' in v or ( ptype != 'pie' and 'all_but_pie' in v )
            k.setEnabled(active)
            try:
                k.setVisible(active)
            except:
                continue


    def readPlotParams(self):
        '''
        Adds a new plot configuration
        '''
        plotParams = {}

        plotParams['layer'] = self.dlg.expFieldX.layer()
        cb = self.dlg.plotTypeCombo
        idx = cb.currentIndex()
        ptype = cb.itemData(idx)
        plotParams['type'] = ptype

        plotParams['x'] = self.dlg.expFieldX
        plotParams['y'] = self.dlg.expFieldY
        plotParams['z'] = self.dlg.expFieldZ
        plotParams['opacity'] = (100 - self.dlg.alpha.value()) / 100.0
        plotParams['showlegend'] = self.dlg.legendCheck.isChecked()
        plotParams['title'] = self.dlg.plotTitle.text()

        return plotParams


    def addTrace(self):
        '''
        Uses the base class for instanciating a single plit
        '''
        # Get params
        plotParams = self.readPlotParams()

        # Instanciate the trace plot class
        p = DataPlotTrace()

        # Add layer
        p.addLayer( plotParams['layer'] )

        # Get type
        p.setType( plotParams['type'] )

        # Get other properties

        # Set data from fields
        axis = {}
        axis['x'] = plotParams['x']
        axis['y'] = plotParams['y']
        axis['z'] = plotParams['z']

        p.plot_data = {}
        fieldX = ''
        fieldXType = 'field'
        for k,v in axis.items():
            if not v.currentText():
                continue
            if v.currentField()[1]:
                fieldX = v.currentText()
                fieldXType = 'field'
                p.setAxisDataFromLayer(k, fieldName=fieldX )
            else:
                fieldX = v.currentField()[0]
                fieldXType = 'expression'
                p.setAxisDataFromLayer(k, expression=fieldX )

        p.setMatrix()

        # Set properties
        plot_properties = {
            'opacity': plotParams['opacity']
        }
        # Set custom properties based on type
        customProperties = self.getTypeProperties(plotParams['type'])
        for k,v in customProperties.items():
            plot_properties[k] = v

        p.setProperties( plot_properties )

        # Set layout properties
        plot_layout = {
            'showlegend': plotParams['showlegend'],
            'title': plotParams['title']
        }
        # Set custom layout props based on type
        cLayout = self.getTypeLayout(plotParams['type'])
        for k,v in cLayout.items():
            plot_layout[k] = v
        p.setLayout( plot_layout )

        # Build plot depending on type
        p.buildPlot()

        # Get trace
        trace = p.plot_trace

        # Add a name with layer id and x field
        trace['name'] = '%s|%s|%s' % (
            p.plot_layer.id(),
            fieldXType,
            fieldX
        )

        # Add trace
        self.dataPlotTraces[p.plot_id] = p
        self.log( trace, 'added trace')

        # Refresh plots table
        self.refreshPlotTable()

    def removeTrace(self):
        '''
        Remove selected trace
        '''
        # Get selected lines
        table = self.dlg.plotTable
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return

        # Modify values for each line
        for index in lines:
            row = index.row()
            id_item = table.item( row, 0 )
            trace_id = id_item.data(0)
            table.removeRow(row)
            print self.dataPlotTraces
            self.dataPlotTraces.pop(trace_id, None)
            print self.dataPlotTraces


    def refreshPlotTable(self):
        '''
        Refresh the table of plots
        '''
        table = self.dlg.plotTable

        # empty previous content
        for row in range(table.rowCount()):
            table.removeRow(row)
        table.setRowCount(0)

        # Add lines
        for pid, p in self.dataPlotTraces.items():
            # Set row and column count
            twRowCount = table.rowCount()

            # add a new line
            table.setRowCount( twRowCount + 1 )

            # Id
            newItem = QTableWidgetItem()
            newItem.setData( Qt.EditRole, pid )
            table.setItem(twRowCount, 0, newItem)

            # Type
            newItem = QTableWidgetItem()
            newItem.setData( Qt.EditRole, p.plot_type )
            table.setItem(twRowCount, 1, newItem)


    def createFigures(self):
        '''
        Create a figure instance
        '''
        # Reset previous figures
        self.dataPlotFigures = []

        # Get figure parameters from ui
        idx = self.dlg.figureTypeCombo.currentIndex()
        ftype = self.dlg.figureTypeCombo.itemData(idx)

        # Separate incompatible charts
        a = self.dataPlotTraces
        pie_traces = dict( (k,v) for k,v in a.items() if v.plot_type == 'pie' )
        other_traces = dict( (k,v) for k,v in a.items() if v.plot_type != 'pie' )

        if pie_traces:
        # Instanciate figure
            f1 = DataPlotFigure(
                figure_type=ftype,
                figure_data=pie_traces
            )
            # Add figure to self
            self.dataPlotFigures.append(f1)
            self.log( f1.figure, 'added figure')

        if other_traces:
            # Instanciate figure
            f2 = DataPlotFigure(
                figure_type=ftype,
                figure_data=other_traces
            )
            # Add figure to self
            self.dataPlotFigures.append(f2)
            self.log( f2.figure, 'added figure')


    def renderFigures(self):
        '''
        Render a figure and show it in the webview
        '''
        # Create needed figures
        self.createFigures()

        # Get html from configured figures
        html = ''
        for i,figure in enumerate(self.dataPlotFigures):
            include_plotlyjs=False if i>0 else True
            html+= figure.buildHtml(include_plotlyjs)

        html = html.replace(
            '</script><div',
            '</script><table width="100%"><tr><td><div'
        )
        html+= '</td></tr></table>'

        html+= 'Click on the chart and <select id="dataPlotAction">'
        html+= '<option value="select">' + self.tr('Select corresponding features') + '</option>';
        html+= '<option value="zoom">' + self.tr('Zoom to corresponding features') + '</option>';
        html+= '<option value="filter">' + self.tr('Filter layer with corresponding features') + '</option>';

        html+= '</select> (experimental !)'
        html+= '<div id="dataPlotLog"></div>'

        # Add javascript code to interact with QGIS
        html+= self.getJavascriptInteractionCode()

        # Create temp file
        tmpdir = tempfile.mkdtemp()
        predictable_filename = 'dataplot.html'
        tpath = os.path.join(tmpdir, predictable_filename)
        print tpath
        with open(tpath, 'w') as afile:
            afile.write(html)

        # Load html
        self.webview.loadUrl(tpath)

        # Go to webview
        self.dlg.listWidget.setCurrentRow(1)


    def getJavascriptInteractionCode(self):
        '''
        Add some javascript code to interact with QGIS
        '''
        js = ''
        with open( os.path.join( self.plugin_dir, 'qgisJsInteraction.js'), 'r' ) as jsfile:
            js = jsfile.read()

        return js

    def getTypeProperties(self, ptype):
        '''
        Get properties specific to a chart type
        '''
        sprop = {}
        if ptype == 'bar':
            color = hex_to_rgb(self.dlg.colorButton.color().name())
            color_line = hex_to_rgb(self.dlg.colorButton2.color().name())
            width = self.dlg.widthBox.value()

            sprop['marker'] = dict(
                color = 'rgb' + color,
                line = dict(
                    color = 'rgb' + str(color_line),
                    width = width
                )
            )

            idx = self.dlg.orientationCombo.currentIndex()
            ori = self.dlg.orientationCombo.itemData(idx)

            sprop['orientation'] = ori




        if ptype == 'scatter':
            color = hex_to_rgb(self.dlg.colorButton.color().name())
            color_line = hex_to_rgb(self.dlg.colorButton2.color().name())
            width = self.dlg.widthBox.value()
            size = self.dlg.Size.value()

            idx = self.dlg.symbolCombo.currentIndex()
            mode = self.dlg.symbolCombo.itemData(idx)

            sprop['mode'] = mode

            sprop['marker'] = dict(
                color = 'rgb' + color,
                size = size,
                line = dict(
                    color = 'rgb' + str(color_line),
                    width = width
                )
            )

        if ptype == 'box':
            color = hex_to_rgb(self.dlg.colorButton.color().name())
            color_line = hex_to_rgb(self.dlg.colorButton2.color().name())
            width = self.dlg.widthBox.value()


            # box fill color
            sprop['fillcolor'] = 'rgb' + color

            # outlines box color and width
            sprop['line'] = dict(
                color = 'rgb' + color_line,
                width = width
            )

            # optional outlier points color
            sprop['marker'] = dict(
                color = 'rgb' + color,
            )


            idx = self.dlg.statCombo.currentIndex()
            stat = self.dlg.statCombo.itemData(idx)

            sprop['boxmean'] = stat

            idx = self.dlg.outlierCombo.currentIndex()
            out = self.dlg.outlierCombo.itemData(idx)

            sprop['boxpoints'] = out


        if ptype == 'histogram':
            color = hex_to_rgb(self.dlg.colorButton.color().name())

            # bar color
            sprop['marker'] = dict(
                color = 'rgb' + color,
            )



        return sprop

    def getTypeLayout(self, ptype):
        '''
        Get layout properties specific to a chart type
        '''
        sprop = {}
        if ptype == 'bar':

            idx = self.dlg.orientationCombo.currentIndex()
            ori = self.dlg.orientationCombo.itemData(idx)
            sprop['orientation'] = ori

        elif ptype == 'histogram':
            # bar overlaying mode
            idx = self.dlg.histCombo.currentIndex()
            over = self.dlg.histCombo.itemData(idx)

            sprop['barmode'] = over

        return sprop






    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Data Plot'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        # show the dialog
        self.dlg.show()
        self.dlg.listWidget.setCurrentRow(0)
        self.dlg.orientationCombo.setCurrentIndex(1)
        self.refreshPlotWidgets( self.dlg.plotTypeCombo.currentIndex())

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
