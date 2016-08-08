import os, sys, datetime, csv
from collections import defaultdict

script_args = str(sys.argv)
num_args = len(sys.argv)

gtfs_path = sys.argv[0]
id_stops_lst = sys.argv[1]


## a = datetime.datetime.now()
# ...wait a while...
##b = datetime.datetime.now()
## print(b-a)

##If you don't want to display the microseconds, just use (as gnibbler suggested):

###def FindTransitServiceAtStops( gtfs_path, *stop_list ):



##def FindTransitServiceAtStops( gtfs_path, stop_list ):
#"This prints a passed string into this function"
#print GTFSDirectory
#for s in StopList:
#    print s
#
#start_time = datetime.datetime.now().replace(microsecond=0)

#print "Starting analysis"
print "Starting analysis"

##############################
### File references
##############################

agency_file = "agency.txt"
stops_file = "stops.txt"
calendar_file = "calendar.txt"
calendar_dates_file = "calendar_dates.txt"
stop_times_file = "stop_times.txt"
trips_file = "trips.txt"
routes_file = "routes.txt"

fn_stops = os.path.join(gtfs_path, stops_file)
fn_cal = os.path.join(gtfs_path, calendar_file)
fn_calendar_dates = os.path.join(gtfs_path, calendar_dates_file)
fn_stop_times = os.path.join(gtfs_path, stop_times_file)
fn_trips = os.path.join(gtfs_path, trips_file)
fn_routes = os.path.join(gtfs_path, routes_file)
fn_agency = os.path.join(gtfs_path, agency_file)

id_stops_lst.sort()
id_stops = [str(i) for i in id_stops_lst]

##############################
### identify single service hours
##############################

## Times use 24 hr clock

AM = "10"
PM = "16"

##############################
### identify service blocks
##############################

## Times use 24 hr clock
## The end time hour that is specified is INCLUDED in the block.

AM_start = 7
AM_end = 9
PM_start = 16
PM_end = 18

AM_block = []
PM_block = []

AM_block_hours = 0
PM_block_hours = 0

for h in range(AM_start,AM_end + 1):
	if h < 10:
		hstr = str("0" ) + str(h)
		AM_block.append(hstr)
	else:
		hstr = str(h)
		AM_block.append(hstr)
	AM_block_hours = AM_block_hours + 1 


for h in range(PM_start,PM_end + 1):
	if h < 10:
		hstr = str("0" ) + str(h)
		PM_block.append(hstr)
	else:
		hstr = str(h)
		PM_block.append(hstr)
	PM_block_hours = PM_block_hours + 1     


##############################
### create project dictionaries
##############################

## create list for file warnings
warnings = []

servedByD = {}
servedByTripD = {}
AMDeparturesD = {}
PMDeparturesD = {}
routeD = {}
serviceD = {}
directionD = {}
headsignD = {}

DICT_servedBy = {}
DICT_servedByTrip = {}
DICT_AMDepartures = {}
DICT_PMDepartures = {}
DICT_route = {}
DICT_service = {}
DICT_direction = {}
DICT_headsign = {}
DICT_routeShortName = {}
DICT_routeLongName = {}
DICT_routeAgencyID = {}
DICT_AgencyName = {}

###########data_dict = defaultdict(list)

## routes serving transit stop
DList_servedBy = defaultdict(list)
## routes serving transit stop with agenc ids
DList_servedByAgency = defaultdict(list)
## Agencies in the feed
DList_Agency = defaultdict(list)
## Agencies at each stop
DList_AgencyAtStop = defaultdict(list)
## Agencies Name at each stop
DList_AgencyNameAtStop = defaultdict(list)
## trips serving transit stop with agenc ids
DList_servedByTrip = defaultdict(list)
## departures during hour specified in variable AM for weekday service
DList_AMDepartures_WD = defaultdict(list)
## departures during hour specified in variable PM for weekday service
DList_PMDepartures_WD = defaultdict(list)
## departures during hour specified in variable AM for Saturday service
DList_AMDepartures_SA = defaultdict(list)
## departures during hour specified in variable PM for Saturday service
DList_PMDepartures_SA = defaultdict(list)
## departures during hour specified in variable AM for Sunday service
DList_AMDepartures_SU = defaultdict(list)
## departures during hour specified in variable PM for Sunday service
DList_PMDepartures_SU = defaultdict(list)
## route code (not necessarily a generally recognized number)
DList_route = defaultdict(list)
## service ids, used to identify weekday, Saturday and Sunday service
DList_service = defaultdict(list)
## inbound or outbound
DList_direction = defaultdict(list)
## transit route headsign eg, 'Avondale Road via Redmond'
DList_headsign = defaultdict(list)

## Total daily departures weekday service
DList_AllDepartures_WD = defaultdict(list)
## Total daily departures Saturday service
DList_AllDepartures_SA = defaultdict(list)
## Total daily departures Sunday service
DList_AllDepartures_SU = defaultdict(list)

### Departure block lists

## departures during block specified in variable AM_start and AM_end for weekday service
DList_AMDeparturesBLK_WD = defaultdict(list)
## departures during block specified in variable PM_start and PM_end for weekday service
DList_PMDeparturesBLK_WD = defaultdict(list)
## departures during block specified in variable AM_start and AM_end for weekday service
DList_AMDeparturesBLK_SA = defaultdict(list)
## departures during block specified in variable PM_start and PM_end for weekday service
DList_PMDeparturesBLK_SA = defaultdict(list)
## departures during block specified in variable AM_start and AM_end for weekday service
DList_AMDeparturesBLK_SU = defaultdict(list)
## departures during block specified in variable PM_start and PM_end for weekday service
DList_PMDeparturesBLK_SU = defaultdict(list)

### Stops lists

## transit stop name
DICT_stop_name = {}
## transit stop lat
DICT_stop_lat = {}
## transit stop lon
DICT_stop_lon = {}
## stop zone
DICT_zone_id = {}

##import os.path
##if os.path.isfile(fName):
##    print "The in-file exists!"
##else:
##    print "This file was not found"
##

##############################
### Header row, agency file
##############################

'''
Why is the program doing looking for the field names programatically?
Because, the field order might be different in different extracts.  Some fields are optional
which might impact the order they appear.  Finding these programatcially will help
identify the correct data points.

'''

##agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone

with open(fn_agency, 'r') as f:
	first_line = f.readline()
###print first_line
fl = first_line.split(",")

#### find the position of W, Sa, Su

agency_id = "UNK"
agency_name = "UNK"
agency_url = "UNK"
agency_timezone = "UNK"
agency_lang = "UNK"
agency_phone = "UNK"
fare_url = "UNK"
publishing_agency_name = "UNK"
publishing_agency_fareURL = "UNK"

agency_id_used = False
fare_url_used = False

c_agency_id = 0
c_agency_name = 0
c_agency_url = 0
c_agency_timezone = 0
c_agency_lang = 0
c_agency_phone = 0
c_fare_url = 0

counter = 0

for f in fl:
		#print f
		if f == "agency_id":
				c_agency_id = counter
				agency_id_used = True
		if f == "agency_name":
				c_agency_name = counter
		if f == "agency_url":
				c_agency_url = counter
		if f == "agency_timezone":
				c_agency_timezone = counter
		if f == "agency_lang":
				c_agency_lang = counter
		if f == "agency_phone" or "agency_phone" in f:
				c_agency_phone = counter
		if f == "fare_url" or "fare_url" in f:
				c_fare_url = counter
				publishing_agency_fareURL = True
		counter = counter + 1

#### find the agency id info

counter = 0
text_file = open(fn_agency, 'r')
for line in text_file:
		line_val = line.split(",")
		#print line
		if agency_id_used:
			agency_id = line_val[c_agency_id]
			if line_val[c_agency_id] != "agency_id":
				if counter == 1:
					agency_id = str(line_val[c_agency_id])
		if line_val[c_agency_name] != "agency_name":
			if agency_id_used:
				DICT_AgencyName[agency_id] = line_val[c_agency_name]
			if counter == 1:
				agency_name = str(line_val[c_agency_name])
				publishing_agency_name = str(line_val[c_agency_name])
		if line_val[c_agency_url] != "agency_url":
			if counter == 1:
				agency_url = str(line_val[c_agency_url])
		if line_val[c_agency_timezone] != "agency_timezone":
			if counter == 1:
				agency_timezone = str(line_val[c_agency_timezone])
		if line_val[c_agency_lang] != "agency_lang":
			if counter == 1:
				agency_lang = str(line_val[c_agency_lang])
		if line_val[c_agency_phone] != "agency_phone":
				agency_phone = str(line_val[c_agency_phone])
		if fare_url_used:
			fare_url = line_val[c_fare_url]
			if line_val[c_fare_url] != "fare_url":
				if counter == 1:
					publishing_agency_fareURL = str(line_val[c_fare_url])
		#if agency_id != "UNK":
		#        break
		counter = counter + 1

if counter > 1:
	add_agency = counter - 1
	#agency_id = agency_id + str(" plus ") + str(add_agency) + " more"
	#add_agency = counter - 1
	#agency_name = agency_name + str(" plus ") + str(add_agency) + " more"
	#agency_url = agency_url + str(" plus ") + str(add_agency) + " more"
	agency_name = agency_name
	agency_url = agency_url

print "Agency information collected"


for d in DICT_AgencyName:
		print d

##############################
### Header row, stops file
##############################

'''
Why is the program doing looking for the field names programatically?

See Agency section for explanation.

'''

##stop_id,stop_name,stop_lat,stop_lon,zone_id,stop_time

with open(fn_stops, 'r') as f:
	first_line = f.readline()
###print first_line
fl = first_line.split(",")

#### find the position of W, Sa, Su

zone_id_used = False

stop_id = "UNK"
stop_name = "UNK"
stop_lat = "UNK"
stop_lon = "UNK"
zone_id = "UNK"

c_stop_id = 0
c_stop_name = 0
c_stop_lat = 0
c_stop_lon = 0
c_zone_id = 0

counter = 0

for f in fl:
		#print f
		if f == "stop_id":
			c_stop_id = counter
		if f == "stop_name":
			c_stop_name = counter
		if f == "stop_lat":
			c_stop_lat = counter
		if f == "stop_lon":
			c_stop_lon = counter
		if f == "zone_id":
			c_zone_id = counter
			zone_id_used = True
		#if f == "agency_phone" or "agency_phone" in f:
		#        c_agency_phone = counter
		counter = counter + 1

#### find the stop info

text_file = open(fn_stops, 'r')
for line in text_file:
	h = '"'				
	if h in line:
		print "There is a quote in the line"
		count = line.count(h)
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
					print line
					print "lineMod"
					print lineMod
					line = lineMod
				count = line.count(h)
	#print "line"
	#print line
	l = line.split(",")
	#print "l"
	#print l
	if l[c_stop_id] != "stop_id":
		if l[c_stop_name] != "stop_name":
			DICT_stop_name [l[c_stop_id]] = l[c_stop_name]
		if l[c_stop_lat] != "stop_lat":
			DICT_stop_lat [l[c_stop_id]] = l[c_stop_lat]
		if l[c_stop_lon] != "stop_lon":
			DICT_stop_lon [l[c_stop_id]] = l[c_stop_lon]
		if zone_id_used:
			if l[c_zone_id] != "zone_id":
				DICT_zone_id [l[c_stop_id]] = l[c_zone_id]

print "Stop information collected"

##############################
### Header row, calendar file
##############################

'''
the code uses Wednesday as a proxy to identify weekday service

'''
if os.path.exists(fn_cal):
	print "calendar.txt exists."

	single_service_id = True

	with open(fn_cal, 'r') as f:
		first_line = f.readline()
	#print first_line
	fl = first_line.split(",")

	#### find the position of W, Sa, Su

	c_service_id = 0
	c_wed = 0
	c_sat = 0
	c_sun = 0
	c_startD = 0
	c_endD = 0
	counter = 0

	cal_list = []
	cal_list_wed = []
	cal_list_sat = []
	cal_list_sun = []

	max_WD_serv_length = 0
	max_SA_serv_length = 0
	max_SU_serv_length = 0

	servID_list_wed = []
	servID_list_sat = []
	servID_list_sun = []

	### Departure block lists

	## departures during block specified in variable AM_start and AM_end for weekday service
	DList_WD = defaultdict(list)
	DList_SA = defaultdict(list)
	DList_SU = defaultdict(list)

	List_WD = []
	List_SA = []
	List_SU = []

	## departures during block specified in variable PM_start and PM_end for weekday service

	for f in fl:
			#print f
			if f == "service_id":
					c_service_id = counter
			if f == "wednesday" or f == "Wednesday":
					c_wed = counter
			if f == "saturday" or f == "Saturday":
					c_sat = counter
			if f == "sunday" or f == "Sunday":
					c_sun = counter
			if f == "start_date":
					c_startD = counter
			if f == "end_date" or "end_date" in f:
					c_endD = counter
			counter = counter + 1

	#### find the service id of W, Sa, Su

	WD_servID = "UNK"
	SA_servID = "UNK"
	SU_servID = "UNK"

	##        DailyDepWD = len(DList_AllDepartures_WD)
	
	ref_start_date = "21000101"
	ref_end_date = "20000101"

	ref_start_yr = ref_start_date[0:4]
	ref_start_mo = ref_start_date[4:6]
	ref_start_day =  ref_start_date[6:8]
	#
	ref_end_yr = ref_end_date[0:4]
	ref_end_mo = ref_end_date[4:6]
	ref_end_day = ref_end_date[6:8]

	###

	GTFS_WD_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
	GTFS_WD_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))

	GTFS_SA_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
	GTFS_SA_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))

	GTFS_SU_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
	GTFS_SU_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))

	T_GTFS_WD_start_date = "UNK"
	T_GTFS_WD_end_date = "UNK"

	T_GTFS_SA_start_date = "UNK"
	T_GTFS_SA_end_date = "UNK"

	T_GTFS_SU_start_date = "UNK"
	T_GTFS_SU_end_date = "UNK"

	text_file = open(fn_cal, 'r')
	for line in text_file:
		line_val = line.split(",")
		#if len(List_WD) > 1:
		#    single_service_id = False
		if line_val[c_wed] == 1 or line_val[c_wed] == "1":
			WD_start_date_str = str(line_val[c_startD])
			WD_end_date_str = str(line_val[c_endD])
			start_yr = WD_start_date_str[0:4]
			start_mo = WD_start_date_str[4:6]
			start_day =  WD_start_date_str[6:8]
			#
			end_yr = WD_end_date_str[0:4]
			end_mo = WD_end_date_str[4:6]
			end_day =  WD_end_date_str[6:8]
			#
			WD_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
			WD_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
			WD_serv_len = abs((WD_end_date - WD_start_date).days)
			if WD_start_date < GTFS_WD_start_date:
				GTFS_WD_start_date = WD_start_date
				T_GTFS_WD_start_date = str(line_val[c_startD])
			if WD_end_date > GTFS_WD_end_date:
				GTFS_WD_end_date = WD_end_date
				T_GTFS_WD_end_date = str(line_val[c_endD])
		#if len(List_SA) > 1:
		#    single_service_id = False
		if line_val[c_sat] == 1 or line_val[c_sat] == "1":
			SA_start_date_str = str(line_val[c_startD])
			SA_end_date_str = str(line_val[c_endD])
			start_yr = SA_start_date_str[0:4]
			start_mo = SA_start_date_str[4:6]
			start_day =  SA_start_date_str[6:8]
			#
			end_yr = SA_end_date_str[0:4]
			end_mo = SA_end_date_str[4:6]
			end_day =  SA_end_date_str[6:8]
			#
			SA_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
			SA_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
			SA_serv_len = abs((SA_end_date - SA_start_date).days)
			if SA_start_date < GTFS_SA_start_date:
				GTFS_SA_start_date = SA_start_date
				T_GTFS_SA_start_date = str(line_val[c_startD])
			if SA_end_date > GTFS_SA_end_date:
				GTFS_SA_end_date = SA_end_date         
				T_GTFS_SA_end_date = str(line_val[c_endD])                         
		#if len(List_SU) > 1:
		#    single_service_id = False
		if line_val[c_sun] == 1 or line_val[c_sun] == "1":
			SU_start_date_str = str(line_val[c_startD])
			SU_end_date_str = str(line_val[c_endD])
			start_yr = SU_start_date_str[0:4]
			start_mo = SU_start_date_str[4:6]
			start_day = SU_start_date_str[6:8]
			#
			end_yr = SU_end_date_str[0:4]
			end_mo = SU_end_date_str[4:6]
			end_day = SU_end_date_str[6:8]
			#
			SU_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
			SU_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
			SU_serv_len = abs((SU_end_date - SU_start_date).days)
			if SU_start_date < GTFS_SU_start_date:
				GTFS_SU_start_date = SU_start_date
				T_GTFS_SU_start_date = str(line_val[c_startD])
			if SU_end_date > GTFS_SU_end_date:
				GTFS_SU_end_date = SU_end_date                           
				T_GTFS_SU_end_date = str(line_val[c_endD])                            


	##max(list1)

	WD_serv_len = abs((GTFS_WD_end_date - GTFS_WD_start_date).days)
	SA_serv_len = abs((GTFS_SA_end_date - GTFS_SA_start_date).days)
	SU_serv_len = abs((GTFS_SU_end_date - GTFS_SU_start_date).days)

	WD_serv_half = int(WD_serv_len / 2)
	SA_serv_half = int(SA_serv_len / 2)
	SU_serv_half = int(SU_serv_len / 2)


	GTFS_WD_mid_date = GTFS_WD_start_date + datetime.timedelta(days=WD_serv_half)
	GTFS_SA_mid_date = GTFS_SA_start_date + datetime.timedelta(days=SA_serv_half)
	GTFS_SU_mid_date = GTFS_SU_start_date + datetime.timedelta(days=SU_serv_half)

	#GTFS_WD_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
	#GTFS_WD_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))

	line_counter = 0
	text_file = open(fn_cal, 'r')
	for line in text_file:
			line_val = line.split(",")
			if line_val[c_wed] == 1 or line_val[c_wed] == "1":
				WD_start_date_str = str(line_val[c_startD])
				WD_end_date_str = str(line_val[c_endD])
				start_yr = WD_start_date_str[0:4]
				start_mo = WD_start_date_str[4:6]
				start_day = WD_start_date_str[6:8]
				#
				end_yr = WD_end_date_str[0:4]
				end_mo = WD_end_date_str[4:6]
				end_day = WD_end_date_str[6:8]
				#
				WD_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
				WD_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
				if (GTFS_WD_mid_date > WD_start_date) and (GTFS_WD_mid_date < WD_end_date):
					List_WD.append(line_counter)
					servID_list_wed.append(str(line_val[c_service_id]))            
			if line_val[c_sat] == 1 or line_val[c_sat] == "1":
				SA_start_date_str = str(line_val[c_startD])
				SA_end_date_str = str(line_val[c_endD])
				start_yr = SA_start_date_str[0:4]
				start_mo = SA_start_date_str[4:6]
				start_day = SA_start_date_str[6:8]
				#
				end_yr = SA_end_date_str[0:4]
				end_mo = SA_end_date_str[4:6]
				end_day = SA_end_date_str[6:8]
				#
				SA_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
				SA_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
				if (GTFS_SA_mid_date > SA_start_date) and (GTFS_SA_mid_date < SA_end_date):
					List_SA.append(line_counter)
					servID_list_sat.append(str(line_val[c_service_id]))            
			if line_val[c_sun] == 1 or line_val[c_sun] == "1":
				SU_start_date_str = str(line_val[c_startD])
				SU_end_date_str = str(line_val[c_endD])
				start_yr = SU_start_date_str[0:4]
				start_mo = SU_start_date_str[4:6]
				start_day = SU_start_date_str[6:8]
				#
				end_yr = SU_end_date_str[0:4]
				end_mo = SU_end_date_str[4:6]
				end_day = SU_end_date_str[6:8]
				#
				SU_start_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
				SU_end_date = datetime.date(int(end_yr), int(end_mo), int(end_day))
				if (GTFS_SU_mid_date > SU_start_date) and (GTFS_SU_mid_date < SU_end_date):
					List_SU.append(line_counter)
					servID_list_sun.append(str(line_val[c_service_id]))
			line_counter = line_counter + 1    

		##print "Calendar information collected from calendar.txt"


if not os.path.exists(fn_cal):
	if os.path.exists(fn_calendar_dates):
		print "calendar.txt does not exist."
		warnings.append("NOTE: calendar_dates.txt used to identify service dates.")
		with open(fn_calendar_dates, 'r') as f:
			first_line = f.readline()
			#print "first_line"
			#print first_line
		#print first_line
		fl = first_line.split(",")
		#### find the position of W, Sa, Su
		counter = 0
		c_service_id = 0
		c_date = 0
		c_exception_type = 0
		#
		cal_list = []
		cal_list_wed = []
		cal_list_sat = []
		cal_list_sun = []
		#
		max_WD_serv_length = 0
		max_SA_serv_length = 0
		max_SU_serv_length = 0
		#
		servID_list_wed = []
		servID_list_sat = []
		servID_list_sun = []
		#
		### Departure block lists
		## departures during block specified in variable AM_start and AM_end for weekday service
		#DList_WD = defaultdict(list)
		#DList_SA = defaultdict(list)
		#DList_SU = defaultdict(list)
		#
		List_WD = []
		List_SA = []
		List_SU = []
		## departures during block specified in variable PM_start and PM_end for weekday service
		for f in fl:
			#print f
			#print "f"
			if f == "service_id":
					c_service_id = counter
			if f == "date" or f == "Date":
					c_date = counter
			if f == "exception_type" or "exception_type" in f:
					c_exception_type = counter
			counter = counter + 1
		#### find the service id of W, Sa, Su
		print "c_service_id"
		print c_service_id
		print "c_date"
		print c_date
		print "c_exception_type"
		print c_exception_type
		WD_servID = "UNK"
		SA_servID = "UNK"
		SU_servID = "UNK"
		#
		##        DailyDepWD = len(DList_AllDepartures_WD)
		#
		ref_start_date = "22000101"
		ref_end_date = "20000101"
		#
		ref_start_yr = ref_start_date[0:4]
		ref_start_mo = ref_start_date[4:6]
		ref_start_day =  ref_start_date[6:8]
		#
		ref_end_yr = ref_end_date[0:4]
		ref_end_mo = ref_end_date[4:6]
		ref_end_day = ref_end_date[6:8]
		###
		GTFS_WD_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
		GTFS_WD_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))
		#
		GTFS_SA_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
		GTFS_SA_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))
		#
		GTFS_SU_start_date = datetime.date(int(ref_start_yr), int(ref_start_mo), int(ref_start_day))
		GTFS_SU_end_date = datetime.date(int(ref_end_yr), int(ref_end_mo), int(ref_end_day))
		#
		T_GTFS_WD_start_date = "UNK"
		T_GTFS_WD_end_date = "UNK"
		#
		T_GTFS_SA_start_date = "UNK"
		T_GTFS_SA_end_date = "UNK"
		#
		T_GTFS_SU_start_date = "UNK"
		T_GTFS_SU_end_date = "UNK"
		#
		line_counter = 0
		text_file = open(fn_calendar_dates, 'r')
		for line in text_file:
			#print line
			line_val2 = line.split("\n")
			#line_val = line.split(",")
			line_val = line_val2[0].split(",")
			#print "[" + str(line_val[c_exception_type]) + str(type(line_val[c_exception_type])) + "]"
			##print line_val[c_date], line_val[c_exception_type]
			#
			# 1 is used as service is 'added'
			#
			if line_val[c_exception_type] == 1 or line_val[c_exception_type] == "1":
				###print "1!"
				WD_date_str = str(line_val[c_date])
				#WD_end_date_str = str(line_val[c_endD])
				start_yr = WD_date_str[0:4]
				start_mo = WD_date_str[4:6]
				start_day = WD_date_str[6:8]
				#
				WD_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
				if (WD_date < GTFS_WD_start_date):
					GTFS_WD_start_date = WD_date
					#print "Start WD_date"
					#print WD_date
				if (WD_date > GTFS_WD_start_date):
					GTFS_WD_end_date = WD_date
					#print "End WD_date"
					#print WD_date
		WD_serv_len = abs((GTFS_WD_end_date - GTFS_WD_start_date).days)
		#WD_serv_len = abs((GTFS_WD_end_date - GTFS_WD_start_date).days)
		#SA_serv_len = abs((GTFS_SA_end_date - GTFS_SA_start_date).days)
		#SU_serv_len = abs((GTFS_SU_end_date - GTFS_SU_start_date).days)
		#
		WD_serv_half = int(WD_serv_len / 2)
		#WD_serv_half = int(WD_serv_len / 2)
		#SA_serv_half = int(SA_serv_len / 2)
		#SU_serv_half = int(SU_serv_len / 2)
		#
		GTFS_WD_mid_date = GTFS_WD_start_date + datetime.timedelta(days=WD_serv_half)
		#GTFS_WD_mid_date = GTFS_WD_start_date + datetime.timedelta(days=WD_serv_half)
		#GTFS_SA_mid_date = GTFS_SA_start_date + datetime.timedelta(days=SA_serv_half)
		#GTFS_SU_mid_date = GTFS_SU_start_date + datetime.timedelta(days=SU_serv_half)
		#
		mid_date_day = GTFS_WD_mid_date.weekday()
		print mid_date_day
		if mid_date_day == 0:
			WD_AddDays = 2
			SA_AddDays = 5
			SU_AddDays = 6
		if mid_date_day == 1:
			WD_AddDays = 1
			SA_AddDays = 4
			SU_AddDays = 5
		if mid_date_day == 2:
			WD_AddDays = 0
			SA_AddDays = 3
			SU_AddDays = 4
		if mid_date_day == 3:
			WD_AddDays = -1
			SA_AddDays = 2
			SU_AddDays = 3            
		if mid_date_day == 4:
			WD_AddDays = -2
			SA_AddDays = 1
			SU_AddDays = 2
		if mid_date_day == 5:
			WD_AddDays = -3
			SA_AddDays = 0
			SU_AddDays = 1
		if mid_date_day == 6:
			WD_AddDays = -4
			SA_AddDays = -1
			SU_AddDays = 0
		#GTFS_WD_date = GTFS_WD_mid_date + WD_AddDays.days
		#end_date = date_1 + datetime.timedelta(days=10)
		GTFS_WD_date = GTFS_WD_mid_date + datetime.timedelta(days=WD_AddDays)
		#GTFS_SA_date = GTFS_WD_mid_date + SA_AddDays.days
		GTFS_SA_date = GTFS_WD_mid_date + datetime.timedelta(days=SA_AddDays)
		#GTFS_SU_date = GTFS_WD_mid_date + SU_AddDays.days
		GTFS_SU_date = GTFS_WD_mid_date + datetime.timedelta(days=SU_AddDays)
		print "GTFS_WD_date"
		print GTFS_WD_date
		print "GTFS_SA_date"
		print GTFS_SA_date
		print "GTFS_SU_date"
		print GTFS_SU_date
		#
		line_counter = 0
		text_file = open(fn_calendar_dates, 'r')
		for line in text_file:
			line_val2 = line.split("\n")
			#line_val = line.split(",")
			line_val = line_val2[0].split(",")
			##line_val = line.split(",")
			#print line
			##print line_val[c_exception_type]
			if line_val[c_exception_type] == 1 or line_val[c_exception_type] == "1":
				#print "UES"
				WD_date_str = str(line_val[c_date])
				#print "WD_date_str"
				#print WD_date_str
				#WD_end_date_str = str(line_val[c_endD])
				start_yr = WD_date_str[0:4]
				start_mo = WD_date_str[4:6]
				start_day = WD_date_str[6:8]
				#
				WD_date = datetime.date(int(start_yr), int(start_mo), int(start_day))
				#print "WD_date"
				#print WD_date
				if (WD_date == GTFS_WD_date):
					#GTFS_WD_start_date = WD_date
					List_WD.append(line_counter)
					servID_list_wed.append(str(line_val[c_service_id]))
				if (WD_date == GTFS_SA_date):
					#GTFS_WD_end_date = WD_date
					List_SA.append(line_counter)
					servID_list_sat.append(str(line_val[c_service_id]))
				if (WD_date == GTFS_SU_date):
					#GTFS_WD_end_date = WD_date
					List_SU.append(line_counter)
					servID_list_sun.append(str(line_val[c_service_id]))
		print "servID_list_wed"
		print servID_list_wed
		print "servID_list_sat"
		print servID_list_sat
		print "servID_list_sun"
		print servID_list_sun

		print "Calendar information collected from calendar_dates.txt"


print "Calendar information collected"


##############################
### find trip keys
##############################

with open(fn_trips, 'r') as f:
	first_line = f.readline()
fl = first_line.split(",")

#### find the position of W, Sa, Su
##trip_id,stop_id,arrival_time,departure_time,stop_sequence,stop_headsign

c_route_id = 0
c_trip_id = 0
c_service_id = 0
c_direction_id = 0
c_headsign_id = 0

###stop_headsign = 0

counter = 0
for f in fl:
		#print f
		if f == "route_id":
				c_route_id = counter
		if f == "trip_id":
				c_trip_id = counter
		if f == "service_id":
				c_service_id = counter
		if f == "direction_id":
				c_direction_id = counter
		if f == "headsign_id":
				c_headsign_id = counter
		counter = counter + 1

text_file = open(fn_trips, 'r')
#text_file.write(textfile_string)
for line in text_file:
		l = line.split(",")
		if l[c_route_id] != "route_id":
			DICT_route [l[c_trip_id]] = l[c_route_id]
			DICT_service  [l[c_trip_id]] = l[c_service_id]
			DICT_direction  [l[c_trip_id]] = l[c_direction_id]
			DICT_headsign  [l[c_trip_id]] = l[c_headsign_id]

#print routeD
#print serviceD
#print directionD
#print headsignD

##############################
### find routes keys
##############################

with open(fn_routes, 'r') as f:
	first_line = f.readline()
###print first_line
fl = first_line.split(",")

#### find the position of W, Sa, Su
##trip_id,stop_id,arrival_time,departure_time,stop_sequence,stop_headsign

c_agency_id = 0
c_route_id = 0
c_route_short_name = 0
c_route_long_name = 0

###agencyidName = "UNK"
agency_idNum = "UNK"
agency_idName = "UNK"

route_agency_id_used = False

counter = 0

for f in fl:
		#print f
		if f == "agency_id":
				c_agency_id = counter
				route_agency_id_used = True
		if f == "route_id":
				c_route_id = counter
		if f == "route_short_name":
				c_route_short_name = counter
		if f == "route_long_name":
				c_route_long_name = counter
		#if f == "direction_id":
		#        direction_id = counter
		#if f == "headsign_id":
		#        headsign_id = counter
		counter = counter + 1

text_file = open(fn_routes, 'r')
#text_file.write(textfile_string)
for line in text_file:
		l = line.split(",")
		if l[c_route_id] != "route_id":
			DICT_routeShortName [l[c_route_id]] = l[c_route_short_name]
			DICT_routeLongName  [l[c_route_id]] = l[c_route_long_name]
			if route_agency_id_used:
				DICT_routeAgencyID[l[c_route_id]] = l[c_agency_id]

#DICT_routeAgencyID

#print "done with routes"
print "Route information collected"

##############################
### find stop times keys
##############################

with open(fn_stop_times, 'r') as f:
	first_line = f.readline()
###########print first_line
fl = first_line.split(",")

c_trip_id = 0
c_stop_id = 0
c_arrival_time = 0
c_departure_time = 0
c_stop_headsign = 0

counter = 0

for f in fl:
		#print f
		if f == "trip_id":
				c_trip_id = counter
		if f == "stop_id":
				c_stop_id = counter
		if f == "arrival_time":
				c_arrival_time = counter
		if f == "departure_time":
				c_departure_time = counter
		if f == "stop_headsign":
				c_stop_headsign = counter
		counter = counter + 1

##############################
### find stop times
##############################

text_file = open(fn_stop_times, 'r')
#text_file.write(textfile_string)
for line in text_file:
	l = line.split(",")
	file_key = line[0]
	#print l[stop_id]
	if l[c_stop_id] in id_stops:
		if l[c_trip_id] != "trip_id":
			routeNum = DICT_route[l[c_trip_id]]
			serviceDay = DICT_service[l[c_trip_id]]
			direction_id = DICT_direction[l[c_trip_id]]
			headsign_id = DICT_direction[l[c_trip_id]]
			if route_agency_id_used:
				#print "agency_id"
				#print agency_id
				#print "routeNum"
				#print routeNum
				#print DICT_routeAgencyID
				if agency_id != "agency_id":
					agency = "|" + DICT_routeAgencyID[routeNum]
					agency_idNum = DICT_routeAgencyID[routeNum]
					#print "agency"
					#print agency
					#print agency_idNum
					#print "--agency_id"
					#print agency_idNum
					agency_idName = agency_idNum + "|" + DICT_AgencyName[agency_idNum]
			else:
				agency = ""
				agency_idNum = ""
				agency_idName = ""
				#DICT_routeAgencyID[l[c_route_id]] = l[c_agency_id]            
			###print l[stop_id]
			#
			route_short_name = DICT_routeShortName[routeNum]
			route_long_name = DICT_routeLongName[routeNum]
			#
			DList_servedBy[l[c_stop_id]].append(route_short_name)
			DList_servedByAgency[l[c_stop_id]].append(route_short_name + agency)
			DList_servedByTrip[l[c_stop_id]].append(l[c_trip_id])
			DList_AgencyAtStop[l[c_stop_id]].append(agency_idNum)
			DList_AgencyNameAtStop[l[c_stop_id]].append(agency_idName)
			####
			servHr = l[c_departure_time].split(":")
			##if str(WD_servID) == str(serviceDay):
			if str(serviceDay) in servID_list_wed:
				DList_AllDepartures_WD[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" + str(agency))
				#DList_AllDepartures_WD[l[c_stop_id]].append(str(agency) + str(route_short_name) + "|" + str(l[c_departure_time]))
				####print "hour:", str(str(servHr[0]))
				if str(servHr[0]) == str(AM):
						DList_AMDepartures_WD[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" + str(agency))
				if str(servHr[0]) == str(PM):
						DList_PMDepartures_WD[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" +  str(agency))
				###
				if str(servHr[0])in AM_block:
						DList_AMDeparturesBLK_WD[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" +  str(agency))
				if str(servHr[0])in PM_block:
						DList_PMDeparturesBLK_WD[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" +  str(agency))
				###
			##if str(SA_servID) == str(serviceDay):
			if str(serviceDay) in servID_list_sat:    
					DList_AllDepartures_SA[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name) +  "|"  + direction_id +  "|" +  str(agency))
					if str(servHr[0]) == str(AM):
							DList_AMDepartures_SA[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|"  + direction_id +  "|" +  str(agency))
					if str(servHr[0]) == str(PM):
							DList_PMDepartures_SA[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|"  + direction_id +  "|" +  str(agency))
					###
					if str(servHr[0])in AM_block:
							DList_AMDeparturesBLK_SA[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|" + direction_id +  "|" +  str(agency))
					if str(servHr[0])in PM_block:
							DList_PMDeparturesBLK_SA[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|"  + direction_id +  "|" +  str(agency))
					###
			##if str(SU_servID) == str(serviceDay):
			if str(serviceDay) in servID_list_sun:    
					DList_AllDepartures_SU[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|"  + direction_id +  "|" +  str(agency))
					if str(servHr[0]) == str(AM):
							DList_AMDepartures_SU[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|" + direction_id +  "|" +  str(agency))
					if str(servHr[0]) == str(PM):
							DList_PMDepartures_SU[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|" + direction_id +  "|" +  str(agency))
					###
					if str(servHr[0])in AM_block:
							DList_AMDeparturesBLK_SU[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|" + direction_id +  "|" +  str(agency))
					if str(servHr[0])in PM_block:
							DList_PMDeparturesBLK_SU[l[c_stop_id]].append(str(l[c_departure_time]) + "|" + str(route_short_name)  +  "|" + direction_id +  "|" +  str(agency))
					###

servedBy = []

#print agency_id
print agency_name
print agency_url
print agency_timezone
print agency_lang
print agency_phone

print "GTFS_start_date:", GTFS_WD_start_date
print "GTFS_end_date:", GTFS_WD_end_date

## Open a file to write to:
summary_file_name = "service_summmary.csv"
summary_file = os.path.join(gtfs_path, summary_file_name)

#fieldnames = ("stop_id,stop_name,stop_LatLon,routes_serving_stop,agency_name,agency_url,agency_phone,GTFS_WD_start_date,GTFS_WD_end_date,AM_WD_depart,PM_WD_depart,AM_SA_depart,PM_SA_depart,AM_SU_depart,PM_SU_depart,AvgAM_WD_BlkStops,AvgPM_WD_BlkStops,AvgAM_SA_BlkStops,AvgPM_SA_BlkStops,AvgAM_SU_BlkStops,AvgPM_SU_BlkStops,daily_WD_stops,daily_SA_stops,daily_SU_stops,AM_departures_WD,PM_departures_WD,AM_departures_SA,PM_departures_SA,AM_departures_SU,PM_departures_SU,all_WD_dep,all_SA_dep,all_SU_dep")
##fieldnames = ("stop_id,stop_name,stop_LatLon,routes_serving_stop,AM_WD_depart,PM_WD_depart,AM_SA_depart,PM_SA_depart,AM_SU_depart,PM_SU_depart,AvgAM_WD_BlkStops,AvgPM_WD_BlkStops,AvgAM_SA_BlkStops,AvgPM_SA_BlkStops,AvgAM_SU_BlkStops,AvgPM_SU_BlkStops,daily_WD_stops,daily_SA_stops,daily_SU_stops,AM_departures_WD,PM_departures_WD,AM_departures_SA,PM_departures_SA,AM_departures_SU,PM_departures_SU,all_WD_dep,all_SA_dep,all_SU_dep")

fieldnames = "stop_id,stop_name,stop_LatLon,routes_serving_stop,"
fieldnames = fieldnames + "routes_serving_stop_agency,"
fieldnames = fieldnames + "agency_name,agency_URL,"
fieldnames = fieldnames + "GTFS_start_date,GTFS_end_date,"
fieldnames = fieldnames + "agencies_at_stop,"
fieldnames = fieldnames + "agencies_name_at_stop,"
fieldnames = fieldnames + "stop_zone,"
fieldnames = fieldnames + "agency_fare_url,"
fieldnames = fieldnames + "AM_WD_depart,PM_WD_depart,AM_SA_depart,PM_SA_depart,AM_SU_depart,PM_SU_depart,"
fieldnames = fieldnames + "AvgAM_WD_BlkStops,AvgPM_WD_BlkStops,AvgAM_SA_BlkStops,AvgPM_SA_BlkStops,AvgAM_SU_BlkStops,AvgPM_SU_BlkStops,daily_WD_stops,daily_SA_stops,daily_SU_stops,"
#fieldnames = fieldnames + "AM_departures_WD,PM_departures_WD,AM_departures_SA,PM_departures_SA,AM_departures_SU,PM_departures_SU,"
fieldnames = fieldnames + "all_WD_dep,all_SA_dep,all_SU_dep"

file = open(summary_file, "w")
file.write(fieldnames + "\n")

#print DICT_stop_name
#print DICT_stop_lat

for stop in id_stops:
	#print "Stop", stop
	#print "Stop name", DICT_stop_name[stop]
	#print "Stop lat/lon", "[", DICT_stop_lat[stop], ",", DICT_stop_lon[stop], "]"
	#for s in servedByD:
	StopService = []
	StopList = DList_servedBy[stop]
	StopServiceAgency = []
	StopListAgency = DList_servedByAgency[stop]
	#
	AgencyStop = []
	AgenciesAtStop = DList_AgencyAtStop[stop]
	#
	AgencyNameStop = []
	AgenciesNameAtStop = DList_AgencyNameAtStop[stop]
	## sort stop time lists
	DList_servedBy[stop].sort()
	DList_servedByAgency[stop].sort()
	DList_AllDepartures_WD[stop].sort()
	DList_AMDepartures_WD[stop].sort()
	DList_PMDepartures_WD[stop].sort()
	DList_AMDeparturesBLK_WD[stop].sort()
	DList_PMDeparturesBLK_WD[stop].sort()
	DList_AllDepartures_SA[stop].sort()
	DList_AMDepartures_SA[stop].sort()
	DList_PMDepartures_SA[stop].sort()
	DList_AMDeparturesBLK_SA[stop].sort()
	DList_PMDeparturesBLK_SA[stop].sort()
	DList_AllDepartures_SU[stop].sort()
	DList_AMDepartures_SU[stop].sort()
	DList_PMDepartures_SU[stop].sort()
	DList_AMDeparturesBLK_SU[stop].sort()
	DList_PMDeparturesBLK_SU[stop].sort()
	##
	setStopList = set(StopList)
	for t in setStopList:
			StopService.append(t)
	#print "Transit routes that serve stop", str(stop), ":", str(StopService)
	#
	##
	setStopListAgency = set(StopListAgency)
	for t in setStopListAgency:
			StopServiceAgency.append(t)
	#print "Transit routes (with agency) that serve stop", str(stop), ":", str(StopServiceAgency)
	#
	setAgenciesAtStop = set(AgenciesAtStop)
	for t in setAgenciesAtStop:
			AgencyStop.append(t)
	#print "Transit agencies that serve stop", str(stop), ":", str(AgencyStop)
	#
	setAgenciesNameAtStop = set(AgenciesNameAtStop)
	for a in setAgenciesNameAtStop:
			AgencyNameStop.append(a)
	#print "Transit agencies that serve stop", str(stop), ":", str(AgencyNameStop)
	#
	DailyDepWD = len(DList_AllDepartures_WD[stop])
	#print "Daily departures WD:", DailyDepWD
	DailyDepSA = len(DList_AllDepartures_SA[stop])
	#print "Daily departures SA:", DailyDepSA
	DailyDepSU = len(DList_AllDepartures_SU[stop])
	#print "Daily departures SU:", DailyDepSU
	#
	#print DList_AMDepartures_WD[stop]
	AMDep_WD = len(DList_AMDepartures_WD[stop])
	#print "AM WD departures at stop", str(stop), ":", AMDep_WD
	#print DList_PMDepartures_WD[stop]
	#print "PM WD departures: " + str(stop)
	PMDep_WD = len(DList_PMDepartures_WD[stop])
	#print "PM WD departures at stop", str(stop), ":", PMDep_WD
	#print PMDep_WD
	#print "PM WD departures at stop", str(stop), ":", PMDep_WD
	#
	#print DList_AMDepartures_SA[stop]
	#print "AM SA departures: " + str(stop)
	AMDep_SA = len(DList_AMDepartures_SA[stop])
	#print "AM SA departures at stop", str(stop), ":", AMDep_SA
	#print AMDep_SA
	#print DList_PMDepartures_SA[stop]
	#print "PM SA departures: " + str(stop)
	PMDep_SA = len(DList_PMDepartures_SA[stop])
	#print "PM SA departures at stop", str(stop), ":", PMDep_SA
	#print PMDep_SA
	#
	#print DList_AMDepartures_SU[stop]
	#print "AM SU departures: " + str(stop)
	AMDep_SU = len(DList_AMDepartures_SU[stop])
	#print "AM SU departures at stop", str(stop), ":", AMDep_SU
	#print AMDep_SU
	#print DList_PMDepartures_SU[stop]
	#print "PM SU departures: " + str(stop)
	PMDep_SU = len(DList_PMDepartures_SU[stop])
	#print "PM SU departures at stop", str(stop), ":", PMDep_SU
	#print PMDep_SU
	#
	AMDepBLK_WD = len(DList_AMDeparturesBLK_WD[stop])
	AMDepBLK_AVG_HR_WD = float(AMDepBLK_WD / AM_block_hours)
	#print "AM Block WD departures at stop", str(stop), ":", AMDepBLK_WD
	#print "Average # departures, AM Block WD at stop", str(stop), ":", AMDepBLK_AVG_HR_WD
	##print "Average # departures, AM Block WD at stop", str(stop), ":", float(AMDepBLK_WD / AM_block_hours)
	#
	PMDepBLK_WD = len(DList_PMDeparturesBLK_WD[stop])
	PMDepBLK_AVG_HR_WD = float(PMDepBLK_WD / PM_block_hours)
	#print "PM Block WD departures at stop", str(stop), ":", PMDepBLK_WD
	#print "Average # departures, PM Block WD at stop", str(stop), ":", PMDepBLK_AVG_HR_WD
	##print "Average # departures, PM Block WD at stop", str(stop), ":", float(PMDepBLK_WD / PM_block_hours)
	#
	AMDepBLK_SA = len(DList_AMDeparturesBLK_SA[stop])
	AMDepBLK_AVG_HR_SA = float(AMDepBLK_SA / AM_block_hours)
	#print "AM Block SA departures at stop", str(stop), ":", AMDepBLK_SA
	#print "Average # departures, AM Block SA at stop", str(stop), ":", AMDepBLK_AVG_HR_SA
	##print "Average # departures, AM Block SA at stop", str(stop), ":", float(AMDepBLK_SA / AM_block_hours)
	#
	PMDepBLK_SA = len(DList_PMDeparturesBLK_SA[stop])
	PMDepBLK_AVG_HR_SA = float(PMDepBLK_SA / PM_block_hours)
	#print "PM Block SA departures at stop", str(stop), ":", PMDepBLK_SA
	#print "Average # departures, PM Block SA at stop", str(stop), ":", PMDepBLK_AVG_HR_SA
	##print "Average # departures, PM Block SA at stop", str(stop), ":", float(PMDepBLK_SA / PM_block_hours)
	#
	AMDepBLK_SU = len(DList_AMDeparturesBLK_SU[stop])
	AMDepBLK_AVG_HR_SU = float(AMDepBLK_SU / AM_block_hours)
	#print "AM Block SU departures at stop", str(stop), ":", AMDepBLK_SU
	#print "AM Block SU departures at stop", str(stop), ":", AMDepBLK_AVG_HR_SU
	##print "Average # departures, AM Block SU at stop", str(stop), ":", float(AMDepBLK_SU / AM_block_hours)
	#
	PMDepBLK_SU = len(DList_PMDeparturesBLK_SU[stop])
	PMDepBLK_AVG_HR_SU = float(PMDepBLK_SU / PM_block_hours)
	#print "PM Block SU departures at stop", str(stop), ":", PMDepBLK_SU
	#print "Average # departures, PM Block SU at stop", str(stop), ":", PMDepBLK_AVG_HR_SU
	##print "Average # departures, PM Block SU at stop", str(stop), ":", float(PMDepBLK_SU / PM_block_hours)
	#
	#EDT_StopService = str(StopService)
	#EDT_StopService.replace(",", "|")
	##EDT_StopService.replace("[", "")
	#EDT_StopService.replace("]", "")
	#writeString = str(stop) + ',' +  DICT_stop_name[stop] + ',' + str(DICT_stop_lat[stop]) + '|' + str(DICT_stop_lon[stop]) + ',"' +  str(StopService) + '",' + str(AMDep_WD) + ',' +  str(PMDep_WD) + ',' +  str(AMDep_SA) + ',' +  str(PMDep_SA) + ',' +  str(AMDep_SU) + ',' +  str(PMDep_SU) + ',' + str(AMDepBLK_AVG_HR_WD)  + ',' +  str(PMDepBLK_AVG_HR_WD)  + ',' +  str(AMDepBLK_AVG_HR_SA)  + ',' +  str(PMDepBLK_AVG_HR_SA)  + ',' +  str(AMDepBLK_AVG_HR_SU)  + ',' +  str(PMDepBLK_AVG_HR_SU) + ','  + str(DailyDepWD) + ',' + str(DailyDepSA) + ',' + str(DailyDepSU) + ',"' +  str(DList_AMDepartures_WD[stop]) + '","' + str(DList_PMDepartures_WD[stop]) + '","' +  str(DList_AMDepartures_SA[stop])  + '","' + str(DList_PMDepartures_SA[stop])  + '","' + str(DList_AMDepartures_SU[stop])  + '","' + str(DList_PMDepartures_SU[stop])   + '",' + str(DList_AllDepartures_WD[stop]) + '","'  +  + str(DList_AllDepartures_SA[stop]) + '","'  +  + str(DList_AllDepartures_SU[stop]) + '",'  + '\n'
	######writeString = str(stop) + ',' + DICT_stop_name[stop] + ',' + str(DICT_stop_lat[stop]) + '|' + str(DICT_stop_lon[stop]) + ',"' +  str(StopService)  + ',' + str(agency_name) + ',' + str(agency_url)  + ',' + str(agency_phone) + ',' + str(GTFS_WD_start_date) + ',' + str(GTFS_WD_end_date) + '",' + str(AMDep_WD) + ',' +  str(PMDep_WD) + ',' +  str(AMDep_SA) + ',' +  str(PMDep_SA) + ',' +  str(AMDep_SU) + ',' +  str(PMDep_SU) + ',' + str(AMDepBLK_AVG_HR_WD)  + ',' +  str(PMDepBLK_AVG_HR_WD)  + ',' +  str(AMDepBLK_AVG_HR_SA)  + ',' +  str(PMDepBLK_AVG_HR_SA)  + ',' +  str(AMDepBLK_AVG_HR_SU)  + ',' +  str(PMDepBLK_AVG_HR_SU) + ','  + str(DailyDepWD) + ',' + str(DailyDepSA) + ',' + str(DailyDepSU) + ',"' +  str(DList_AMDepartures_WD[stop]) + '","' + str(DList_PMDepartures_WD[stop]) + '","' +  str(DList_AMDepartures_SA[stop])  + '","' + str(DList_PMDepartures_SA[stop])  + '","' + str(DList_AMDepartures_SU[stop])  + '","' + str(DList_PMDepartures_SU[stop]) + '","' + str(DList_AllDepartures_WD[stop]) + '","'  +  str(DList_AllDepartures_SA[stop]) + '","'  +  str(DList_AllDepartures_SU[stop]) + '",'  + '\n'
	#################writeString = str(stop) + ',' + DICT_stop_name[stop] + ',' + str(DICT_stop_lat[stop]) + '|' + str(DICT_stop_lon[stop]) + ',"' +  str(StopService) + '",' + str(AMDep_WD) + ',' +  str(PMDep_WD) + ',' +  str(AMDep_SA) + ',' +  str(PMDep_SA) + ',' +  str(AMDep_SU) + ',' +  str(PMDep_SU) + ',' + str(AMDepBLK_AVG_HR_WD)  + ',' +  str(PMDepBLK_AVG_HR_WD)  + ',' +  str(AMDepBLK_AVG_HR_SA)  + ',' +  str(PMDepBLK_AVG_HR_SA)  + ',' +  str(AMDepBLK_AVG_HR_SU)  + ',' +  str(PMDepBLK_AVG_HR_SU) + ','  + str(DailyDepWD) + ',' + str(DailyDepSA) + ',' + str(DailyDepSU) + ',"' +  str(DList_AMDepartures_WD[stop]) + '","' + str(DList_PMDepartures_WD[stop]) + '","' +  str(DList_AMDepartures_SA[stop])  + '","' + str(DList_PMDepartures_SA[stop])  + '","' + str(DList_AMDepartures_SU[stop])  + '","' + str(DList_PMDepartures_SU[stop]) + '","' + str(DList_AllDepartures_WD[stop]) + '","'  +  str(DList_AllDepartures_SA[stop]) + '","'  +  str(DList_AllDepartures_SU[stop]) + '",'  + '\n'
	writeString = str(stop) + ','
	if stop in DICT_stop_name:
		#print(DICT_stop_name[stop])
		writeString = writeString + DICT_stop_name[stop] + ','
	else:
		writeString = writeString + ','
	if stop in DICT_stop_lat:
		writeString = writeString + str(DICT_stop_lat[stop]) + '|' + str(DICT_stop_lon[stop]) + ','
		writeString = writeString + '"' + str(StopService) + '",'
		writeString = writeString + '"' + str(StopServiceAgency) + '",'
		writeString = writeString + str(agency_name) + ','
		writeString = writeString + str(agency_url) + ','
		writeString = writeString + str(GTFS_WD_start_date) + ','
		writeString = writeString + str(GTFS_WD_end_date) + ','
		#writeString = writeString + str(AgencyNameStop) + ','
		writeString = writeString + str(AgencyStop) + ','
		writeString = writeString + str(AgencyNameStop) + ','
		if zone_id_used:
			writeString = writeString + DICT_zone_id[stop] + ','
		else:
			writeString = writeString + "UNK,"
		if fare_url_used:
			writeString = writeString + str(publishing_agency_fareURL) + ','
		else:
			writeString = writeString + "UNK,"
		writeString = writeString + str(AMDep_WD) + ','
		writeString = writeString + str(PMDep_WD) + ','
		writeString = writeString + str(AMDep_SA) + ','
		writeString = writeString + str(PMDep_SA) + ','
		writeString = writeString + str(AMDep_SU) + ','
		writeString = writeString + str(PMDep_SU) + ','
		writeString = writeString + str(AMDepBLK_AVG_HR_WD)  + ','
		writeString = writeString + str(PMDepBLK_AVG_HR_WD)  + ','
		writeString = writeString + str(AMDepBLK_AVG_HR_SA)  + ','
		writeString = writeString + str(PMDepBLK_AVG_HR_SA)  + ','
		writeString = writeString + str(AMDepBLK_AVG_HR_SU)  + ','
		writeString = writeString + str(PMDepBLK_AVG_HR_SU) + ','
		writeString = writeString + str(DailyDepWD) + ','
		writeString = writeString + str(DailyDepSA) + ','
		writeString = writeString + str(DailyDepSU) + ','
		#writeString = writeString + '"' + str(DList_AMDepartures_WD[stop]) + '",'
		#writeString = writeString + '"' + str(DList_PMDepartures_WD[stop]) + '",'
		#writeString = writeString + '"' + str(DList_AMDepartures_SA[stop])  + '",'
		#writeString = writeString + '"' + str(DList_PMDepartures_SA[stop])  + '",'
		#writeString = writeString + '"' + str(DList_AMDepartures_SU[stop])  + '",'
		#writeString = writeString + '"' + str(DList_PMDepartures_SU[stop]) + '",'
		writeString = writeString + '"' + str(DList_AllDepartures_WD[stop]) + '",'
		writeString = writeString + '"' + str(DList_AllDepartures_SA[stop]) + '",'
		writeString = writeString + '"' + str(DList_AllDepartures_SU[stop]) + '",'
		writeString = writeString + '\n'
	else:
		writeString = writeString + "Warning: this stop is not in the stop dictionary." + '\n' 
	file.write(writeString)
		#TStopList = stop + "--" + str(StopList)
		#print "TStopList"
		#print TStopList
		#servedBy = []
file.close()


#agency_name,agency_url,agency_phone,GTFS_WD_start_date,GTFS_WD_end_date

# + ',' + agency_name + ',' + agency_url  + ',' + agency_phone + ',' + GTFS_WD_start_date + ',' + GTFS_WD_end_date


##################  write to csv file
##
##summary_file_name = "service_summmary.csv"
##summary_file = os.path.join(gtfs_path, summary_file_name)
##
##fieldnames = "stop_name","stop_LatLon","routes_serving_stops"
##
##with open(summary_file, 'w') as csvfile:
##    ##fieldnames = ['first_name', 'last_name']
##    #fieldnames = ['first_name', 'last_name']
##    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
##
##    writer.writeheader()
##    for stop in id_stops:
##        writer.writerow("stop")
##        ##writer.writerow({stop})
##        #writer.writerow({stop, "[", DICT_stop_lat[stop], "|", DICT_stop_lon[stop], "]", StopService})
##        #print "Stop", stop
##        #print "Stop name", DICT_stop_name[stop]
##        #print "Stop lat/lon", "[", DICT_stop_lat[stop], ",", DICT_stop_lon[stop], "]"
##        #for s in servedByD:
##        ##writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
##        ##writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
##        ##writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
##
##


##print "WD Service date analyzed:"
##print GTFS_WD_date

##print "SA Service date analyzed:"
##print GTFS_SA_date

##print "SU Service date analyzed:"
##print GTFS_SU_date


if len(servID_list_wed) == 0:
	warn_weekday = "Warning: NO weekday service identified"
	warnings.append(warn_weekday)
	print warn_weekday
if len(servID_list_sat) == 0:
	warn_saturday = "Warning: NO Saturday service identified"
	warnings.append(warn_saturday)
	print warn_saturday
if len(servID_list_sun) == 0:
	warn_sunday = "Warning: NO Sunday service identified"
	warnings.append(warn_sunday)
	print warn_sunday

## set up file for warnings
warning_file_name = "conversion_notes.txt"
warning_file = os.path.join(gtfs_path, warning_file_name)
warning_fieldnames = "note"

wfile = open(warning_file, "w")
wfile.write(warning_fieldnames + "\n")

writeString = ""

if len(warnings) > 0:
	for w in warnings:
		#warning_string = w
		#print warning_string
		#writeString = writeString + str(warning_string) + "\n"
		writeString = writeString + str(w) + "\n"
	wfile.write(writeString)
	wfile.close()
	print "Conversion notes recorded.  Please check file."




print "service_id for WD trips"
print servID_list_wed
print "service_id for SAT trips"
print servID_list_sat
print "service_id for SUN trips"
print servID_list_sun


print "Time used for", len(id_stops), "stops"

#### CODE

#end_time = datetime.datetime.now().replace(microsecond=0)
#print(end_time-start_time)
#print "done"
##return


###a = datetime.datetime.now().replace(microsecond=0)

#print "hello, you made it!"
#print num_args

#GTFSDir = sys.argv[0]
#stop_id = sys.argv[1]
###gtfs_path, stop_list
##gtfs_path = sys.argv[0]
##stop_list = sys.argv[1]

##FindTransitServiceAtStops(gtfs_path, stop_list)

#print GTFSDir
#print stop_id

#for s in stop_id:
#    print s
	
#print "done!"

###b = datetime.datetime.now().replace(microsecond=0)
###print(b-a)
