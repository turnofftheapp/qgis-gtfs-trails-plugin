# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FindTransitAccessibleTrailheads
                                 A QGIS plugin
 Uses GTFS to identify transit accessible trailheads
                              -------------------
        begin                : 2016-07-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Leppek / Strong
        email                : mstrong206@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
import osgeo.ogr, osgeo.osr #we will need some packages
from osgeo import ogr #and one more for the creation of a new field
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsVectorDataProvider  

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from TransitAccessibleTrailheads_dialog import FindTransitAccessibleTrailheadsDialog
import os.path
###import ogr2ogr


class FindTransitAccessibleTrailheads:
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
            'FindTransitAccessibleTrailheads_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = FindTransitAccessibleTrailheadsDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&TransitAccessibleTrailheads')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FindTransitAccessibleTrailheads')
        self.toolbar.setObjectName(u'FindTransitAccessibleTrailheads')

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
        return QCoreApplication.translate('FindTransitAccessibleTrailheads', message)


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

        icon_path = ':/plugins/FindTransitAccessibleTrailheads/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Identify transit accessible trailheads'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&TransitAccessibleTrailheads'),
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
        GTFSDir = self.dlg.GTFSLocation.text()
        StopsFile = self.dlg.StopsFile.text()
        StopsShapefileName = self.dlg.StopsShapefileName.text()
        #####output_shp = 
        ##output_file = open(filename, 'w')
        # See if OK was pressed
        if result:
            print "one"
            stop_id = "UNK"
            stop_name = "UNK"
            stop_lat = "UNK"
            stop_lon = "UNK"
            c_stop_id = 0
            c_stop_name = 0
            c_stop_lat = 0
            c_stop_lon = 0
            counter = 0
            text_file = os.path.join(GTFSDir, StopsFile)
            #text_file = 'C:/UWGIS/Geog569/Data/Test/stops.txt' 
            ##
            EPSG_code = 4326
            EPSG_code_WM = 3857
            StopsShapefilePath = os.path.join(GTFSDir, StopsShapefileName + ".shp")
            StopsShapefilePathWM = os.path.join(GTFSDir, StopsShapefileName + "WM.shp")
            ###export_shp = "C:/UWGIS/Geog569/Data/Test/stoptest1.shp"
            spatialReference = osgeo.osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be
            spatialReference.ImportFromEPSG(int(EPSG_code)) #here we define this reference to be the EPSG code
            driver = osgeo.ogr.GetDriverByName('ESRI Shapefile') # will select the driver for our shp-file creation.
            shapeData = driver.CreateDataSource(StopsShapefilePath) #so there we will store our data
            layer = shapeData.CreateLayer('layer', spatialReference, osgeo.ogr.wkbPoint) #this will create a corresponding layer for our data with given spatial information.
            layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
            index = 0
            spatialReferenceWM = osgeo.osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be			
            spatialReferenceWM.ImportFromEPSG(int(EPSG_code_WM)) #here we define this reference to be the EPSG code
            driver = osgeo.ogr.GetDriverByName('ESRI Shapefile') # will select the driver for our shp-file creation.
            shapeDataWM = driver.CreateDataSource(StopsShapefilePathWM) #so there we will store our data
            layerWM = shapeDataWM.CreateLayer('layerWM', spatialReferenceWM, osgeo.ogr.wkbPoint) #this will create a corresponding layer for our data with given spatial information.
            layerWM_defn = layerWM.GetLayerDefn() # gets parameters of the current shapefile
            index = 0
			###print "two"
            fieldnames = []
            with open(text_file, 'r') as f:
                first_line = f.readline()
            fl = first_line.split(",")
            for fn in fl:
                fieldnames.append(fn)
            for f in fl:
                #print f
                if f == "stop_id":
                    c_stop_id = counter
                if f == "stop_name":
                    c_stop_name = counter
                if f == "stop_lat":
                    c_stop_lat = counter
                    print "c_stop_lat"
                    print c_stop_lat
                if f == "stop_lon":
                    c_stop_lon = counter
                new_field = ogr.FieldDefn(f, ogr.OFTString) #we will create a new field with the content of our header
                print "three"
                layer.CreateField(new_field)
                ##layerWM.CreateField(new_field)
                counter = counter + 1
            print "four"
            stop_layer = QgsVectorLayer(StopsShapefilePath, "stop_layer", "ogr")
            stop_layer.startEditing()
            #stop_layer = iface.addVectorLayer(StopsShapefilePath, "stop_layer", "ogr")
            if not stop_layer:
                print "Layer failed to load!"
            ##for line in text_file:
            with open(text_file, 'r') as f:
                lines = f.readlines()
                #print "len(line)"
                #print len(line)
                #l = str(line).split(",")
                #print line
                for line in lines:
                    #print line
                    l = str(line).split(",")
                    #print l[0]
                    #print "c_stop_lat, c_stop_lon"					
                    #print c_stop_lat, c_stop_lon
                    if l[c_stop_id] != "stop_id":
                        stop_id = l[c_stop_id]
                    if l[c_stop_name] != "stop_name":
                        stop_name = l[c_stop_name]
                    if l[c_stop_lat] != "stop_lat":
                        stop_lat = float(l[c_stop_lat])
                    if l[c_stop_lon] != "stop_lon":
                        stop_lon = float(l[c_stop_lon])
                        ##DICT_stop_lon [l[c_stop_id]] = l[c_stop_lon]
                    ##print(stop_lat, stop_lon)
                    if type(stop_lat) == float:
                        if type (stop_lon) == float:
                    	    print(stop_lat, stop_lon)
                    	    caps = stop_layer.dataProvider().capabilities()
                    	    caps_string = stop_layer.dataProvider().capabilitiesString()
                    	    print caps_string
                    	    # Check if a particular capability is supported:
                    	    ##caps & QgsVectorDataProvider.DeleteFeatures
                    	    # Print 2 if DeleteFeatures is supported
                    	    #caps = layer.dataProvider().capabilities()
                    	    if caps & QgsVectorDataProvider.AddFeatures:
                    	        feat = QgsFeature(stop_layer.pendingFields())
                    	        #feat.setAttributes([0, 'hello'])
                    	        #feat.setAttributes(['stop_id', str(stop_id)])
                    	        #feat.setAttributes([0, 'hello'])
                    	        # Or set a single attribute by key or by index:
                    	        #feat.setAttribute('stop_id', stop_id)
                    	        feat.setAttribute(2, 'hello')
                    	        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(stop_lon), float(stop_lat))))
                    	        (res, outFeats) = stop_layer.dataProvider().addFeatures([feat])
                    	        top_layer.commitChanges()
                            #point = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
                            ####point.AddPoint(float([stop_lon]), float([stop_lat])) #we do have LATs and LONs as Strings, so we convert them
                            #point.AddPoint(float(stop_lon), float(stop_lat)) #we do have LATs and LONs as Strings, so we convert them
                            #feature = osgeo.ogr.Feature(layer_defn)
                            #feature.SetGeometry(point) #set the coordinates
                    ##print(row['stop_lat'], row['stop_lon'])
                    #point = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
                    #point.AddPoint(float(row[stop_lon]), float(row[stop_lat])) #we do have LATs and LONs as Strings, so we convert them
                    #feature = osgeo.ogr.Feature(layer_defn)
                    #feature.SetGeometry(point) #set the coordinates
                    ##feature.SetFID(index)
                    ##for field in readerDict.fieldnames:
                    ##    i = feature.GetFieldIndex(field)
                    ##    feature.SetField(i, row[field])
                    ##    layer.CreateFeature(feature)
                    ##    index += 1
                    ##shapeData.Destroy() #lets close the shapefile
                #stop_layer.commitChanges()
					
					
				
            #pass
