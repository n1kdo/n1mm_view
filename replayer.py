#!/usr/bin/python3
"""
n1mm_view log replayer
this program replays old N1MM+ log files as udp broadcasts for testing n1mm_view.

NOTE: the sqlite3 dll that ships with windows python may not be able to read the
N1MM+ database file.
You can get the latest sqlite3 dll from https://www.sqlite.org/download.html and
replace the version in your python dlls folder.  I've not tried this on Linux.
Make sure your download the version for the same architecture as your python
installation (32- vs. 64-bit.)
"""

import datetime
import logging
import os
import socket
import sqlite3
import sys
import time

from config import Config
config = Config()

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019, 2021 Jeffrey B. Otterson and n1mm_view maintainers'
__license__ = 'Simplified BSD'

BROADCAST_BUF_SIZE = 2048

"""
FACTOR is the speed-up factor for replaying, because I don't have a whole day to 
load a day-long contest's data.  Set this to 10 for a 10X speedup.  Set to 60 to make 
minutes take seconds.  set to 60, an day long contest should take about 24 minutes to replay. 
"""
# FACTOR = 60
FACTOR = 120

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
            <ID>%s</ID>
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

    if not os.path.exists(config.N1MM_LOG_FILE_NAME):
        logging.error('cannot find N1MM database file %s', config.N1MM_LOG_FILE_NAME)
        sys.exit(1)

    db_uri = 'file:{}?mode=ro'.format(config.N1MM_LOG_FILE_NAME)
    with sqlite3.connect(db_uri, uri=True) as db:
        cursor = db.cursor()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        cursor.execute('SELECT TS, band, Freq, QSXFreq, Operator, Mode, Call, CountryPrefix, WPXPrefix, \n'
                       'StationPrefix, Continent,  SNT, SentNr, RCV, NR, GridSquare, Exchange1, Sect, ZN, Points, \n'
                       'NetBiosName, ID \n'
                       'FROM DXLOG WHERE ContestName = "FD" AND ContestNR > 0 order by TS;')
        qso_number = 0
        last_tm = 0
        delay = 0.050
        for row in cursor:
            ts = row[0]
            qso_time = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            if True:
                #if config.EVENT_START_TIME <= qso_time <= config.EVENT_END_TIME:
                tm = qso_time.timestamp()
                band = convert_band(row[1])
                rx_freq = row[2] * 100
                tx_freq = row[3] * 100
                values = (ts, band, rx_freq, tx_freq, row[4], row[5], row[6], row[7],
                          row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                          row[16], row[17], row[18], row[19], row[20], row[21])
                payload = TEMPLATE % values
                #print(payload)
                if last_tm != 0:
                    ds = min(3600, int(tm - last_tm))  # set max delta to one hour
                    delay = round(max(ds / FACTOR, 0.050), 2)  # set min delay to 0.050 sec
                    # print(ts, tm, ds, delay)
                    time.sleep(delay)

                last_tm = tm
                s.sendto(payload.encode(), (config.N1MM_BROADCAST_ADDRESS, config.N1MM_BROADCAST_PORT))
                qso_number += 1
                logging.info('sent qso # {} timestamp {}'.format(qso_number, ts))
            else:
                logging.info('ignoring qso with timestamp {}'.format(ts))

    logging.info('replayer done...')


if __name__ == '__main__':
    main()
