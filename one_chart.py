#!/usr/bin/python3

"""
This script allows you to view ONE of the graphs relatively quickly, mostly for debugging the graph generators.
"""
import gc
import logging
import pygame
import sqlite3
import sys
import time

from config import Config
import dataaccess
import graphics

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019, 2025 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

config = Config()


def main():
    logging.info('dashboard startup')
    try:
        screen, size = graphics.init_display()
    except Exception as e:
        logging.exception('Could not initialize display.', exc_info=e)
        sys.exit(1)

    display_size = (size[0], size[1])

    logging.debug('display setup')

    qso_operators = []
    qso_stations = []
    qso_band_modes = []
    operator_qso_rates = []
    qsos_per_hour = []
    qsos_by_section = {}

    logging.debug('load data')
    db = None
    cursor = None
    try:
        logging.debug('connecting to database')
        db = sqlite3.connect(config.DATABASE_FILENAME)
        cursor = db.cursor()
        logging.debug('database connected')

        # get timestamp from the last record in the database
        last_qso_time, message = dataaccess.get_last_qso(cursor)

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

        # load qso exchange data: what class are the other stations?
        qso_classes = dataaccess.get_qso_classes(cursor)

        # load QSOs by Section
        qsos_by_section = dataaccess.get_qsos_by_section(cursor)

        logging.debug('load data done')
    except sqlite3.OperationalError as error:
        logging.exception(error)
        sys.exit(1)
    finally:
        if db is not None:
            logging.debug('Closing DB')
            cursor.close()
            db.close()
            db = None

    try:
        image_data, image_size = graphics.qso_summary_table(size, qso_band_modes)
        graphics.save_image(image_data, image_size, 'images/qso_summary_table.png')
        image_data, image_size = graphics.qso_rates_table(size, operator_qso_rates)
        graphics.save_image(image_data, image_size, 'images/qso_rates_table.png')
        image_data, image_size = graphics.qso_operators_graph(size, qso_operators)
        graphics.save_image(image_data, image_size, 'images/qso_operators_graph.png')
        image_data, image_size = graphics.qso_operators_table(size, qso_operators)
        graphics.save_image(image_data, image_size, 'images/qso_operators_table.png')
        image_data, image_size = graphics.qso_stations_graph(size, qso_stations)
        graphics.save_image(image_data, image_size, 'images/qso_stations_graph.png')
        image_data, image_size = graphics.qso_bands_graph(size, qso_band_modes)
        graphics.save_image(image_data, image_size, 'images/qso_bands_graph.png')
        image_data, image_size = graphics.qso_classes_graph(size, qso_classes)
        graphics.save_image(image_data, image_size, 'images/qso_classes_graph.png')
        image_data, image_size = graphics.qso_modes_graph(size, qso_band_modes)
        graphics.save_image(image_data, image_size, 'images/qso_modes_graph.png')
        image_data, image_size = graphics.qso_rates_graph(size, qsos_per_hour)
        graphics.save_image(image_data, image_size, 'images/qso_rates_graph.png')
        image = pygame.image.frombuffer(image_data, image_size, graphics.image_format)  # this is the image to SHOW on the screen
        image_data, image_size = graphics.draw_map(size, qsos_by_section)
        graphics.save_image(image_data, image_size, 'images/qsos_map.png')
        gc.collect()

        graphics.show_graph(screen, size, image)
        pygame.display.update()

        # wait for a Q key press
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        logging.debug('Q key pressed')
                        run = False
                    else:
                        logging.debug('event key=%d', event.key)

    except Exception as e:
        logging.exception("Exception in main:", exc_info=e)

    pygame.display.quit()
    logging.info('one_chart exit')


if __name__ == '__main__':
    main()
