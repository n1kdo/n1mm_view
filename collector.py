#!/usr/bin/python3
"""
n1mm_view collector
This program collects N1MM+ "Contact Info" broadcasts and saves data from the broadcasts
in database tables.
"""

import hashlib
import logging
import multiprocessing
import socket
import sqlite3
import time
import xml.parsers.expat

import config
import dataaccess

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

BROADCAST_BUF_SIZE = 2048

run = True

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
            self.cursor.execute('insert into station (name) values (?);', (station,))
            self.db.commit()
            sid = self.cursor.lastrowid
            self.stations[station] = sid
        return sid


class N1mmMessageParser:
    """
    this is a cheap and dirty class to parse N1MM+ broadcast messages.
    It accepts the message and returns a dict, keyed by the element name.
    This is unsuitable for any other purpose, since it throws away the
    outer _contactinfo_ (or whatever) element -- instead it returns the name of
    the outer element as the value of the __messagetype__ key.
    OTOH, hopefully it is faster than using the DOM-based minidom.parse
    """
    result = {}
    lastElementName = None
    lastElementValue = None

    def __init__(self):
        self.parser = None
        self.result = None
        self.lastElementValue = None
        self.lastElementName = None

    def parse(self, data):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.char_data
        self.lastElementValue = None
        self.lastElementName = None

        self.result = {}
        self.parser.Parse(data)
        return self.result

    def start_element(self, name, attrs):
        if self.lastElementName is not None:
            self.result['__messagetype__'] = self.lastElementName
        self.lastElementName = name
        self.lastElementValue = None

    def end_element(self, name):
        if self.lastElementName is not None and self.lastElementValue is not None:
            self.result[self.lastElementName] = self.lastElementValue
        self.lastElementName = None
        self.lastElementValue = None

    def char_data(self, data):
        self.lastElementValue = data


def compress_message(msg):
    new_msg = bytearray()
    state = 0
    count = 0
    for byte in msg:
        if state == 0 and byte == 10:
            state = 1
            continue
        elif state == 1 and byte == 32:
            continue
        else:
            state = 0
            new_msg.append(byte)
            count += 1
    return new_msg


def checksum(data):
    """
    generate a unique ID for each QSO.
    this is using md5 rather than crc32 because it is hoped that md5 will have less collisions.
    """
    hval = data['timestamp'] + data['StationName'] + data['contestnr'] + data['call']
    return int(hashlib.md5(hval.encode()).hexdigest(), 16)


def convert_timestamp(s):
    """
    convert the N1MM+ timestamp into a python time object.
    """
    return time.strptime(s, '%Y-%m-%d %H:%M:%S')


def process_message(parser, db, cursor, operators, stations, message, seen):
    """
    Process a N1MM+ contactinfo message
    """
    bInsert = False
    message = compress_message(message)
    #logging.debug(message)
    data = parser.parse(message)
    message_type = data.get('__messagetype__') or ''
    logging.debug('Received UDP message %s' % (message_type))
    if message_type == 'contactinfo' or message_type == 'contactreplace':
        qso_id = data.get('ID') or '';
        
        # If no ID tag from N1MM, generate a hash for uniqueness
        if len(qso_id) == 0:
           qso_id = checksum(data)
        else:
           qso_id = qso_id.replace('-','')
            
        qso_timestamp = data.get('timestamp')
        mycall = data.get('mycall', '').upper()
        band = data.get('band')
        mode = data.get('mode', '').upper()
        operator = data.get('operator', '').upper()
        station_name = data.get('StationName', '')
        if station_name is None or station_name == '':
            station_name = data.get('NetBiosName', '')
        station = station_name.upper()
        rx_freq = int(data.get('rxfreq')) * 10  # convert to Hz
        tx_freq = int(data.get('txfreq')) * 10
        callsign = data.get('call', '').upper()
        rst_sent = data.get('snt')
        rst_recv = data.get('rcv')
        exchange = data.get('exchange1', '').upper()
        section = data.get('section', '').upper()
        comment = data.get('comment', '')
        
        # convert qso_timestamp to datetime object
        timestamp = convert_timestamp(qso_timestamp)

        dataaccess.record_contact_combined(db, cursor, operators, stations,
                                           timestamp, mycall, band, mode, operator, station,
                                           rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                                           exchange, section, comment, qso_id)
    elif message_type == 'RadioInfo':
        logging.debug('Received radioInfo message')
    elif message_type == 'contactdelete':
        qso_id = data.get('ID') or ''
        
        # If no ID tag from N1MM, generate a hash for uniqueness
        if len(qso_id) == 0:
            qso_id = checksum(data)
        else:
            qso_id = qso_id.replace('-','')
        
        logging.info('Delete QSO Request with ID %s' % (qso_id))
        dataaccess.delete_contact_by_qso_id(db, cursor, qso_id)
        
    elif message_type == 'dynamicresults':
        logging.debug('Received Score message')
    else:
        logging.warning('unknown message type {} received, ignoring.'.format(message_type))
        logging.debug(message)


def message_processor(q, event):
    global run
    logging.info('collector message_processor starting.')
    message_count = 0
    seen = set()
    db = sqlite3.connect(config.DATABASE_FILENAME)
    try:
        cursor = db.cursor()
        dataaccess.create_tables(db, cursor)

        operators = Operators(db, cursor)
        stations = Stations(db, cursor)
        parser = N1mmMessageParser()

        thread_run = True
        while not event.is_set() and thread_run:
            try:
                udp_data = q.get()
                message_count += 1
                process_message(parser, db, cursor, operators, stations, udp_data, seen)
            except KeyboardInterrupt:
                logging.debug('message processor stopping due to keyboard interrupt')
                thread_run = False
    finally:
        db.close()
        logging.info('db closed')
        run = False
        logging.info('collector message_processor exited, {} messages collected.'.format(message_count))


def main():
    try:
        logging.info('Collector started...')
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        process_event = None
        proc = None
        try:
            receive_socket.bind(('', config.N1MM_BROADCAST_PORT))

            q = multiprocessing.Queue()
            process_event = multiprocessing.Event()

            proc = multiprocessing.Process(name='message_processor', target=message_processor, args=(q, process_event))
            proc.start()

            receive_socket.settimeout(5)
            global run
            while run:
                try:
                    udp_data = receive_socket.recv(BROADCAST_BUF_SIZE)
                    q.put(udp_data)
                except socket.timeout:
                    pass
        finally:
            if receive_socket is not None:
                receive_socket.close()
            if process_event is not None:
                process_event.set()
            if proc is not None:
                proc.join(60)
                if proc.is_alive():
                    logging.warning('message processor did not exit upon request, killing.')
                    proc.terminate()
    except KeyboardInterrupt:
        pass

    logging.info('Collector done...')


if __name__ == '__main__':
    main()
