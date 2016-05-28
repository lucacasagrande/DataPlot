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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QUrl
from PyQt4.QtGui import QAction, QIcon, QVBoxLayout

# Import the code for the dialog
from data_plot_dialog import DataPlotDialog
import os.path
import tempfile
import time
from qgis.gui import QgsMapLayerProxyModel
from DataPlot.plots.base_plot import BasePlot
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

        # Add data to vertical/horizontal combo
        self.orientations = {
            'vertical': self.tr('Vertical'),
            'horizontal': self.tr('Horizontal')
        }
        self.dlg.orientationCombo.clear()
        for k,v in self.orientations.items():
            self.dlg.orientationCombo.addItem(v, k)

        self.plot_figures = []


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

        self.dlg.addPlotButton.clicked.connect(self.instanciateSinglePlot)
        self.dlg.renderPlotButton.clicked.connect(self.renderPlot)

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
            title = str( time.time() )
        if clear:
            self.dlg.plotList.clear()

        self.dlg.plotList.appendPlainText(u'%s' % str(title).upper())
        self.dlg.plotList.appendPlainText(u'%s' % str(message))
        self.dlg.plotList.appendPlainText(u'' )

    def createFigure(self, ftype, cols=2, rows=1):
        '''
        Create a plot figure
        '''

        # Build a figure
        if ftype == 'pie':
            figure = go.Figure()
        else:
            figure = tools.make_subplots(
                rows=rows,
                cols=cols
            )

        fig_id = time.time()

        return figure


    def readPlotParams(self):
        '''
        Adds a new plot configuration
        '''
        plotParams = {}

        plotParams['layer'] = self.dlg.expFieldX.layer()

        idx = self.dlg.plotTypeCombo.currentIndex()
        ptype = self.dlg.plotTypeCombo.itemData(idx)
        plotParams['type'] = ptype

        plotParams['x'] = self.dlg.expFieldX
        plotParams['y'] = self.dlg.expFieldY
        plotParams['z'] = self.dlg.expFieldZ
        plotParams['opacity'] = (100 - self.dlg.alpha.value()) / 100.0
        plotParams['showlegend'] = self.dlg.legendCheck.isChecked()
        plotParams['title'] = self.dlg.plotTitle.text()

        return plotParams

    def instanciateSinglePlot(self):
        '''
        Uses the base class for instanciating a single plit
        '''
        # Get params
        plotParams = self.readPlotParams()

        # Instanciate the base plot class
        p = BasePlot()

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
        for k,v in axis.items():
            if not v.currentText():
                continue
            if v.currentField()[1]:
                p.setAxisDataFromLayer(k, fieldName=v.currentText() )
            else:
                p.setAxisDataFromLayer(k, expression=v.currentField()[0] )

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

        # Set custom layout properties based on type
        p.buildPlot()

        # Create a new figure
        layout = go.Layout( p.plot_layout )
        figure = self.createFigure(plotParams['type'], 1, 2)
        self.log( str(figure) , 'figure created')

        trace = p.plot_trace
        for k,v in p.plot_layout.items():
            figure['layout'][k] = v

        if plotParams['type'] != 'pie':
            figure.append_trace(trace, 1, 1)
        else:
            self.log( trace, 'trace for pie' )
            figure['data'].append( trace )

        self.plot_figures.append(figure)




    def buildPlotHtml(self, figure):
        '''
        Build the HTML for a figure
        '''
        html = plotly.offline.plot(
            figure,
            show_link=False,
            output_type='div'
        )
        return html


    def renderPlot(self):
        '''
        Insert the added plot to the webview
        '''
        self.log( self.plot_figures, 'plot_figures after trace added' )
        figure = self.plot_figures[0]
        html = self.buildPlotHtml(figure)

        layout = self.dlg.webViewPage.layout()
        items = (layout.itemAt(i) for i in range(layout.count()))
        self.webview.loadHtml(html)
        self.plot_figures = []


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
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
