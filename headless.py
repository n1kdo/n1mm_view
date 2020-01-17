#!/usr/bin/python3
"""
n1mm_view_headless
create images from contest data
non-interactive version.  This creates files on the disk and updates them periodically.
"""

import gc
import logging
import os
import re
import sqlite3
import time

import config
import dataaccess
import graphics

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2017 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.LOG_LEVEL)
logging.Formatter.converter = time.gmtime

      

def makePNGTitle(image_dir, title):
    return ''.join([image_dir, '/', re.sub('[^\w\-_]', '_', title), '.png'])


def create_images(size, image_dir, last_qso_timestamp):
    """
    load data from the database tables
    """
    logging.debug('load data')

    qso_operators = []
    qso_stations = []
    qso_band_modes = []
    operator_qso_rates = []
    qsos_per_hour = []
    qsos_by_section = {}

    db = None
    data_updated = False

    try:
        logging.debug('connecting to database')
        db = sqlite3.connect(config.DATABASE_FILENAME)
        cursor = db.cursor()
        logging.debug('database connected')

        # Handy routine to dump the database to help debug strange problems
        #if logging.getLogger().isEnabledFor(logging.DEBUG):
        #   cursor.execute('SELECT timestamp, callsign, section, operator_id, operator.name FROM qso_log join operator WHERE operator.id = operator_id')
        #  for row in cursor: 
        #      logging.debug('QSO: %s\t%s\t%s\t%s\t%s' % (row[0], row[1], row[2], row[3], row[4])) 
              
        # get timestamp from the last record in the database
        last_qso_time, message = dataaccess.get_last_qso(cursor)

        logging.debug('old_timestamp = %d, timestamp = %d', last_qso_timestamp, last_qso_time)
        if last_qso_time != last_qso_timestamp:
            # last_qso_time is passed as the result and updated in call to this function.
            logging.debug('data updated!')
            data_updated = True

            # load qso_operators
            qso_operators = dataaccess.get_operators_by_qsos(cursor)

            # load qso_stations -- maybe useless chartjunk
            qso_stations = dataaccess.get_station_qsos(cursor)

            # get something else.
            qso_band_modes = dataaccess.get_qso_band_modes(cursor)

            # load QSOs per Hour by Operator
            operator_qso_rates = dataaccess.get_qsos_per_hour_per_operator(cursor, last_qso_time)

            # load QSO rates per Hour by Band
            qsos_per_hour, qsos_per_band = dataaccess.get_qsos_per_hour_per_band(cursor)

        # load QSOs by Section
        qsos_by_section = dataaccess.get_qsos_by_section(cursor)

        logging.debug('load data done')
    except sqlite3.OperationalError as error:
        logging.exception(error)
        return
    finally:
        if db is not None:
            logging.debug('Closing DB')
            cursor.close()
            db.close()
            db = None

    if data_updated:
        try:
            image_data, image_size = graphics.qso_summary_table(size, qso_band_modes)
            filename = makePNGTitle(image_dir, 'qso_summary_table')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_rates_table(size, operator_qso_rates)
            filename = makePNGTitle(image_dir, 'qso_rates_table')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_operators_graph(size, qso_operators)
            filename = makePNGTitle(image_dir, 'qso_operators_graph')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_operators_table(size, qso_operators)
            filename = makePNGTitle(image_dir, 'qso_operators_table')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_stations_graph(size, qso_stations)
            filename = makePNGTitle(image_dir, 'qso_stations_graph')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_bands_graph(size, qso_band_modes)
            filename = makePNGTitle(image_dir, 'qso_bands_graph')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_modes_graph(size, qso_band_modes)
            filename = makePNGTitle(image_dir, 'qso_modes_graph')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_rates_chart(size, qsos_per_hour)
            filename = makePNGTitle(image_dir, 'qso_rates_chart')
            graphics.save_image(image_data, image_size, filename)
        except Exception as e:
            logging.exception(e)

    # map gets updated every time so grey line moves
    try:
        # There is a memory leak in the next code -- is there?
        image_data, image_size = graphics.draw_map(size, qsos_by_section)
        filename = makePNGTitle(image_dir, 'sections_worked_map')
        graphics.save_image(image_data, image_size, filename)
        gc.collect()

    except Exception as e:
        logging.exception(e)

    #if data_updated:   # Data is always updated since the sections map is always updated. Let rsync command handle this.
    if config.POST_FILE_COMMAND is not None:
       os.system(config.POST_FILE_COMMAND)

    return last_qso_time


def main():
    logging.info('headless startup...')
    size = (1280, 1024)
    image_dir = config.IMAGE_DIR
    logging.debug("Checking for IMAGE_DIR")
    logging.info("IMAGE_DIR set to %s - checking if exists" % config.IMAGE_DIR)
    # Check if the dir given exists and create if necessary
    if not os.path.exists(config.IMAGE_DIR):
       logging.error("%s did not exist - creating..." % config.IMAGE_DIR)
       os.makedirs(config.IMAGE_DIR)
    if not os.path.exists(config.IMAGE_DIR):
       sys.exit('Image %s directory could not be created' % config.IMAGE_DIR)
       
    logging.info('creating world...')
#    base_map = graphics.create_map()

    run = True
    last_qso_timestamp = '' 
    logging.info('headless running...')
    while run:
        try:
            last_qso_timestamp = create_images(size, image_dir, last_qso_timestamp)
            time.sleep(config.DATA_DWELL_TIME)
        except KeyboardInterrupt:
            logging.info('Keyboard interrupt, shutting down...')
            run = False

    logging.info('headless shutdown...')


if __name__ == '__main__':
    main()
