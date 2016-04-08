#!/usr/bin/python

import sqlite3
import time
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR

BROADCAST_ADDRESS = "192.168.1.255"
BROADCAST_PORT = 12060
BROADCAST_BUF_SIZE = 2048

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


# mainline
def main():
    """
    re-play last years logs as UDP broadcasts to load test the collector process
    """
    print 'replayer started...'

    db = sqlite3.connect('2015N4N.s3db')
    cursor = db.cursor()

    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        s.bind(('', BROADCAST_PORT))
    except:
        print "Error connecting to the UDP stream."
        return

    cursor.execute('SELECT TS, band, Freq, QSXFreq, Operator, Mode, Call, CountryPrefix, WPXPrefix, \n'
                   'StationPrefix, Continent,  SNT, SentNr, RCV, NR, GridSquare, Exchange1, Sect, ZN, Points, \n'
                   'NetBiosName \n'
                   'FROM DXLOG order by TS;')
    qso_number = 0
    for row in cursor:
        #  ts = row[0]
        ts =  time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        band = convert_band(row[1])
        rx_freq = row[2] * 100
        tx_freq = row[3] * 100
        values = (ts, band, rx_freq, tx_freq, row[4], row[5], row[6], row[7],
                  row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                  row[16], row[17], row[18], row[19], row[20])
        payload = TEMPLATE % values

        s.sendto(payload, (BROADCAST_ADDRESS, BROADCAST_PORT))
        qso_number += 1
        print "sent qso # %d timestamp %s" % (qso_number, ts)
        # there are ~4000 qsos in the database.
        # 4/sec will take ~1000 sec --> 17 minutes to play back -- the entire contest.
        time.sleep(0.25)

    db.close()

    print 'replayer done...'


if __name__ == '__main__':
    main()
