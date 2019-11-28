#!/usr/bin/python
"""
n1mm_view collector
This program collects N1MM+ "Contact Info" broadcasts and saves data from the broadcasts
in database tables.
"""

import logging
import sqlite3
import time
from hashlib import md5
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from xml.dom.minidom import parseString

import config
import dataaccess

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

BROADCAST_BUF_SIZE = 2048

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.LOG_LEVEL)
logging.Formatter.converter = time.gmtime


class Operators:
    operators = {}
    db = None
    cursor = None

    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor
        # load operators
        self.cursor.execute('SELECT id, name FROM operator;')
        for row in self.cursor:
            self.operators[row[1]] = row[0]

    def lookup_operator_id(self, operator):
        """
        lookup the operator id for the supplied operator text.
        if the operator is not found, create it.
        """
        oid = self.operators.get(operator)
        if oid is None:
            self.cursor.execute("insert into operator (name) values (?);", (operator,))
            self.db.commit()
            oid = self.cursor.lastrowid
            self.operators[operator] = oid
        return oid


class Stations:
    stations = {}
    db = None
    cursor = None

    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor
        self.cursor.execute('SELECT id, name FROM station;')
        for row in self.cursor:
            self.stations[row[1]] = row[0]

    def lookup_station_id(self, station):
        sid = self.stations.get(station)
        if sid is None:
            self.cursor.execute("insert into station (name) values (?);", (station,))
            self.db.commit()
            sid = self.cursor.lastrowid
            self.stations[station] = sid
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
    except Exception as e:
        return ''


def process_message(db, cursor, operators, stations, data, seen):
    """
    Process a N1MM+ contactinfo message
    """
    #  logging.debug(data)
    dom = parseString(data)
    if dom.getElementsByTagName("contactinfo").length == 1 or dom.getElementsByTagName("contactreplace").length == 1:
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
        station_name = get_from_dom(dom, "StationName")
        if station_name == '':
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

        dataaccess.record_contact(db, cursor, operators, stations,
                                  timestamp, mycall, band, mode, operator, station,
                                  rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                                  exchange, section, comment)
    elif dom.getElementsByTagName("RadioInfo").length == 1:
        logging.debug("Received radioInfo message")
    elif dom.getElementsByTagName("contactdelete").length == 1:
        qso_timestamp = get_from_dom(dom, "timestamp")
        callsign = get_from_dom(dom, "call")
        station_name = get_from_dom(dom, "StationName")
        station = station_name
        #  convert qso_timestamp to datetime object
        timestamp = convert_timestamp(qso_timestamp)
        dataaccess.delete_contact(db, cursor, timestamp, station, callsign)
    elif dom.getElementsByTagName("dynamicresults").length == 1:
        logging.debug("Received Score message")
    else:
        logging.warning('unknown message received, ignoring.')
        logging.debug(data)


def listener(db, cursor):
    """
    this is the UDP listener, the main loop.
    """
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        s.bind(('', config.N1MM_BROADCAST_PORT))
    except:
        logging.critical('Error connecting to the UDP stream.')
        return

    operators = Operators(db, cursor)
    stations = Stations(db, cursor)

    seen = set()
    run = True
    while run:
        try:
            udp_data = s.recv(BROADCAST_BUF_SIZE)
            process_message(db, cursor, operators, stations, udp_data, seen)

        except KeyboardInterrupt:
            logging.info('Keyboard interrupt, shutting down...')
            s.close()
            run = False


def main():
    logging.info('Collector started...')
    db = sqlite3.connect(config.DATABASE_FILENAME)
    cursor = db.cursor()
    dataaccess.create_tables(db, cursor)
    listener(db, cursor)
    db.close()

    logging.info('Collector done...')


if __name__ == '__main__':
    main()
