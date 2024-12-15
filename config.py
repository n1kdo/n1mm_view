#!/usr/bin/python3

import configparser
import logging
import datetime

class Config:
    def __init__(self, filename='config.ini'):
        # read ini file 
        # parse into properties of this class
        self.DATABASE_FILENAME = 'n1mm_view.WFD2025.db'
        self.EVENT_NAME = 'CARS/SPARC/UPARC Winter Field Day'
        self.EVENT_START_TIME = datetime.datetime.strptime('2025-01-25 15:00:00', '%Y-%m-%d %H:%M:%S')
        self.EVENT_END_TIME = datetime.datetime.strptime('2025-01-26 20:59:59', '%Y-%m-%d %H:%M:%S')
        self.N1MM_BROADCAST_PORT = 12060
        self.N1MM_BROADCAST_ADDRESS = '192.168.1.255'
        self.N1MM_LOG_FILE_NAME = 'FD2024-N4N.s3db'
        self.QTH_LATITUDE = 27.9837941202094249
        self.QTH_LONGITUDE = -82.74670114956339
        self.DISPLAY_DWELL_TIME = 6
        self.DATA_DWELL_TIME = 60
        self.LOG_LEVEL = logging.DEBUG
        self.IMAGE_DIR = None  #  '/mnt/ramdisk/n1mm_view/html'
        self.HEADLESS = False
        self.POST_FILE_COMMAND = 'rsync -avz /mnt/ramdisk/n1mm_view/html/* sparc:www/n1mm_view/html'
        self.VIEW_FONT = 64
        self.BIGGER_FONT = 180







"""
this file contains configuration values for n1mm_view.
This should be the only thing you would need to customize.
"""
# import datetime
# import logging
# 
# """ name of database file """
# DATABASE_FILENAME = 'n1mm_view.db'
# """ Name of the event/contest """
# EVENT_NAME = 'N4N Field Day'
# """ start time of the event/contest in YYYY-MM-DD hh:mm:ss format """
# 
# EVENT_START_TIME = datetime.datetime.strptime('2024-06-22 18:00:00', '%Y-%m-%d %H:%M:%S')
# """ end time of the event/contest """
# EVENT_END_TIME = datetime.datetime.strptime('2024-06-23 17:59:59', '%Y-%m-%d %H:%M:%S')
# """ port number used by N1MM+ for UDP broadcasts This matches the port you set in N1MM Configurator UDP logging """
# N1MM_BROADCAST_PORT = 12060
# """ 
# broadcast IP address, used by log re-player. 
# This could be the IP of the N1MM master, or just the last address in the network segment 
# """
# N1MM_BROADCAST_ADDRESS = '192.168.1.255'
# """ n1mm+ log file name used by replayer """
# N1MM_LOG_FILE_NAME = 'FD2024-N4N.s3db'
# """ QTH here is the location of your event. We mark this location with a red dot when we generate the map views."""
# """ QTH Latitude """
# QTH_LATITUDE = 34.0109629
# """ QTH Longitude """
# QTH_LONGITUDE = -84.4616047
# """ number of seconds before automatic display change to the next screen """
# DISPLAY_DWELL_TIME = 6
# """
# number of seconds before automatic info recalculation from database. Too low makes the Pi work harder.
# Too high makes a lag in viewing your results.
# """
# DATA_DWELL_TIME = 60
# """ log level for apps -- one of logging.WARN, logging.INFO, logging.DEBUG """
# LOG_LEVEL = logging.DEBUG
# #
# """images directory, or None if not writing image files"""
# IMAGE_DIR = None  #  '/mnt/ramdisk/n1mm_view/html'
# 
# """ set HEADLESS True to not open graphics window. This is for using only the Apache option."""
# HEADLESS = False
# 
# # This should match the directory above we want to send from the directory to which we write.
# POST_FILE_COMMAND = 'rsync -avz /mnt/ramdisk/n1mm_view/html/* sparc:www/n1mm_view/html'
# 
# """ Font Sizes """
# # If font seems too big, try 60 for VIEW_FONT and 100 for BIGGER_FONT
# VIEW_FONT = 64
# BIGGER_FONT = 180
