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

class DataPlotFigure():

    figure = None

    # id
    figure_id = None

    # type : single, combined, subplots
    figure_type = None

    # figure data
    figure_data = []

    # number of traces in data
    figure_data_length = 0

    # figure cols and rows
    figure_cols = 1
    figure_rows = 1


    def __init__(self, figure_type='single', figure_cols=1, figure_rows=1, **kwargs):
        '''
        Initialize a plot figure
        '''

        self.figure_id = int(round(time.time() * 1000))

        self.figure_type = figure_type
        self.figure_cols = figure_cols
        self.figure_rows = figure_rows

        if figure_type in ['subplots']:
            figure = tools.make_subplots(
                rows=figure_rows,
                cols=figure_cols
            )

        elif figure_type in ['single', 'multiple'] :
            figure = go.Figure()

        else:
            figure = go.Figure()

        self.figure = figure


    def addTrace(self, trace):
        '''
        Add some trace to the figure
        '''
        self.figure_data.append(trace)
        self.figure_data_length = len(self.figure_data)

        if self.figure_type in ['single', 'multiple']:
            self.figure['data'].append( trace )

        elif self.figure_type in ['subplots']:
            self.figure.append_trace(trace, 1, 1)

        else:
            return

    def setLayout(self):
        '''
        Set figure layout
        '''
        return
        # Code taken from trace : need modification
        #layout = p.buildLayout()
        #for k,v in p.plot_layout.items():
            #figure['layout'][k] = v



    def buildHtml(self):
        '''
        Create HTML content for the figure
        '''
        html = plotly.offline.plot(
            self.figure,
            show_link=False,
            output_type='div'
        )
        return html

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
