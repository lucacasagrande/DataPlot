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

import time
import plotly
import plotly.graph_objs as go
from plotly import tools

class DataPlotFigure():

    figure = None

    # id
    figure_id = None

    # type : classic or subplots
    figure_type = ''

    # figure data
    figure_data = {}

    # Traces contained if figure_data
    figure_traces = []

    # number of traces in data
    figure_data_length = 0


    def __init__(self, figure_type, figure_data={}, **kwargs):
        '''
        Initialize a plot figure
        '''

        # Set properties
        self.figure_id = int(round(time.time() * 1000))
        self.figure_data = figure_data

        # Set traces from data
        self.figure_traces = [ p.plot_trace for pid, p in self.figure_data.items() ]
        self.figure_data_length = len(self.figure_traces)

        # Set figure type based on data
        self.figure_type = figure_type
        canSubplot = True
        subplotIncompatibleTypes = ['pie']
        for pid, p in figure_data.items():
            if p.plot_type in subplotIncompatibleTypes:
                canSubplot = False
                break
        if figure_type == 'subplots' and not canSubplot:
            self.figure_type = 'classic'

        # Create figure
        self.createFigure()

        # Add traces
        self.addTraces()


    def createFigure(self):
        '''
        Create figure
        '''

        if self.figure_type in ['subplots']:
            cols = 2 if self.figure_data_length > 1 else 1
            rows = int( self.figure_data_length / 2 ) + (self.figure_data_length % 2 )
            figure = tools.make_subplots(
                cols=cols,
                rows=rows
            )

        else:
            figure = go.Figure()

        self.figure = figure



    def addTraces(self):
        '''
        Add some trace to the figure
        '''

        # Count lines in the rendered plot grid
        rows = int( self.figure_data_length / 2 ) + (self.figure_data_length % 2 )

        # Add each trace in the right position in the grid
        i=0
        for pid, p in self.figure_data.items():
            trace = p.plot_trace

            # Subplots - only for axis (no Pie chart)
            if self.figure_type in ['subplots']:
                col = 1 + i % 2
                row = int(i / 2) + 1
                self.figure.append_trace(
                    trace, row, col
                )

            # One figure with multiple plots
            else:
                if p.plot_type == 'pie' and self.figure_data_length > 1:
                    rh = float(1) / rows
                    dxa = 0 if i % 2 == 0 else 0.52
                    dxb = 0.48 if i % 2 == 0 else 1
                    row = int(i / 2) + 1
                    dya = row * rh - rh
                    dyb = row * rh
                    domain = {
                        'x': [dxa, dxb],
                        'y': [dya, dyb]
                    }
                    trace['domain'] = domain
                self.figure['data'].append( trace )

            i+=1


    def setLayout(self, p):
        '''
        Set figure layout
        '''
        layout = p.buildLayout()
        for k,v in p.plot_layout.items():
            figure['layout'][k] = v



    def buildHtml(self, include_plotlyjs=True):
        '''
        Create HTML content for the figure
        '''

        html = plotly.offline.plot(
            self.figure,
            show_link=False,
            output_type='div',
            include_plotlyjs=include_plotlyjs
        )
        return html


    def buildImage(self):
        '''
        Export as image
        '''
        return
        #plotly.image.save_as(
            #self.figure,
            #'my_plot.png'
        #)


    def exportToJSON(self):
        '''
        Export the figure to JSON
        '''
        return

    def importFromJson(self):
        '''
        Import figure from JSON
        '''
        return
