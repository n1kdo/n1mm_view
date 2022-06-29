"""
this file contains configuration values for n1mm_view.
This should be the only thing you would need to customize.
"""
import datetime
import logging

""" name of database file """
DATABASE_FILENAME = 'n1mm_view.db'
""" Name of the event/contest """
EVENT_NAME = 'Field Day'
""" start time of the event/contest in YYYY-MM-DD hh:mm:ss format """
# EVENT_START_TIME = datetime.datetime.strptime('2019-06-25 18:00:00', '%Y-%m-%d %H:%M:%S')
# EVENT_START_TIME = datetime.datetime.strptime('2021-06-26 18:00:00', '%Y-%m-%d %H:%M:%S')
EVENT_START_TIME = datetime.datetime.strptime('2022-06-25 18:00:00', '%Y-%m-%d %H:%M:%S')
""" end time of the event/contest """
# EVENT_END_TIME = datetime.datetime.strptime('2019-06-26 17:59:59', '%Y-%m-%d %H:%M:%S')
# EVENT_END_TIME = datetime.datetime.strptime('2021-06-27 17:59:59', '%Y-%m-%d %H:%M:%S')
EVENT_END_TIME = datetime.datetime.strptime('2022-06-26 17:59:59', '%Y-%m-%d %H:%M:%S')
""" port number used by N1MM+ for UDP broadcasts This matches the port you set in N1MM Configurator UDP logging """
N1MM_BROADCAST_PORT = 12060
""" 
broadcast IP address, used by log re-player. 
This could be the IP of the N1MM master, or just the last address in the network segment 
"""
N1MM_BROADCAST_ADDRESS = '192.168.1.255'
""" n1mm+ log file name used by replayer """
# N1MM_LOG_FILE_NAME = 'MyClubCall-2019.s3db'
N1MM_LOG_FILE_NAME = 'MyClubCall-2020.s3db'
""" QTH here is the location of your event. We mark this location with a red dot when we generate the map views."""
""" QTH Latitude """
QTH_LATITUDE = 34.0109629
""" QTH Longitude """
QTH_LONGITUDE = -84.4616047
""" number of seconds before automatic display change to the next screen """
DISPLAY_DWELL_TIME = 6
"""
number of seconds before automatic info recalculation from database. Too low makes the Pi work harder.
Too high makes a lag in viewing your results.
"""
DATA_DWELL_TIME = 60
""" log level for apps -- one of logging.WARN, logging.INFO, logging.DEBUG """
LOG_LEVEL = logging.WARN
#
"""images directory, or None if not writing image files"""
IMAGE_DIR = '/mnt/ramdisk/n1mm_view/html'
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
""" set HEADLESS True to not open graphics window. This is for using only the Apache option."""
HEADLESS = False

# This should match the directory above we want to send from the directory to which we write.
POST_FILE_COMMAND = 'rsync -avz /mnt/ramdisk/n1mm_view/html/* sparc:www/n1mm_view/html'

""" Font Sizes """
# If font seems too big, try 60 for VIEW_FONT and 100 for BIGGER_FONT
VIEW_FONT = 64
BIGGER_FONT = 180
