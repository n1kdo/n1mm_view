#!/usr/bin/python3

import configparser
import logging
import datetime

class Singleton(type):
    def __init__(self, name, bases, mmbs):
        super(Singleton, self).__init__(name, bases, mmbs)
        self._instance = super(Singleton, self).__call__()

    def __call__(self, *args, **kw):
        return self._instance

class Config(metaclass = Singleton):
        
    def __init__(self, *args, **kw):
    #def __init__(self, filename='~/.config/n1mm_view.ini'):
        # read ini file
        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        print ('*******Config__init__ running...') 
        # parse into properties of this class
        self.DATABASE_FILENAME = cfg.get('GLOBAL','DATABASE_FILENAME',fallback='n1mm_view.db')
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
        self.N1MM_BROADCAST_ADDRESS = cfg.get('N1MM INFO','BROADCAST_ADDRESS')
        self.N1MM_LOG_FILE_NAME = cfg.get('N1MM INFO','LOG_FILE_NAME')
        
        self.QTH_LATITUDE = cfg.getfloat('EVENT INFO','QTH_LATITUDE')
        self.QTH_LONGITUDE = cfg.getfloat('EVENT INFO','QTH_LONGITUDE')
        self.DISPLAY_DWELL_TIME = cfg.getint('GLOBAL','DISPLAY_DWELL_TIME',fallback=6)
        self.DATA_DWELL_TIME = cfg.getint('GLOBAL','DATA_DWELL_TIME',fallback=60)
        self.LOG_LEVEL = cfg.get('GLOBAL','LOG_LEVEL',fallback='ERROR')
        self.IMAGE_DIR = cfg.get('HEADLESS INFO','IMAGE_DIR',fallback='/mnt/ramdisk/n1mm_view/html')
        self.HEADLESS = cfg.getboolean('HEADLESS INFO','HEADLESS',fallback = False) #False
        self.POST_FILE_COMMAND = cfg.get('HEADLESS INFO','POST_FILE_COMMAND', fallback=None)
        self.VIEW_FONT = cfg.getint('FONT INFO','VIEW_FONT',fallback=64)
        self.BIGGER_FONT = cfg.getint('FONT INFO','BIGGER_FONT',fallback=180)
