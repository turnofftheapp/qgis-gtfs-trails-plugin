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
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
import osgeo.ogr, osgeo.osr #we will need some packages
from osgeo import ogr #and one more for the creation of a new field
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsVectorDataProvider, QgsFeature, QgsGeometry, QgsVectorFileWriter  
from qgis.core import QgsPoint, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsDataSourceURI, QgsRectangle
from PyQt4.QtCore import *
from qgis.analysis import *
from collections import defaultdict
import numpy

# Initialize Qt resources from file resources.py
##############import resources
# Import the code for the dialog
####################from TransitAccessibleTrailheads_dialog import FindTransitAccessibleTrailheadsDialog
import os.path, sys, datetime
import os
###import ogr2ogr

####class FindTransitAccessibleTrailheads:
    """QGIS Plugin Implementation."""

    # def __init__(self, iface):
        # """Constructor.

        # :param iface: An interface instance that will be passed to this class
            # which provides the hook by which you can manipulate the QGIS
            # application at run time.
        # :type iface: QgsInterface
        # """
        # # Save reference to the QGIS interface
        # self.iface = iface
        # # initialize plugin directory
        # self.plugin_dir = os.path.dirname(__file__)



def IdentifyTransitAccessibleTrailheads(GTFSDir, StopsFile, BufferDistance, working_dir, outputGeoJSON, in_format, host_name, port, database_name, uname, password, postGIS_table_name, PostGISExpr, shapefile_th, th_id_field, th_name_field):
	# """Run method that performs all the real work"""
	# # show the dialog
	# self.dlg.show()
	# # Run the dialog event loop
	# result = self.dlg.exec_()
	# GTFSDir = self.dlg.GTFSLocation.text()
	# StopsFile = self.dlg.StopsFile.text()
	# stopID = self.dlg.stopID.text()
	stopID = "stop_id"
	# ###StopsShapefileName = self.dlg.StopsShapefileName.text()
	StopsShapefileName = "stops"
	AddToMapCanvas = False
	trailBufferShpName = "trailBuff"
	# working_dir_name = self.dlg.working_dir.text()
	TrailheadData_shp = shapefile_th
	# ADDED TO STANDALONE
	#dir_path = os.getcwd()
	#dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
	###dir_path = os.path.dirname(os.path.realpath(__file__))
	#dir_path = os.path.realpath(__file__)
	dir_path =  sys.executable
	# BufferDistance = self.dlg.BufferDistance.text()
	# th_id_field = self.dlg.th_id_field.text()
	# th_name_field = self.dlg.th_name_field.text()
	# outputGeoJSON = self.dlg.outputGeoJSON.text()
	# PostGISExpr = self.dlg.tbPostGISExpr.text()		
	# AddToMapCanvas = self.dlg.cbAddToMapCanvas.isChecked() # returns True if checked
	# ###trailBufferShpName = self.dlg.trailBufferShpName.text()
	# #in_format.append("Shapefile")
	# #in_format.append("PostGIS")
	# #self.dlg.comboBox.addItems(in_format)		
	# #
	# ##shapefile_th = self.dlg.checkBoxShapefile.isChecked() # returns True if checked
	# ##postGIS_th = self.dlg.checkBoxPostGIS.isChecked()
	# #
	# shapefile_th = self.dlg.radioButtonShapefile.isChecked() # returns True if checked
	# postGIS_th = self.dlg.radioButtonPostGIS.isChecked()
	# #
	# host_name = self.dlg.host_name.text()
	# port = self.dlg.port.text()
	# database_name = self.dlg.database_name.text()
	# uname = self.dlg.uname.text()
	# password = self.dlg.password.text()
	# postGIS_table_name = self.dlg.postGIS_table_name.text()
	shapefile_th = False
	postGIS_th = False
	# #
	if in_format == "Shapefile":
		shapefile_th = True
	if in_format == "PostGIS":
		postGIS_th = True
	InputDataSpecified = False
	if shapefile_th:
		InputDataSpecified = True
	if postGIS_th:
		InputDataSpecified = True
	#postGIS_th = True
	#shapefile_th = True		
	working_dir = os.path.join(GTFSDir, working_dir)
	#if working_dir doesn't exist, create it
	if not os.path.exists(working_dir):
		os.makedirs(working_dir)   
	TATShp = os.path.join(working_dir, "TAToutput.shp")
	TATdShp = os.path.join(working_dir, "TATdoutput.shp")
	THShp = os.path.join(working_dir, "TH.shp")
	#
	DList_TrailsStops = defaultdict(list)
	#
	###  code same as TransitAccessibleTrailheads.py after this point 
	### 
	#####if result:
	if InputDataSpecified:
		start_time = datetime.datetime.now().replace(microsecond=0)
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
		crsSrc = QgsCoordinateReferenceSystem(4326)    # WGS 84
		crsDest = QgsCoordinateReferenceSystem(3857)  # WGS 84 / Web Mercator
		xform = QgsCoordinateTransform(crsSrc, crsDest)
		rev_xform = QgsCoordinateTransform(crsDest, crsSrc)
		##
		#StopsShapefilePath = os.path.join(GTFSDir, StopsShapefileName + ".shp")
		#StopsShapefileBufferPath = os.path.join(GTFSDir, StopsShapefileName + "BUFF.shp")
		#StopsShapefilePathWM = os.path.join(GTFSDir, StopsShapefileName + "WM.shp")
		StopsShapefilePath = os.path.join(working_dir, StopsShapefileName + ".shp")
		StopsShapefileBufferPath = os.path.join(working_dir, StopsShapefileName + "BUFF.shp")
		StopsShapefilePathWM = os.path.join(working_dir, StopsShapefileName + "WM.shp")
		##
		spatialReference = osgeo.osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be
		spatialReference.ImportFromEPSG(int(EPSG_code)) #here we define this reference to be the EPSG code
		driver = osgeo.ogr.GetDriverByName('ESRI Shapefile') # will select the driver for our shp-file creation.
		##
		index = 0
		spatialReferenceWM = osgeo.osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be			
		spatialReferenceWM.ImportFromEPSG(int(EPSG_code_WM)) #here we define this reference to be the EPSG code
		driver = osgeo.ogr.GetDriverByName('ESRI Shapefile') # will select the driver for our shp-file creation.
		# create layer
		#if shapefile_th_rb:
		#    print "USING Shapefiles!"
		#if postGIS_th_rb:
		#    print "USING PostGIS!"			
		##vl = QgsVectorLayer("Point", "stop_points", "memory")
		vl = QgsVectorLayer("Point?crs=EPSG:3857", "stop_points", "memory")
		##vl.spatialReference
		pr = vl.dataProvider()
		#
		# changes are only possible when editing the layer
		vl.startEditing()
		# add fields
		pr.addAttributes([QgsField("stop_id", QVariant.String),QgsField("stop_name", QVariant.Int),QgsField("stop_lat", QVariant.Double),QgsField("stop_lon", QVariant.Double)])
		index = 0
		###print "two"
		fieldnames = []
		stop_lat = 0
		stop_lon = 0
		c_stop_id = 0
		c_stop_name = 0
		c_stop_lat = 0
		c_stop_lon = 0
		with open(text_file, 'r') as f:
			first_line = f.readline()
		fl = first_line.split(",")
		counter = 0
		for f in fl:
			fieldnames.append(f)
			#for f in fl:
			#print f
			if f == "stop_id":
				c_stop_id = counter
			if f == "stop_name":
				c_stop_name = counter
			if f == "stop_lat":
				c_stop_lat = counter
				#print "stop_lat is in column ", c_stop_lat
				#print c_stop_lat
			if f == "stop_lon":
				c_stop_lon = counter
				#print "stop_lon is in column ", c_stop_lon
				##print c_stop_lon
				##print "three"
			counter = counter + 1
			#
		with open(text_file, 'r') as f:
			lines = f.readlines()
			for line in lines:
				h = '"'					
				if h in line:
					count = line.count(h)
					print "Removed quote from line" + str(count)
					while count > 0:
						#print [pos for pos, char in enumerate(line) if char == c]
						cc = [pos for pos, char in enumerate(line) if char == h]
						d = ','
						#print [pos for pos, char in enumerate(line) if char == d]
						dd = [pos for pos, char in enumerate(line) if char == d]
						startP = cc[0]
						endP = cc[1]
						for ddd in dd:
							if (ddd > startP) and (ddd < endP):
								extraCommaPos = ddd
								line1 = line[0:startP]  
								line2 = line[(startP + 1):extraCommaPos]
								line3 = line[(extraCommaPos + 1):(endP)]
								line4 = line[(endP + 1):-1]
								lineMod = line1 + line2 + line3 + line4
								#print line
								#print "Comma removed"
								#print lineMod
								line = lineMod
								count = line.count(h)
				l = str(line).split(",")
				if l[c_stop_id] != "stop_id":
					stop_id = l[c_stop_id]
				if l[c_stop_name] != "stop_name":
					stop_name = l[c_stop_name]
				if l[c_stop_lat] != "stop_lat":
					stop_lat = float(l[c_stop_lat])
				if l[c_stop_lon] != "stop_lon":
					stop_lon = float(l[c_stop_lon])
				if type(stop_lat) == float:
					if type (stop_lon) == float:
						fet = QgsFeature()
						stop_pt_WM = xform.transform(QgsPoint(stop_lon,stop_lat))
						###print "Transformed point:", stop_pt_WM
						#fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(stop_lon, stop_lat)))
						fet.setGeometry(QgsGeometry.fromPoint(stop_pt_WM))
						fet.setAttributes([stop_id, stop_name, stop_lat, stop_lon])
						pr.addFeatures([fet])
						vl.commitChanges()
		#
		# add layer to the legend
		stops_extent = vl.extent()
		xmin = stops_extent.xMinimum()			            
		ymin = stops_extent.yMinimum()
		xmax = stops_extent.xMaximum()
		ymax = stops_extent.yMaximum()
		##QgsMapLayerRegistry.instance().addMapLayer(vl)
		#
		# Add trailheads from postGIS if postGIS_th = True 			
		#
		if postGIS_th:
			uri = QgsDataSourceURI()
			# set host name, port, database name, username and password
			#uri.setConnection("localhost", "5432", "dbname", "johny", "xxx")
			uri.setConnection(host_name, port, database_name, uname, password)
			print "made PostGIS connection successfully"
			# set database schema, table name, geometry column and optionally
			# subset (WHERE clause)
			#uri.setDataSource("public", "roads", "the_geom", "cityid = 2643")
			#uri.setDataSource("public", postGIS_table_name, "geom", PostGISExpr)
			uri.setDataSource("public", postGIS_table_name, "geom", PostGISExpr)
			#
			#vlayer = QgsVectorLayer(uri.uri(), "layer name you like", "postgres")
			DB_TH_layer = QgsVectorLayer(uri.uri(), "DB_TH_layer", "postgres")
			QgsMapLayerRegistry.instance().addMapLayer(DB_TH_layer)
			#
			stop_extent = QgsVectorLayer("Polygon?crs=EPSG:4326", "stop_extent", "memory")
			pr = stop_extent.dataProvider()
			stop_extent.startEditing()
			#
			fet = QgsFeature()
			#fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(stop_lon, stop_lat)))
			#
			stop_ex_SW = rev_xform.transform(QgsPoint(xmin, ymin))
			stop_ex_NW = rev_xform.transform(QgsPoint(xmin, ymax))
			stop_ex_NE = rev_xform.transform(QgsPoint(xmax, ymax))
			stop_ex_SE = rev_xform.transform(QgsPoint(xmax, ymin))
			print "Stops layer extent (lower):", stop_ex_SW
			print "Stops layer extent (upper):", stop_ex_NE			
			##fet.setGeometry(QgsGeometry.fromPolygon([[QgsPoint(xmin,ymin),QgsPoint(xmin,ymax), QgsPoint(xmax,ymax), QgsPoint(xmax,ymin), QgsPoint(xmin,ymin)]]))
			fet.setGeometry(QgsGeometry.fromPolygon([[stop_ex_SW, stop_ex_NW, stop_ex_NE, stop_ex_SE, stop_ex_SW]]))
			pr.addFeatures([fet])
			stop_extent.commitChanges()				
			QgsMapLayerRegistry.instance().addMapLayer(stop_extent)
			#
			print "overlay points! - using extent from stops"
			overlayAnalyzer = QgsOverlayAnalyzer()
			overlayAnalyzer.intersection(DB_TH_layer, stop_extent, THShp)
			TH_layer = QgsVectorLayer(THShp, "TH_layer", "ogr")
			if not TH_layer.isValid():
				print "TH.shp layer failed to load!"	
			########## this adds trailheads to the map canvas ########QgsMapLayerRegistry.instance().addMapLayer(TH_layer)
			iter = TH_layer.getFeatures()
			#for feature in iter:
			#    geomIn = feature.geometry()
			#    #print geom.vectorType()
			#    featgeom = geomIn.exportToWkt()
			#    print featgeom
			#    geom = QgsGeometry.fromWkt(featgeom)
			#    #print geom2 #= QgsGeometry.fromWkt(featgeom)
			#    #if geom.isMultipart:
			#    #    print "multi"
			#    feature_name = feature['name']
			#    feature_id = feature['FEAT_ID']
			#    print "geom.asPoint()"
			#    print geom.asPoint()
			#
		# add trailhead layer from shapefile if selected (assumes it is stored in WGS 84)
		#
		if shapefile_th:
			trailhead_layer = QgsVectorLayer(TrailheadData_shp, "trailhead_layer", "ogr")
			######### this adds trailsheads to map canvas############QgsMapLayerRegistry.instance().addMapLayer(trailhead_layer)
			if not trailhead_layer.isValid():
				print "trailhead layer failed to load!"
		# 
		# create trailhead layer in Web Mercator
		#
		vltWM = QgsVectorLayer("Point?crs=EPSG:3857", "trailhead_points_WM", "memory")
		prtWM = vltWM.dataProvider()
		#
		# changes - including adding fields - are only possible when editing the layer
		vltWM.startEditing()
		prtWM.addAttributes([QgsField("name", QVariant.String),QgsField("FEAT_ID", QVariant.Int)])
		#
		#  Get the features from the trailhead layer that is loaded, from shp or db
		#  and convert to a WM dataset
		#
		if shapefile_th:
			iter = trailhead_layer.getFeatures()
			print "using shape"
			for feature in iter:
				geom = feature.geometry()
				feature_name = feature['name']
				feature_id = feature['FEAT_ID']
				th_x = geom.asPoint().x()	
				th_y = geom.asPoint().y()
				print th_x, th_y
				trailhead_pt_WM = xform.transform(QgsPoint(geom.asPoint()))
				fet = QgsFeature()
				fet.setGeometry(QgsGeometry.fromPoint(trailhead_pt_WM))
				fet.setAttributes([feature_name, feature_id])
				prtWM.addFeatures([fet])
				vltWM.commitChanges()
		if postGIS_th:
			trailhead_layer = QgsVectorLayer(THShp, "trailhead_layer", "ogr")
			iter = trailhead_layer.getFeatures()
			print "using postGIS"
			for feature in iter:
				geomIn = feature.geometry()
				featgeom = geomIn.exportToWkt()
				#featgeom = featgeom.replace("MultiPoint", "POINT")					
				#featgeom = featgeom.replace("((", "(")					
				#featgeom = featgeom.replace("))", ")")					
				#featgeom = '"' + str(featgeom) + '"'
				geoString1 = featgeom.split('((')
				geoString2 = geoString1[1].split('))')
				#geoString22 = geoString2[0]	
				geoString = geoString2[0].split(' ')
				ptX = float(geoString[0])					                    
				ptY = float(geoString[1])
				#ptX = geoString[0]					
				#ptY = geoString[1]
				#geomString = '"POINT (' + str(ptX) + " " + str(ptY) + ')"'
				geomString = '"POINT (' + str(ptX) + " " + str(ptY) + ')"'
				#print geomString	
				#geom = QgsGeometry.fromWkt(geomString)
				geom = QgsGeometry.fromPoint(QgsPoint(ptX, ptY))
				#geom = QgsGeometry.fromWkt("POINT (-122.24501049999997804 47.86390650000004143)")
				###geom = feature.geometry()
				###feature_name = feature['name']
				###feature_id = feature['FEAT_ID']
				feature_name = feature[th_name_field]
				feature_id = feature[th_id_field]
				trailhead_pt_WM = xform.transform(QgsPoint(geom.asPoint()))
				fet = QgsFeature()
				fet.setGeometry(QgsGeometry.fromPoint(trailhead_pt_WM))
				fet.setAttributes([feature_name, feature_id])
				prtWM.addFeatures([fet])
				vltWM.commitChanges()
				###fet = QgsFeature()
				#####feature.asPoint()
				####print feature
				###fet.setGeometry(QgsGeometry.fromPoint(trailhead_pt_WM))
				###fet.setAttributes([feature_name, feature_id])
				###prtWM.addFeatures([fet])
				###vltWM.commitChanges()
				###fet.setGeometry(QgsGeometry.fromPoint(trailhead_pt_WM))
				###fet.setGeometry(geom)
				###fet.setAttributes([feature_name, feature_id])
				####print "geom"
				####print geom
				###trailhead_pt_WM = xform.transform(QgsPoint(geom.asPoint()))
				###prtWM.addFeatures([fet])
				###vltWM.commitChanges()
		#	
		#	Add WM trailheads to the map canvas
		#
		#print "PostGISExpr"
		#print PostGISExpr
		#if PostGISExpr == "":
		#	print "NO EXPR!"
		if AddToMapCanvas:
			QgsMapLayerRegistry.instance().addMapLayer(vltWM)
		#	print "NO EXPR!"
		#QgsMapLayerRegistry.instance().addMapLayer(vltWM)
		#	Buffer stops
		vltb = QgsVectorLayer("Point?crs=EPSG:3857", "trailhead_buffer_dissolved", "memory")
		#
		#QgsGeometryAnalyzer().dissolve(vlt, vltb, onlySelectedFeatures=False, uniqueIdField=-1, p=None)
		#	Buffer stops
		geometryanalyzer = QgsGeometryAnalyzer()
		geometryanalyzer.buffer(vltWM, StopsShapefileBufferPath + ".shp", int(BufferDistance), False, False, -1)
		trailheadBuffer_layer = QgsVectorLayer(StopsShapefileBufferPath + ".shp", "trailhead_buffer_layer", "ogr")
		if AddToMapCanvas:
			QgsMapLayerRegistry.instance().addMapLayer(trailheadBuffer_layer)
		# 
		geometryanalyzer.buffer(vltWM, StopsShapefileBufferPath + "d.shp", int(BufferDistance), False, True, -1)
		#trailheadBufferd_layer = QgsVectorLayer(StopsShapefileBufferPath + "d.shp", "trailhead_buffer_d", "ogr")
		trailheadBufferd_layer = QgsVectorLayer(StopsShapefileBufferPath + "d.shp", "trailhead_buffer_d", "ogr")
		if AddToMapCanvas:
			QgsMapLayerRegistry.instance().addMapLayer(trailheadBufferd_layer)
		# 
		# overlay - using dissolved buffer
		# 
		print "overlay points! - using dissolved buffers"
		overlayAnalyzer = QgsOverlayAnalyzer()
		#overlayAnalyzer.intersection(vl, vlt, "C:/UWGIS/Geog569/Data/Test/TAToutput.shp")
		overlayAnalyzer.intersection(vl, trailheadBufferd_layer, TATdShp)
		TATd_layer = QgsVectorLayer(TATdShp, "TrAccTrailheads_diss_layer", "ogr")
		if not TATd_layer.isValid():
			print "TATd layer failed to load!"	
		if AddToMapCanvas:
			QgsMapLayerRegistry.instance().addMapLayer(TATd_layer)
		iter = TATd_layer.getFeatures()
		stopList = []
		for feature in iter:
			# retrieve every feature with its geometry and attributes
			feature_id = feature[stopID]
			stopList.append(feature_id)				
			#feature_id = feature['FEAT_ID']
		#for s in stopList:
		#	print s
		#
		# overlay - using the indivdual buffered points
		# this can be used to compute distance between trailhaeds and each stop in its buffer
		#				
		print "overlay points! - using dissolved buffers"
		overlayAnalyzer = QgsOverlayAnalyzer()
		#overlayAnalyzer.intersection(vl, vlt, "C:/UWGIS/Geog569/Data/Test/TAToutput.shp")
		overlayAnalyzer.intersection(vl, trailheadBuffer_layer, TATShp)
		TAT_layer = QgsVectorLayer(TATShp, "TrAccTrailheads_layer", "ogr")
		if not TAT_layer.isValid():
			print "TAT layer failed to load!"	
		if AddToMapCanvas:
			QgsMapLayerRegistry.instance().addMapLayer(TAT_layer)
		iter = TAT_layer.getFeatures()
		THstopList = []
		for feature in iter:
			# retrieve every feature with its geometry and attributes
			# fetch geometry
			#geom = feature.geometry()
			###print "Feature ID %d: " % feature.id()
			###print geom.type()
			###trailhead_name = feature['name']
			###trailhead_id = feature['FEAT_ID']				
			###trailhead_name = feature['name']
			trailhead_id = feature[th_id_field]				
			#####feature_id = feature[th_name_field]
			####feature_id = "u" + str(feature_id)th_id_field
			##feature_id = feature['FEAT_ID']
			feature_id = feature[th_id_field]
			TH_Stop = str(trailhead_id) + ":" +  str(feature_id)				
			#print feature['stop_id']
			THstopList.append(TH_Stop)
			DList_TrailsStops[trailhead_id].append(feature_id)
			#feature_id = feature['FEAT_ID']
		#for s in THstopList:
		#	print s
		#for s in DList_TrailsStops:
		#	print s, DList_TrailsStops[s]
		#	#print DList_TrailsStops[s]
		print xmin, ymin, xmax, ymax
		fet = QgsFeature()
		stop_pt_WM = rev_xform.transform(QgsPoint(xmin, ymin))
		print "Stops layer extent (lower):", stop_pt_WM
		#fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(stop_lon, stop_lat)))
		stop_pt_WM = rev_xform.transform(QgsPoint(xmax, ymax))
		print "Stops layer extent (upper):", stop_pt_WM
		###print self.plugin_dir
		sys.argv = [GTFSDir, stopList]
		missing_files = []
		all_files_present = True
		fn_stop_times = "stop_times.txt"
		f_stop_times = os.path.join(GTFSDir, fn_stop_times)
		if not os.path.exists(f_stop_times):
			all_files_present = False   
			missing_files.append(fn_stop_times)   
		fn_stops = "stops.txt"
		f_stops = os.path.join(GTFSDir, fn_stops)
		if not os.path.exists(f_stops):
			all_files_present = False   
			missing_files.append(fn_stops)   
		fn_trips = "trips.txt"
		f_trips = os.path.join(GTFSDir, fn_trips)
		if not os.path.exists(f_trips):
			all_files_present = False   
			missing_files.append(fn_trips)   
		fn_routes = "routes.txt"
		f_routes = os.path.join(GTFSDir, fn_routes)
		if not os.path.exists(f_routes):
			all_files_present = False   
			missing_files.append(fn_routes)   
		fn_agency = "agency.txt"
		f_agency = os.path.join(GTFSDir, fn_agency)
		if not os.path.exists(f_agency):
			all_files_present = False   
			missing_files.append(fn_agency)   
		#if working_dir doesn't exist, create it
		###if os.path.exists(f_stop_times):			
		if all_files_present:
			print "starting service analysis...this might take some time"   
			##SummarizeTransitService = os.path.join(self.plugin_dir, "SummarizeTransitService.py")
			SummarizeTransitService = os.path.join(dir_path, "SummarizeTransitService.py")
			##SummarizeTransitService =  "SummarizeTransitService.py"
			execfile(SummarizeTransitService)
		else:
			print "The GTFS appears to be incomplete.  The following files seem to be missing."   				
			#print "The GTFS appears to be incomplete.  Check that all parts are present and try again."   				
			for f in missing_files:
				print f
			##create empty dictionary
		##  BEGIN DISTANCE CODE!
		distance_dictionary = {}
		DList_TH_stops = defaultdict(list)
		### (temporarily) set ref to TAT in case
		##Enter data into Dictionary
		iter = vltWM.getFeatures()
		#iter = TAToutput.getFeatures()
		##THstopList = []
		for feature in iter:
			##identifies attributes for future use
			#print "Feature ID %d: " % feature.id()
			trailhead_id = feature[str('FEAT_ID')]
			geom = feature.geometry()
			th_x = geom.asPoint().x()	
			th_y = geom.asPoint().y()
			th_point = QgsPoint(th_x,th_y)
			#transit_stop_id = feature['stop_id']
			### replace this line with something that selects features from TAToutput that have the same trailhead id here...
			iter_stops = TAT_layer.getFeatures() ###[new layer here?]
			for stop_feature in iter_stops:
			##identifies attributes for future use
				#print "Feature ID %d: " % feature.id()
				stop_id = stop_feature[str('stop_id')]
				th_id = stop_feature[str('FEAT_ID')]
				if th_id == trailhead_id:
					stop_geom = stop_feature.geometry()
					stop_id = stop_feature['stop_id']
					DList_TH_stops[th_id].append(stop_id)
					###print trailhead_id, stop_id
					stop_x = stop_geom.asPoint().x()	
					stop_y = stop_geom.asPoint().y()
					#print stop_x, stop_y
					### I think  we are using Web Mercator points, so the line below is all that is needed here..but (see below) 
					s_point = QgsPoint(stop_x,stop_y)
					### if the points were lat / lon, we would transform them and use the line below (and commenting out the line above!):
					###s_point = xform.transform(QgsPoint(stop_lon,stop_lat))
					### replace this line with something that figures out Euclidian dist
					stop_distance = 0
					#def dist(x,y):
					#         return numpy.sqrt(numpy.sum(x-y)**2)
					a = numpy.array(th_point)
					b = numpy.array(s_point)
					#stop_distance = dist(a,b)
					stop_distance = numpy.sqrt(numpy.sum(a-b)**2)
					# stop_distance = th_point (distance from) s_point
					th_stop = str(trailhead_id) + ":" + str(stop_id)
					#print th_stop
					distance_dictionary[th_stop] = stop_distance 		
		## below is a placeholder for the distance calculations!
		###print distance_dictionary
		#pass
		##outputGeoJSON
		vl_outTH = QgsVectorLayer("Point?crs=EPSG:4326", "stop_points", "memory")
		##vl.spatialReference
		pr_outTH = vl_outTH.dataProvider()
		#
		# changes are only possible when editing the layer
		vl_outTH.startEditing()
		# add fields
		##pr_outTH.addAttributes([QgsField(th_id_field, QVariant.Int),QgsField(th_name_field, QVariant.String),QgsField("number_stops_nearby", QVariant.Int),QgsField("stops_near", QVariant.String),QgsField("stops_near_dist", QVariant.String)])
		pr_outTH.addAttributes([QgsField(th_id_field, QVariant.Int),QgsField(th_name_field, QVariant.String),QgsField("number_stops_nearby", QVariant.Int),QgsField("stops_near", QVariant.String)])
		index = 0
		iter = trailhead_layer.getFeatures()
		for feature in iter:
			geom = feature.geometry()
			feature_id = feature[th_id_field]
			feature_name = feature[th_name_field]
			#stops_near = str(DList_TH_stops[feature_id])
			num_stops_near = 0
			stops_near_in = DList_TH_stops[feature_id]
			stops_near = []
			for t in stops_near_in:
				#print t
				if not t in stops_near:
					stops_near.append(t)					
			stops_near.sort() 
			num_stops_near = len(stops_near)
			stops_near = str(stops_near)
			stops_near = stops_near.replace("u'", "")
			stops_near = stops_near.replace("'", "")
			stops_near = stops_near.replace("[", "")
			stops_near = stops_near.replace("]", "")
			#print stops_near
			dist_list = []
			stops_near_L = DList_TH_stops[feature_id]
			stops_near_L.sort()
			for s in stops_near_L:
				#print s
				k = str(feature_id) + ":" + str(s)
				dist = distance_dictionary[k]
				dist = int(dist)
				dist_list_data = '{stop_id: ' + str(s) + ', distance ' + str(dist) + '}'
				if not dist_list_data in dist_list:
					dist_list.append(dist_list_data)					
			#dist_list.sort() 
			#trailhead_pt_WM = xform.transform(QgsPoint(geom.asPoint()))
			#print "dist_list"
			#print dist_list
			#dist_list = dist_list.replace("u'", "")
			#dist_list = dist_list.replace("'", "")
			dist_list = str(dist_list)
			dist_list = dist_list.replace("[", "")
			dist_list = dist_list.replace("]", "")
			dist_list = dist_list.replace("'", "")
			fet = QgsFeature()
			fet.setGeometry(geom)
			#fet.setGeometry(QgsGeometry.fromPoint(geom))
			#fet.setAttributes([feature_id, feature_name, num_stops_near, stops_near, dist_list])
			fet.setAttributes([feature_id, feature_name, num_stops_near, dist_list])
			pr_outTH.addFeatures([fet])
			vl_outTH.commitChanges()
		GeoJSONfile = os.path.join(GTFSDir, outputGeoJSON)
		writeString = ""
		QgsVectorFileWriter.writeAsVectorFormat(vl_outTH, GeoJSONfile, "utf-8", None, "GeoJSON")
		#file = open(GeoJSONfile, "w")
		##file.write(fieldnames + "\n")
		#iter = vltWM.getFeatures()
		#for feature in iter:
		#	##identifies attributes for future use
		#	#print "Feature ID %d: " % feature.id()
		#	trailhead_id = feature[str('FEAT_ID')]
		#	#trailhead_id = feature['FEAT_ID']
		#	geom = feature.geometry()
		#    th_x = geom.asPoint().x()	
		#    th_y = geom.asPoint().y()
		#    writeLine = ''
		#    writeLine = '{ "type": "Feature", "properties": { "FEAT_ID": ' + str(trailhead_id) # + '\n'
		#    #writeLine = writeLine  + ' "STOPS_NEARBY": ' + str(DList_TH_stops[trailhead_id])  ###'\n'
		#    writeLine = writeLine  + ' "STOPS_NEARBY": ' + DList_TH_stops[trailhead_id]  ###'\n'
		#    writeLine = writeLine  + '				}, "geometry": { "type": "Point", "coordinates": [ '
		#    writeLine = writeLine  + str(th_x) + ' ' + str(th_x) + ' ] } }'
		#    writeLine = writeLine  + ', \n'
		#    writeString = writeString + writeLine 
		#file.write(writeString)
		#file.close()
		end_time = datetime.datetime.now().replace(microsecond=0)
		print(end_time-start_time)
		print "done"
	else:
		print "Input trailhead data was not specified"

process_file = "C:\UWGIS\Geog569\Notes\ProcessTrailheads.csv"

GTFSDir = "none"
StopsFile = "none"
BufferDistance_meters = 400
working_dir = "none"
outputGeoJSON = "none"
in_format = "none"
host_name = "none"
port = "none"
database_name = "none"
PostGIS_uname = "none"
password = "none"
postGIS_table_name = "none"
PostGISExpr = "none"
shapefile_th = "none"
th_id_field = "none"
th_name_field =  "none"

c_GTFSDir = 0
c_StopsFile = 0
c_BufferDistance_meters = 0
c_working_dir = 0
c_outputGeoJSON = 0
c_in_format = 0
c_host_name = 0
c_port = 0
c_database_name = 0
c_PostGIS_uname = 0
c_password = 0
c_postGIS_table_name = 0
c_PostGISExpr = 0
c_shapefile_th = 0
c_th_id_field = 0
c_th_name_field = 0

##text_file = open(process_file, 'r')

text_file = open(process_file, 'r')
for line in text_file:
    fl = line.split(",")
    counter = 0
    for f in fl:
        if f == "GTFSDir":
            c_GTFSDir = counter
        if f == "StopsFile":
            c_StopsFile = counter
        if f == "BufferDistance_meters":
            c_BufferDistance_meters = counter
        if f == "working_dir":
            c_working_dir = counter
        if f == "outputGeoJSON":
            c_outputGeoJSON = counter
        if f == "in_format":
            c_in_format = counter
        if f == "PostGIS_hostname":
            c_host_name = counter
        if f == "port":
            c_port = counter
        if f == "database_name":
            c_database_name = counter
        if f == "PostGIS_uname":
            c_PostGIS_uname = counter
        if f == "PostGIS_password":
            c_password = counter
        if f == "postGIS_table_name":
            c_postGIS_table_name = counter
        if f == "PostGISExpr":
            c_PostGISExpr = counter
        if f == "shapefile_th":
            c_shapefile_th = counter
        if f == "th_id_field":
            c_th_id_field = counter
        if f == "th_name_field" or "th_name_field" in f:
            c_th_name_field = counter
        counter = counter + 1


# print c_GTFSDir
# print c_StopsFile
# print c_BufferDistance_meters
# print c_working_dir
# print c_outputGeoJSON
# print c_in_format
# print c_PostGIS_hostname
# print c_port
# print c_database_name
# print c_PostGIS_uname
# print c_PostGIS_password
# print c_postGIS_table_name
# print c_PostGISExpr
# print c_shapefile_th
# print c_th_id_field
# print c_th_name_field		
	
	
text_file = open(process_file, 'r')

counter = 0
for line in text_file:
	f = line.split(",")
	if counter > 0:
		#l = line.split(",")
		GTFSDir = f[c_GTFSDir]
		StopsFile = f[c_StopsFile]
		BufferDistance_meters = f[c_BufferDistance_meters]
		working_dir = f[c_working_dir]
		outputGeoJSON = f[c_outputGeoJSON]
		in_format = f[c_in_format]
		host_name = f[c_host_name]
		port =  f[c_port]
		database_name = f[c_database_name]
		PostGIS_uname =  f[c_PostGIS_uname]
		password =  f[c_password]
		postGIS_table_name =  f[c_postGIS_table_name]
		PostGISExpr = f[c_PostGISExpr]
		shapefile_th = f[c_shapefile_th]
		th_id_field = f[c_th_id_field]
		th_name_field = f[c_th_name_field]
		print GTFSDir
		print StopsFile
		print BufferDistance_meters
		print working_dir
		print outputGeoJSON
		print in_format
		print host_name
		print port
		print database_name
		print PostGIS_uname
		print password
		print postGIS_table_name
		print PostGISExpr
		print shapefile_th
		print th_id_field
		print th_name_field
		IdentifyTransitAccessibleTrailheads(GTFSDir, StopsFile, BufferDistance_meters, working_dir, outputGeoJSON, in_format, host_name, port, database_name, PostGIS_uname, password, postGIS_table_name, PostGISExpr, shapefile_th, th_id_field, th_name_field)
	counter = counter + 1


	
##GTFSDir = self.dlg.GTFSLocation.text()
##StopsFile = self.dlg.StopsFile.text()
##stopID = self.dlg.stopID.text()
###StopsShapefileName = self.dlg.StopsShapefileName.text()
#StopsShapefileName = "stops"
#AddToMapCanvas = False
###TrailheadData_shp = self.dlg.TrailheadData.text()
### BufferDistance = self.dlg.BufferDistance.text()
### th_id_field = self.dlg.th_id_field.text()
### th_name_field = self.dlg.th_name_field.text()
### outputGeoJSON = self.dlg.outputGeoJSON.text()
### PostGISExpr = self.dlg.tbPostGISExpr.text()		
### AddToMapCanvas = self.dlg.cbAddToMapCanvas.isChecked() # returns True if checked
### ###trailBufferShpName = self.dlg.trailBufferShpName.text()
### #in_format = []
### #in_format.append("Shapefile")
### #in_format.append("PostGIS")
####self.dlg.comboBox.addItems(in_format)		
### trailBufferShpName = "trailBuff"
### working_dir_name = self.dlg.working_dir.text()
##
###shapefile_th = self.dlg.checkBoxShapefile.isChecked() # returns True if checked
###postGIS_th = self.dlg.checkBoxPostGIS.isChecked()
##
#shapefile_th = self.dlg.radioButtonShapefile.isChecked() # returns True if checked
#postGIS_th = self.dlg.radioButtonPostGIS.isChecked()
##
#host_name = self.dlg.host_name.text()
#port = self.dlg.port.text()
#database_name = self.dlg.database_name.text()
#uname = self.dlg.uname.text()
#password = self.dlg.password.text()
#postGIS_table_name = self.dlg.postGIS_table_name.text()
		
		
###def run(self):
