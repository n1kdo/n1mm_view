#!/usr/bin/python
"""
n1mm_view collector
This program collects N1MM+ "Contact Info" broadcasts and saves data from the broadcasts
in database tables.
"""

import calendar
import logging
import sqlite3
import time
from hashlib import md5
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from xml.dom.minidom import parseString

from n1mm_view_constants import *
from n1mm_view_config import *

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

BROADCAST_BUF_SIZE = 2048

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.Formatter.converter = time.gmtime

# globals.  fix this shit.
operators = {}
stations = {}


def create_tables(db, cursor):
    """
    set up the database tables
    """
    cursor.execute('CREATE TABLE IF NOT EXISTS operator\n'
                   '    (id INTEGER PRIMARY KEY NOT NULL, \n'
                   '    name char(12) NOT NULL);')
    cursor.execute('CREATE INDEX IF NOT EXISTS operator_name ON operator(name);')

    cursor.execute('CREATE TABLE IF NOT EXISTS station\n'
                   '    (id INTEGER PRIMARY KEY NOT NULL, \n'
                   '    name char(12) NOT NULL);')
    cursor.execute('CREATE INDEX IF NOT EXISTS station_name ON station(name);')

    cursor.execute('CREATE TABLE IF NOT EXISTS qso_log\n'
                   #'    (id INTEGER PRIMARY KEY NOT NULL,\n'
                   '     (timestamp INTEGER NOT NULL,\n'
                   '     mycall char(12) NOT NULL,\n'
                   '     band_id INTEGER NOT NULL,\n'
                   '     mode_id INTEGER NOT NULL,\n'
                   '     operator_id INTEGER NOT NULL,\n'
                   '     station_id INTEGER NOT NULL,\n'
                   '     rx_freq INTEGER NOT NULL,\n'
                   '     tx_freq INTEGER NOT NULL,\n'
                   '     callsign char(12) NOT NULL,\n'
                   '     rst_sent char(3),\n'
                   '     rst_recv char(3),\n'
                   '     exchange char(4),\n'
                   '     section char(4),\n'
                   '     comment TEXT);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_band_id ON qso_log(band_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_mode_id ON qso_log(mode_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_operator_id ON qso_log(operator_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_station_id ON qso_log(station_id);')
    db.commit()


def load_data(db, cursor):
    """
    load data from the database tables
    """
    global operators, stations

    # load operators
    cursor.execute('SELECT id, name FROM operator;')
    for row in cursor:
        operators[row[1]] = row[0]

    # load stations
    cursor.execute('SELECT id, name FROM station;')
    for row in cursor:
        stations[row[1]] = row[0]


def add_operator(db, cursor, operator):
    """
    add an operator to the operator table, and to the operator dict
    """
    global operators
    cursor.execute("insert into operator (name) values (?);", (operator,))
    db.commit()
    oid = cursor.lastrowid
    operators[operator] = oid
    return oid


def add_station(db, cursor, station):
    """
    add an station to the station table, and to the station dict
    """
    global stations
    cursor.execute("insert into station (name) values (?);", (station,))
    db.commit()
    sid = cursor.lastrowid
    stations[station] = sid
    return sid


def checksum(data):
    """
    generate a unique ID for each QSO.
    this is using md5 rather than crc32 because it is hoped that md5 will have less collisions.
    """
    # return int(md5(data).hexdigest()[:16], 16)  # 1,000,000 iterations takes 35.506 sec  # 32 bit
    return int(md5(data).hexdigest(), 16)  # 1,000,000 iterations takes 35.506 sec
    # return binascii.crc32(data) # 1,000,000 iterations takes takes 34.630 sec


def convert_timestamp(s):
    """
    convert the N1MM+ timestamp into a python time object.
    """
    return time.strptime(s, '%Y-%m-%d %H:%M:%S')


def listener(db, cursor):
    """
    this is the UDP listener, the main loop.
    """
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        s.bind(('', N1MM_BROADCAST_PORT))
    except:
        logging.critical('Error connecting to the UDP stream.')
        return
    seen = set()
    run = True
    while run:
        try:
            udp_data = s.recv(BROADCAST_BUF_SIZE)
            process_message(db, cursor, udp_data, seen)

        except KeyboardInterrupt:
            logging.info('Keyboard interrupt, shutting down...')
            s.close()
            run = False


def get_from_dom(dom, name):
    """
    safely extract a field from a dom.
    return empty string on any failures.
    """
    try:
        fc = dom.getElementsByTagName(name)[0].firstChild
        if fc is None:
            return ''
        else:
            return fc.nodeValue
    except Exception, e:
        logging.exception('could not parse %s from dom.' % name, e)
        return ''


def lookup_band_id(band):
    """
    lookup the band ID number for the supplied band text
    """
    bid = BANDS.get(band)
    if bid is None:
        logging.warn('unknown band %s' % band)
        return 0
    return bid


def lookup_mode_id(mode):
    """
    lookup the mode id for the supplied mode text
    """
    mid = MODES.get(mode)
    if mid is None:
        return 0
    return mid


def lookup_operator_id(db, cursor, operator):
    """
    lookup the operator id for the supplied operator text.
    if the operator is not found, create it.
    """
    global operators
    oid = operators.get(operator)
    if oid is None:
        oid = add_operator(db, cursor, operator)
    return oid


def lookup_station_id(db, cursor, station):
    """
    lookup the station id for the supplied station text.
    if the station is not found, create it.
    """
    global stations
    sid = stations.get(station)
    if sid is None:
        sid = add_station(db, cursor, station)
    return sid


def record_contact(db, cursor,
                   timestamp, mycall, band, mode, operator, station,
                   rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                   exchange, section, comment):
    """
    record the results of a contact_message
    """

    band_id = lookup_band_id(band)
    mode_id = lookup_mode_id(mode)
    operator_id = lookup_operator_id(db, cursor, operator)
    station_id = lookup_station_id(db, cursor, station)

    logging.info('QSO: %s %6s %4s %-6s %-12s %-12s %10d %10d %-6s %3s %3s %3s %-3s %-3s' % (
        time.strftime('%Y-%m-%d %H:%M:%S', timestamp),
        mycall, band,
        mode, operator,
        station, rx_freq, tx_freq, callsign, rst_sent,
        rst_recv, exchange, section, comment))

    cursor.execute(
        'insert into qso_log \n'
        '    (timestamp, mycall, band_id, mode_id, operator_id, station_id , rx_freq, tx_freq, \n'
        '     callsign, rst_sent, rst_recv, exchange, section, comment)\n'
        '    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (calendar.timegm(timestamp), mycall, band_id, mode_id, operator_id, station_id, rx_freq, tx_freq,
         callsign, rst_sent, rst_recv, exchange, section, comment))

    db.commit()


def process_message(db, cursor, data, seen):
    """
    Process a N1MM+ contactinfo message
    """

    dom = parseString(data)
    if dom.getElementsByTagName("contactinfo").length == 1:
        checksum_value = checksum(data)
        if checksum_value in seen:
            logging.debug('duplicate message')
            return
        seen.add(checksum_value)
        qso_timestamp = get_from_dom(dom, "timestamp")
        mycall = get_from_dom(dom, "mycall")
        band = get_from_dom(dom, "band")
        mode = get_from_dom(dom, "mode")
        operator = get_from_dom(dom, "operator")
        station_name = get_from_dom(dom, "NetBiosName")
        station = station_name
        rx_freq = int(get_from_dom(dom, "rxfreq")) * 10  # convert to Hz
        tx_freq = int(get_from_dom(dom, "txfreq")) * 10
        callsign = get_from_dom(dom, "call")
        rst_sent = get_from_dom(dom, "snt")
        rst_recv = get_from_dom(dom, "rcv")
        exchange = get_from_dom(dom, "exchange1")
        section = get_from_dom(dom, "section")
        comment = get_from_dom(dom, "comment")

        # convert qso_timestamp to datetime object
        timestamp = convert_timestamp(qso_timestamp)

        record_contact(db, cursor,
                       timestamp, mycall, band, mode, operator, station,
                       rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                       exchange, section, comment)
    else:
        logging.warn('unknown message received, ignoring.')


def main():
    logging.info('Collector started...')
    db = sqlite3.connect(DATABASE_FILENAME)
    cursor = db.cursor()
    create_tables(db, cursor)
    load_data(db, cursor)
    listener(db, cursor)
    db.close()

    logging.info('Collector done...')


if __name__ == '__main__':
    main()
