#!/usr/bin/python
"""
n1mm_view log replayer
this program replays old N1MM+ log files as udp broadcasts for testing n1mm_view.

NOTE: the sqlite3 dll that ships with windows python won't read the N1MM+ log file.
You must get the latest sqlite3 dll from https://www.sqlite.org/download.html and
replace the version in your python dlls folder.  I've not tried this on Linux.
Make sure your download the version for the same architecture as your python
installation (32- vs. 64-bit.)
"""

import logging
import random
import sqlite3
import time
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR

from config import *

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

BROADCAST_BUF_SIZE = 2048

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.Formatter.converter = time.gmtime

""" this is what the N1MM+ broadcast looks like. """
TEMPLATE = '''<?xml version="1.0"?>
    <contactinfo>
            <contestname>FD</contestname>
            <contestnr>1</contestnr>
            <timestamp>%s</timestamp>
            <mycall>N4N</mycall>
            <band>%s</band>
            <rxfreq>%d</rxfreq>
            <txfreq>%d</txfreq>
            <operator>%s</operator>
            <mode>%s</mode>
            <call>%s</call>
            <countryprefix>%s</countryprefix>
            <wpxprefix>%s</wpxprefix>
            <stationprefix>%s</stationprefix>
            <continent>%s</continent>
            <snt>%s</snt>
            <sntnr>%s</sntnr>
            <rcv>%s</rcv>
            <rcvnr>%s</rcvnr>
            <gridsquare>%s</gridsquare>
            <exchange1>%s</exchange1>
            <section>%s</section>
            <comment></comment>
            <qth></qth>
            <name></name>
            <power></power>
            <misctext></misctext>
            <zone>%d</zone>
            <prec></prec>
            <ck>0</ck>
            <ismultiplier1>0</ismultiplier1>
            <ismultiplier2>0</ismultiplier2>
            <ismultiplier3>0</ismultiplier3>
            <points>%d</points>
            <radionr>1</radionr>
            <RoverLocation></RoverLocation>
            <RadioInterfaced>0</RadioInterfaced>
            <NetworkedCompNr>0</NetworkedCompNr>
            <IsOriginal>True</IsOriginal>
            <NetBiosName>%s</NetBiosName>
            <IsRunQSO>0</IsRunQSO>
    </contactinfo>'''


def convert_band(band):
    if band == 1.8:
        return '1.8'
    elif band == 3.5:
        return '3.5'
    else:
        return '%d' % band


def main():
    """
    re-play last years logs as UDP broadcasts to load test the collector process
    """
    logging.info('replayer started...')

    db = sqlite3.connect(N1MM_LOG_FILE_NAME)
    cursor = db.cursor()

    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        s.bind(('', N1MM_BROADCAST_PORT))
    except:
        logging.exception('Error connecting to the UDP stream.')
        return

    cursor.execute('SELECT TS, band, Freq, QSXFreq, Operator, Mode, Call, CountryPrefix, WPXPrefix, \n'
                   'StationPrefix, Continent,  SNT, SentNr, RCV, NR, GridSquare, Exchange1, Sect, ZN, Points, \n'
                   'NetBiosName \n'
                   'FROM DXLOG order by TS;')
    qso_number = 0
    for row in cursor:
        ts = row[0]
        band = convert_band(row[1])
        rx_freq = row[2] * 100
        tx_freq = row[3] * 100
        values = (ts, band, rx_freq, tx_freq, row[4], row[5], row[6], row[7],
                  row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                  row[16], row[17], row[18], row[19], row[20])
        payload = TEMPLATE % values

        s.sendto(payload, (N1MM_BROADCAST_ADDRESS, N1MM_BROADCAST_PORT))
        qso_number += 1
        logging.info("sent qso # %d timestamp %s" % (qso_number, ts))
        # there are ~4000 qsos in the database.
        # 4/sec will take ~1000 sec --> 17 minutes to play back -- the entire contest.
        # random.random returns a number from 0 to 1, so this will average about 2/sec.
        time.sleep(random.random()/10.0)

    db.close()

    logging.info('replayer done...')


if __name__ == '__main__':
    main()
