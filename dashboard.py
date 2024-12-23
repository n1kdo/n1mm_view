#!/usr/bin/python3
"""
n1mm_view dashboard
This program displays QSO statistics collected by the collector.
"""

from datetime import datetime
import logging
import os
import gc
import multiprocessing
import pygame
import sqlite3
import sys
import time

from config import Config
import dataaccess
import graphics

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

config = Config()

LOGO_IMAGE_INDEX = 0
QSO_COUNTS_TABLE_INDEX = 1
QSO_RATES_TABLE_INDEX = 2
QSO_OPERATORS_PIE_INDEX = 3
QSO_OPERATORS_TABLE_INDEX = 4
QSO_STATIONS_PIE_INDEX = 5
QSO_BANDS_PIE_INDEX = 6
QSO_MODES_PIE_INDEX = 7
QSO_CLASSES_PIE_INDEX = 8
QSO_RATE_CHART_IMAGE_INDEX = 9
SECTIONS_WORKED_MAP_INDEX = 10
IMAGE_COUNT = 11

IMAGE_MESSAGE = 1
CRAWL_MESSAGE = 2

IMAGE_FORMAT = 'RGB'
SAVE_PNG = False

def load_data(size, q, last_qso_timestamp):
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
    qso_classes = []

    db = None
    data_updated = False

    try:
        logging.debug('connecting to database')
        db = sqlite3.connect(config.DATABASE_FILENAME)
        cursor = db.cursor()
        logging.debug('database connected')

        # get timestamp from the last record in the database
        last_qso_time, message = dataaccess.get_last_qso(cursor)

        logging.debug('old_timestamp = %d, timestamp = %d', last_qso_timestamp, last_qso_time)
        if last_qso_time != last_qso_timestamp:
            logging.debug('data updated!')
            data_updated = True
            q.put((CRAWL_MESSAGE, 3, message))

            # load qso_operators
            qso_operators = dataaccess.get_operators_by_qsos(cursor)

            # load qso_stations -- maybe useless chartjunk
            qso_stations = dataaccess.get_station_qsos(cursor)

            # get something else.
            qso_band_modes = dataaccess.get_qso_band_modes(cursor)

            # load qso exchange data: what class are the other stations?
            qso_classes = dataaccess.get_qso_classes(cursor)

            # load QSOs per Hour by Operator
            operator_qso_rates = dataaccess.get_qsos_per_hour_per_operator(cursor, last_qso_time)

            # load QSO rates per Hour by Band
            qsos_per_hour, qsos_per_band = dataaccess.get_qsos_per_hour_per_band(cursor)

        # load QSOs by Section
        # This has to be done even if no new QSO to advance gray line and since the map is always drawn.
        qsos_by_section = dataaccess.get_qsos_by_section(cursor)

        q.put((CRAWL_MESSAGE, 0, ''))

        logging.debug('load data done')
    except sqlite3.OperationalError as error:
        if error.args is not None and error.args[0].startswith('no such table'):
            q.put((CRAWL_MESSAGE, 0, 'database not ready', graphics.YELLOW, graphics.RED))
        else:
            logging.error(error.args[0])
            logging.exception(error)
            q.put((CRAWL_MESSAGE, 0, 'database read error', graphics.YELLOW, graphics.RED))
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
            enqueue_image(q, QSO_COUNTS_TABLE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_rates_table(size, operator_qso_rates)
            enqueue_image(q, QSO_RATES_TABLE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_operators_graph(size, qso_operators)
            enqueue_image(q, QSO_OPERATORS_PIE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_operators_table(size, qso_operators)
            enqueue_image(q, QSO_OPERATORS_TABLE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_stations_graph(size, qso_stations)
            enqueue_image(q, QSO_STATIONS_PIE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_bands_graph(size, qso_band_modes)
            enqueue_image(q, QSO_BANDS_PIE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_modes_graph(size, qso_band_modes)
            enqueue_image(q, QSO_MODES_PIE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_classes_graph(size, qso_classes)
            enqueue_image(q, QSO_CLASSES_PIE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)
        try:
            image_data, image_size = graphics.qso_rates_graph(size, qsos_per_hour)
            enqueue_image(q, QSO_RATE_CHART_IMAGE_INDEX, image_data, image_size)
        except Exception as e:
            logging.exception(e)

    try:
        image_data, image_size = graphics.draw_map(size, qsos_by_section)
        enqueue_image(q, SECTIONS_WORKED_MAP_INDEX, image_data, image_size)
        gc.collect()
    except Exception as e:
        logging.exception(e)

    return last_qso_time


def enqueue_image(q, image_id, image_data, size):
    if image_data is not None:
        q.put((IMAGE_MESSAGE, image_id, image_data, size))


def delta_time_to_string(delta_time):
    """
    return a string that represents delta time
    """
    seconds = delta_time.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days != 0:
        return '%d days, %02d:%02d:%02d' % (days, hours, minutes, seconds)
    else:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


def update_crawl_message(crawl_messages):
    crawl_messages.set_message(0, config.EVENT_NAME)
    crawl_messages.set_message_colors(0, graphics.BRIGHT_BLUE, graphics.BLACK)
    now = datetime.utcnow()
    crawl_messages.set_message(1, datetime.strftime(now, '%H:%M:%S'))
    if now < config.EVENT_START_TIME:
        delta = config.EVENT_START_TIME - now
        seconds = delta.total_seconds()
        bg = graphics.BLUE if seconds > 3600 else graphics.RED
        crawl_messages.set_message(2, '%s starts in %s' % (config.EVENT_NAME, delta_time_to_string(delta)))
        crawl_messages.set_message_colors(2, graphics.WHITE, bg)
    elif now < config.EVENT_END_TIME:
        delta = config.EVENT_END_TIME - now
        seconds = delta.total_seconds()
        fg = graphics.YELLOW if seconds > 3600 else graphics.ORANGE
        crawl_messages.set_message(2, '%s ends in %s' % (config.EVENT_NAME, delta_time_to_string(delta)))
        crawl_messages.set_message_colors(2, fg, graphics.BLACK)
    else:
        crawl_messages.set_message(2, '%s is over.' % config.EVENT_NAME)
        crawl_messages.set_message_colors(2, graphics.RED, graphics.BLACK)


class CrawlMessages:
    """
    class to manage a crawl of varied text messages on the bottom of the display
    """

    def __init__(self, screen, size):
        self.screen = screen
        self.size = size
        self.messages = [''] * 10
        self.message_colors = [(graphics.GREEN, graphics.BLACK)] * 10
        self.message_surfaces = None
        self.last_added_index = -1
        self.first_x = -1

    def set_message(self, index, message):
        if index >= 0 and index < len(self.messages):
            self.messages[index] = message

    def set_message_colors(self, index, fg, bg):
        if index >= 0 and index < len(self.messages):
            self.message_colors[index] = (fg, bg)

    def crawl_message(self):
        if self.message_surfaces is None:
            self.message_surfaces = [graphics.view_font.render(' ' + self.messages[0] + ' ', True,
                                                               self.message_colors[0][0],
                                                               self.message_colors[0][1])]
            self.first_x = self.size[0]
            self.last_added_index = 0

        self.first_x -= 2  # JEFF
        rect = self.message_surfaces[0].get_rect()
        if self.first_x + rect.width < 0:
            self.message_surfaces = self.message_surfaces[1:]
            self.first_x = 0
        x = self.first_x
        for surf in self.message_surfaces:
            rect = surf.get_rect()
            x = x + rect.width

        while x < self.size[0]:
            self.last_added_index += 1
            if self.last_added_index >= len(self.messages):
                self.last_added_index = 0
            if self.messages[self.last_added_index] != '':
                surf = graphics.view_font.render(' ' + self.messages[self.last_added_index] + ' ', True,
                                                 self.message_colors[self.last_added_index][0],
                                                 self.message_colors[self.last_added_index][1])
                rect = surf.get_rect()
                self.message_surfaces.append(surf)
                x += rect.width

        x = self.first_x
        for surf in self.message_surfaces:
            rect = surf.get_rect()
            rect.bottom = self.size[1] - 1
            rect.left = x
            self.screen.blit(surf, rect)
            x += rect.width
            if x >= self.size[0]:
                break


def update_charts(q, event, size):
    try:
        os.nice(10)
    except AttributeError:
        logging.warning("can't be nice to windows")
    q.put((CRAWL_MESSAGE, 4, 'Chart engine starting...'))
    last_qso_timestamp = 0
    q.put((CRAWL_MESSAGE, 4, ''))

    try:
        while not event.is_set():
            t0 = time.time()
            last_qso_timestamp = load_data(size, q, last_qso_timestamp) or 0
            t1 = time.time()
            delta = t1 - t0
            update_delay = config.DATA_DWELL_TIME - delta
            if update_delay < 0:
                update_delay = config.DATA_DWELL_TIME
            logging.debug('Next data update in %f seconds', update_delay)
            event.wait(update_delay)
    except Exception as e:
        logging.exception('Exception in update_charts', exc_info=e)
        q.put((CRAWL_MESSAGE, 4, 'Chart engine failed.', graphics.YELLOW, graphics.RED))


def change_image(screen, size, images, image_index, delta):
    while True:
        image_index += delta
        if image_index >= len(images):
            image_index = 0
        elif image_index < 0:
            image_index = len(images) - 1
        if images[image_index] is not None:
            break
    graphics.show_graph(screen, size, images[image_index])
    return image_index


def main():
    logging.info('dashboard startup')
    last_qso_timestamp = 0
    q = multiprocessing.Queue()

    process_event = multiprocessing.Event()

    images = [None] * IMAGE_COUNT
    try:
        screen, size = graphics.init_display()
    except Exception as e:
        logging.exception('Could not initialize display.', exc_info=e)
        sys.exit(1)

    display_size = (size[0], size[1] - graphics.view_font_height)

    logging.debug('display setup')

    images[LOGO_IMAGE_INDEX] = pygame.image.load(config.LOGO_FILENAME)
    crawl_messages = CrawlMessages(screen, size)
    update_crawl_message(crawl_messages)

    proc = multiprocessing.Process(name='image-updater', target=update_charts, args=(q, process_event, display_size))
    proc.start()

    try:
        image_index = LOGO_IMAGE_INDEX
        graphics.show_graph(screen, size, images[LOGO_IMAGE_INDEX])

        pygame.time.set_timer(pygame.USEREVENT, 1000)
        run = True
        paused = False

        display_update_timer = config.DISPLAY_DWELL_TIME
        clock = pygame.time.Clock()

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                elif event.type == pygame.USEREVENT:
                    display_update_timer -= 1
                    if display_update_timer < 1:
                        if paused:
                            graphics.show_graph(screen, size, images[image_index])
                        else:
                            image_index = change_image(screen, size, images, image_index, 1)
                        display_update_timer = config.DISPLAY_DWELL_TIME
                    update_crawl_message(crawl_messages)
                elif event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        logging.debug('Q key pressed')
                        run = False
                    elif event.key == pygame.K_n or event.key == 275 or event.key == pygame.K_RIGHT:
                        logging.debug('next key pressed')
                        image_index = change_image(screen, size, images, image_index, 1)
                        display_update_timer = config.DISPLAY_DWELL_TIME
                    elif event.key == pygame.K_p or event.key == 276 or event.key == pygame.K_LEFT:
                        logging.debug('prev key pressed')
                        image_index = change_image(screen, size, images, image_index, -1)
                        display_update_timer = config.DISPLAY_DWELL_TIME
                    elif event.key == 302 or event.key == pygame.K_SCROLLLOCK:
                        logging.debug('scroll lock key pressed')
                        if paused:
                            image_index = change_image(screen, size, images, image_index, 1)
                            display_update_timer = config.DISPLAY_DWELL_TIME
                        paused = not paused
                    else:
                        logging.debug('event key=%d', event.key)
                while not q.empty():
                    payload = q.get()
                    message_type = payload[0]
                    if message_type == IMAGE_MESSAGE:
                        n = payload[1]
                        image = payload[2]
                        image_size = payload[3]
                        images[n] = pygame.image.frombuffer(image, image_size, IMAGE_FORMAT)
                        logging.debug('received image %d', n)
                    elif message_type == CRAWL_MESSAGE:
                        n = payload[1]
                        message = payload[2]
                        fg = graphics.CYAN
                        bg = graphics.BLACK
                        if len(payload) > 3:
                            fg = payload[3]
                        if len(payload) > 4:
                            bg = payload[4]
                        crawl_messages.set_message(n, message)
                        crawl_messages.set_message_colors(n, fg, bg)

            crawl_messages.crawl_message()
            pygame.display.flip()

            clock.tick(60)

        pygame.time.set_timer(pygame.USEREVENT, 0)
    except Exception as e:
        logging.exception("Exception in main:", exc_info=e)

    pygame.display.quit()
    logging.debug('stopping update process')
    process_event.set()
    logging.debug('waiting for update process to stop...')
    proc.join(60)
    if proc.is_alive():
        logging.warning('chart engine did not exit upon request, killing.')
        proc.terminate()
    logging.debug('update thread has stopped.')
    logging.info('dashboard exit')


if __name__ == '__main__':
    main()
