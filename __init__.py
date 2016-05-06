# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlot
                                 A QGIS plugin
 High level charts
                             -------------------
        begin                : 2016-04-27
        copyright            : (C) 2016 by Matteo Ghetta
        email                : matteo.ghetta@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataPlot class from file DataPlot.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .data_plot import DataPlot
    return DataPlot(iface)
