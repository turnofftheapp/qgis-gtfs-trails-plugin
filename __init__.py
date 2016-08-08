# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FindTransitAccessibleTrailheads
                                 A QGIS plugin
 Uses GTFS to identify transit accessible trailheads
                             -------------------
        begin                : 2016-07-18
        copyright            : (C) 2016 by Leppek / Strong
        email                : mstrong206@gmail.com
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
    """Load FindTransitAccessibleTrailheads class from file FindTransitAccessibleTrailheads.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .TransitAccessibleTrailheads import FindTransitAccessibleTrailheads
    return FindTransitAccessibleTrailheads(iface)
