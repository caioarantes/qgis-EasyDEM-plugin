# -*- coding: utf-8 -*-
"""
/***************************************************************************
 easydem
                                 A QGIS plugin
 Get Digital Elevation Model (DEM) data from Google Earth Engine and plot as raster layer it contour lines, make elevation maps.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-11-13
        copyright            : (C) 2024 by Caio Arantes
        email                : caiosimplicioarantes@gmail.com
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
    """Load easydem class from file easydem.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .easy import easydem
    return easydem(iface)
