#!/usr/bin/python3

"""
this file is a rewrite of config.py to implement a configParser to keep the config in n1mm_view.ini
"""

__author__ = 'Tom Schaefer NY4I'
__copyright__ = 'Copyright 2024 Thomas M. Schaefer'
__license__ = 'Simplified BSD'


import configparser
import logging
import datetime
import os
import time

# Note LOG_FORMATS is here rather than constants.py to avoid a circular import
LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(module)s::%(funcName)s] %(message)s'



BASE_CONFIG_NAME = 'n1mm_view.ini'
CONFIG_NAMES = [ os.path.dirname(__file__) + '/' + BASE_CONFIG_NAME
                ,os.path.expanduser('~/' + BASE_CONFIG_NAME)
                ,os.path.expanduser('~/.config/' + BASE_CONFIG_NAME)                             
               ]
               
# Setup logging. This is the first occurrence so this is the only place basicConfig is called
logging.basicConfig( format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S'
                    ,level=logging.DEBUG # Set to DEBUG so we get all until we grab the value from the config file. THis allows config.py to log before we read the log level
                   )
logging.Formatter.converter = time.gmtime                   
class Singleton(type):
    def __init__(self, name, bases, mmbs):
        super(Singleton, self).__init__(name, bases, mmbs)
        self._instance = super(Singleton, self).__call__()

    def __call__(self, *args, **kw):
        return self._instance

class Config(metaclass = Singleton):
        
    def __init__(self, *args, **kw):
        
        cfg = configparser.ConfigParser()
        # Find and read ini file
        readCFGName = cfg.read(CONFIG_NAMES)
        # Check if there was just one config file found or none at all - Error in both cases so exit
        n = len(readCFGName) # Number of config files found
        if n > 1:
           print ('ConfigParser found more than one config file named %s' % (BASE_CONFIG_NAME))
           for s in readCFGName:
              print ('     Found %s' % (s))
           print ('Please use ONLY ONE file named %s in one of the following locations:' % (BASE_CONFIG_NAME))
           for s in CONFIG_NAMES:
              print ('     %s' % (s))   
           exit ()
        elif n == 0:
           print ('ConfigParser cannot find a config file named %s' % (BASE_CONFIG_NAME))
           print ('Please create ONLY ONE config file named %s in one of the following locations:' % (BASE_CONFIG_NAME))
           for s in CONFIG_NAMES:
              print ('     %s' % (s))   
           exit ()
        
        
       
        # Get logging level set first for subsequent logging...
        self.LOG_LEVEL = cfg.get('GLOBAL','LOG_LEVEL',fallback='ERROR')
        logging.info('Setting log level to %s' % (self.LOG_LEVEL))
        
        # Note that basicConfig is called again since n1mm_view uses the class methods in logging. 
        # While there is a setLevel to dynamically set the level, it is not a class function. 
        # So you have to call basicConfig again with the force parameter True to override the existing one.
        # If rather than call the class function, logging was instantiated as logger (accessible to all) then it could just use setLevel, but that is a bigger refactor.
        
        logging.basicConfig( format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S'
                    ,level=self.LOG_LEVEL 
                    ,force = True
                   )
        
        logging.info ('Reading config file @ %s' % (readCFGName))
        
        self.DATABASE_FILENAME = cfg.get('GLOBAL','DATABASE_FILENAME',fallback='n1mm_view.db')
        logging.info ('Using database file %s' % (self.DATABASE_FILENAME))
        
        self.LOGO_FILENAME = cfg.get('GLOBAL','LOGO_FILENAME',fallback='logo.png')
        if not os.path.exists(self.LOGO_FILENAME):
           logging.error('Logo file %s does not exist' % (self.LOGO_FILENAME))
        else:
           logging.info ('Using logo file %s' % (self.LOGO_FILENAME))
           
        self.EVENT_NAME = cfg.get('EVENT INFO','NAME')
        
        dt = cfg.get('EVENT INFO','START_TIME')
        try:
           self.EVENT_START_TIME = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
           logging.exception('*** INVALID START_TIME *** Value for START_TIME (%s) is not valid' % (dt))
           exit()
        
        dt = cfg.get('EVENT INFO','END_TIME')
        try:
           self.EVENT_END_TIME = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
           logging.exception('*** INVALID END_TIME *** Value for END_TIME (%s) is not valid' % (dt))
           exit()
              
        self.N1MM_BROADCAST_PORT = cfg.getint('N1MM INFO','BROADCAST_PORT',fallback=12060)
        logging.info ('Listening on UDP port %d' % (self.N1MM_BROADCAST_PORT))
        self.N1MM_BROADCAST_ADDRESS = cfg.get('N1MM INFO','BROADCAST_ADDRESS')
        self.N1MM_LOG_FILE_NAME = cfg.get('N1MM INFO','LOG_FILE_NAME')
        
        self.QTH_LATITUDE = cfg.getfloat('EVENT INFO','QTH_LATITUDE')
        self.QTH_LONGITUDE = cfg.getfloat('EVENT INFO','QTH_LONGITUDE')
        self.DISPLAY_DWELL_TIME = cfg.getint('GLOBAL','DISPLAY_DWELL_TIME',fallback=6)
        self.DATA_DWELL_TIME = cfg.getint('GLOBAL','DATA_DWELL_TIME',fallback=60)
        self.HEADLESS_DWELL_TIME = cfg.getint('GLOBAL','HEADLESS_DWELL_TIME',fallback=180)
        self.SKIP_TIMESTAMP_CHECK = cfg.getboolean('DEBUG','SKIP_TIMESTAMP_CHECK',fallback=False)
        
        
        
        self.IMAGE_DIR = cfg.get('HEADLESS INFO','IMAGE_DIR',fallback='/mnt/ramdisk/n1mm_view/html')
        self.HEADLESS = cfg.getboolean('HEADLESS INFO','HEADLESS',fallback = False) #False
        self.POST_FILE_COMMAND = cfg.get('HEADLESS INFO','POST_FILE_COMMAND', fallback=None)
        self.VIEW_FONT = cfg.getint('FONT INFO','VIEW_FONT',fallback=64)
        self.BIGGER_FONT = cfg.getint('FONT INFO','BIGGER_FONT',fallback=180)
