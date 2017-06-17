"""
this file contains configuration values for n1mm_view.
If I did this right, this should be the only thing a user needs to customize.
"""
import datetime
import logging

""" name of database file """
DATABASE_FILENAME = 'n1mm_view.db'
""" Name of the event/contest """
EVENT_NAME = 'N4N Field Day'
""" start time of the event/contest in YYYY-MM-DD hh:mm:ss format """
# EVENT_START_TIME = datetime.datetime.strptime('2015-06-27 18:00:00', '%Y-%m-%d %H:%M:%S')
EVENT_START_TIME = datetime.datetime.strptime('2016-06-25 18:00:00', '%Y-%m-%d %H:%M:%S')
""" end time of the event/contest """
# EVENT_END_TIME = datetime.datetime.strptime('2015-06-28 17:59:59', '%Y-%m-%d %H:%M:%S')
EVENT_END_TIME = datetime.datetime.strptime('2016-06-26 17:59:59', '%Y-%m-%d %H:%M:%S')
""" port number used by N1MM+ for UDP broadcasts """
N1MM_BROADCAST_PORT = 12060
""" broadcast IP address, used by log replayer """
N1MM_BROADCAST_ADDRESS = '192.168.1.255'
""" n1mm+ log file name used by replayer """
# N1MM_LOG_FILE_NAME = '2015N4N.s3db'
N1MM_LOG_FILE_NAME = 'n4n-2016-final.s3db'
""" QTH Latitude """
QTH_LATITUDE = 34.0109629
""" QTH Longitude """
QTH_LONGITUDE = -84.4616047
""" number of seconds before automatic display change """
DISPLAY_DWELL_TIME = 6
""" number of seconds before automatic graph update from database """
DATA_DWELL_TIME = 60
""" log level for apps -- one of logging.WARN, logging.INFO, logging.DEBUG """
LOG_LEVEL = logging.INFO
""" Directory to which the PNG files are written - Will be created but ensure Apache has rights """
#HTML_DIR = '/home/pi/n1mm_view/html'
""" If True, then this is headless and only creates the PNG files """
HTML_ONLY = False
""" Height and Width of image files written to disk """
#PNG_HEIGHT = 1824
#PNG_WIDTH = 984
""" If set, this command is run after creating the files (used to rsync PNG files to remote web server)
POST_FILE_COMMAND = 'rsync -avz <HTML_DIR from above/*> <user@server>/<remote dir>'

