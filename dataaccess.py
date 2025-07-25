# n1mm_view database access code

import calendar
from datetime import datetime
import logging
import time
import constants
from config import Config

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2019, 2020, Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

config = Config()
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.LOG_LEVEL)
logging.Formatter.converter = time.gmtime


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
                   # '    (id INTEGER PRIMARY KEY NOT NULL,\n'
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
                   '     comment TEXT,\n'
                   '     qso_id  char(32) PRIMARY KEY NOT NULL);')  # this is primary key to speed up Update & Delete
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_band_id ON qso_log(band_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_mode_id ON qso_log(mode_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_operator_id ON qso_log(operator_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_station_id ON qso_log(station_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_section ON qso_log(section);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_qso_id ON qso_log(qso_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS qso_log_qso_timestamp ON qso_log(timestamp);')
    db.commit()


def record_contact_combined(db, cursor, operators, stations,
                            timestamp, mycall, band, mode, operator, station,
                            rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                            exchange, section, comment, qso_id):
    """
    record the results of a contact_message
    """
    band_id = constants.Bands.get_band_number(band)
    mode_id = constants.Modes.get_mode_number(mode)
    operator_id = operators.lookup_operator_id(operator)
    station_id = stations.lookup_station_id(station)

    logging.info(' QSO: %s %6s %4s %-6s %-12s %-12s %10d %10d %-6s %3s %3s %3s %-3s %-3s %32s' % (
        time.strftime('%Y-%m-%d %H:%M:%S', timestamp),
        mycall, band,
        mode, operator,
        station, rx_freq, tx_freq, callsign, rst_sent,
        rst_recv, exchange, section, comment, qso_id))

    if band_id is None or mode_id is None or operator_id is None or station_id is None:
        logging.warning('[dataaccess] cannot log this QSO, bad data.')
        return
    try:
        cursor.execute(
            'insert or replace into qso_log \n'
            '    (timestamp, mycall, band_id, mode_id, operator_id, station_id , rx_freq, tx_freq, \n'
            '     callsign, rst_sent, rst_recv, exchange, section, comment, qso_id)\n'
            '    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
            (calendar.timegm(timestamp), mycall, band_id, mode_id, operator_id, station_id, rx_freq, tx_freq,
             callsign, rst_sent, rst_recv, exchange, section, comment, str(qso_id)))

        db.commit()
    except Exception as err:
        logging.warning('Insert Failed: %s\nError: %s' % (qso_id, str(err)))


def record_contact(db, cursor, operators, stations,
                   timestamp, mycall, band, mode, operator, station,
                   rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                   exchange, section, comment, qso_id):
    """
    record the results of a contact_message
    """
    band_id = constants.Bands.get_band_number(band)
    mode_id = constants.Modes.get_mode_number(mode)
    operator_id = operators.lookup_operator_id(operator)
    station_id = stations.lookup_station_id(station)

    logging.info('QSO: %s %6s %4s %-6s %-12s %-12s %10d %10d %-6s %3s %3s %3s %-3s %-3s %32s' % (
        time.strftime('%Y-%m-%d %H:%M:%S', timestamp),
        mycall, band,
        mode, operator,
        station, rx_freq, tx_freq, callsign, rst_sent,
        rst_recv, exchange, section, comment, qso_id))

    if band_id is None or mode_id is None or operator_id is None or station_id is None:
        logging.warning('cannot log this QSO, bad data.')
        return
    try:
        cursor.execute(
            'insert into qso_log \n'
            '    (timestamp, mycall, band_id, mode_id, operator_id, station_id , rx_freq, tx_freq, \n'
            '     callsign, rst_sent, rst_recv, exchange, section, comment, qso_id)\n'
            '    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
            (calendar.timegm(timestamp), mycall, band_id, mode_id, operator_id, station_id, rx_freq, tx_freq,
             callsign, rst_sent, rst_recv, exchange, section, comment, qso_id))

        db.commit()
    except Exception as err:
        logging.warning('Insert Failed: %s\nError: %s' % (qso_id, str(err)))


def update_contact(db, cursor, operators, stations,
                   timestamp, mycall, band, mode, operator, station,
                   rx_freq, tx_freq, callsign, rst_sent, rst_recv,
                   exchange, section, comment, qso_id):
    """
    record the results of a contact_message
    """
    band_id = constants.Bands.get_band_number(band)
    mode_id = constants.Modes.get_mode_number(mode)
    operator_id = operators.lookup_operator_id(operator)
    station_id = stations.lookup_station_id(station)

    logging.info('Update QSO: %s %6s %4s %-6s %-12s %-12s %10d %10d %-6s %3s %3s %3s %-3s %-3s %32s' % (
        time.strftime('%Y-%m-%d %H:%M:%S', timestamp),
        mycall, band,
        mode, operator,
        station, rx_freq, tx_freq, callsign, rst_sent,
        rst_recv, exchange, section, comment, qso_id))

    if band_id is None or mode_id is None or operator_id is None or station_id is None:
        logging.warning('[dataaccess] cannot log this QSO, bad data.')
        return
    try:
        cursor.execute(
            'update qso_log \n'
            '    set timestamp=?, mycall=?, band_id=?, mode_id=?, operator_id=?, station_id=? , rx_freq=?, tx_freq=?, \n'
            '     callsign=?, rst_sent=?, rst_recv=?, exchange=?, section=?, comment=? \n'
            ' where qso_id = ?;',
            (calendar.timegm(timestamp), mycall, band_id, mode_id, operator_id, station_id, rx_freq, tx_freq,
             callsign, rst_sent, rst_recv, exchange, section, comment, qso_id))

        db.commit()
    except Exception as err:
        logging.warning('Update Failed: %s\nError: %s' % (qso_id, str(err)))


def delete_contact(db, cursor, timestamp, station, callsign):
    """
    Delete the results of a delete in N1MM
    """

    """ station_id = stations.lookup_station_id(station)
"""

    logging.info('DELETEQSO: %s, timestamp = %s' % (callsign, calendar.timegm(timestamp)))
    try:
        cursor.execute(
            "delete from qso_log where callsign = ? and timestamp = ?", (callsign, calendar.timegm(timestamp),))
        db.commit()
    except Exception as e:
        logging.exception('Exception deleting contact from db.')
        return ''


def delete_contact_by_qso_id(db, cursor, qso_id):
    """
    Delete the results of a delete in N1MM
    """

    """ station_id = stations.lookup_station_id(station)
"""

    logging.debug('DELETEQSOByqso_id: %s' % (qso_id))
    try:
        cursor.execute('delete from qso_log where qso_id = ?;', (str(qso_id),))
        db.commit()
    except Exception as e:
        logging.exception('Exception deleting contact (by qso_id) from db.')
        return ''


def get_last_qso(cursor):
    cursor.execute('SELECT timestamp, callsign, exchange, section, operator.name, band_id \n'
                   'FROM qso_log JOIN operator WHERE operator.id = operator_id \n'
                   'ORDER BY timestamp DESC LIMIT 1')
    last_qso_time = int(time.time()) - 60
    message = ''
    for row in cursor:
        last_qso_time = row[0]
        message = 'Last QSO: %s %s %s on %s by %s at %s' % (
            row[1], row[2], row[3], constants.Bands.BANDS_TITLE[row[5]], row[4],
            datetime.utcfromtimestamp(row[0]).strftime('%H:%M:%S'))
        logging.debug('%s' % (message))

    return last_qso_time, message


def get_operators_by_qsos(cursor):
    logging.debug('Load QSOs by Operator')
    qso_operators = []
    cursor.execute('SELECT name, COUNT(operator_id) AS qso_count \n'
                   'FROM qso_log JOIN operator ON operator.id = operator_id \n'
                   'GROUP BY operator_id ORDER BY qso_count DESC;')
    for row in cursor:
        qso_operators.append((row[0], row[1]))
    return qso_operators


def get_station_qsos(cursor):
    logging.debug('Load QSOs by Station')
    qso_stations = []
    cursor.execute('SELECT name, COUNT(station_id) AS qso_count \n'
                   'FROM qso_log JOIN station ON station.id = station_id GROUP BY station_id;')
    for row in cursor:
        qso_stations.append((row[0], row[1]))
    return qso_stations


def get_qsos_per_hour_per_operator(cursor, last_qso_time):
    logging.debug('Load QSOs per Hour by Operator')
    slice_minutes = 15
    slices_per_hour = 60 / slice_minutes
    start_time = last_qso_time - slice_minutes * 60

    cursor.execute('SELECT operator.name, COUNT(operator_id) qso_count FROM qso_log\n'
                   'JOIN operator ON operator.id = operator_id\n'
                   'WHERE timestamp >= ? AND timestamp <= ?\n'
                   'GROUP BY operator_id ORDER BY qso_count DESC LIMIT 10;', (start_time, last_qso_time))
    operator_qso_rates = [['Operator', 'Rate']]
    total = 0
    for row in cursor:
        rate = row[1] * slices_per_hour
        total += rate
        operator_qso_rates.append([row[0], '%4d' % rate])
    operator_qso_rates.append(['Total', '%4d' % total])
    return operator_qso_rates


def get_qso_band_modes(cursor):
    qso_band_modes = [[0] * 4 for _ in constants.Bands.BANDS_LIST]

    cursor.execute('SELECT COUNT(*), band_id, mode_id FROM qso_log GROUP BY band_id, mode_id;')
    for row in cursor:
        qso_band_modes[row[1]][constants.Modes.MODE_TO_SIMPLE_MODE[row[2]]] += row[0]
    return qso_band_modes


def get_qso_classes(cursor):
    cursor.execute('SELECT COUNT(*), exchange FROM qso_log group by exchange;')
    exchanges = []
    for row in cursor:
        exchanges.append((row[0], row[1]))
    return exchanges


def get_qsos_per_hour_per_band(cursor):
    qsos_per_hour = []
    qsos_by_band = [0] * constants.Bands.count()
    slice_minutes = 15
    slice_minutes = 12  # TODO FIXME was 15, 12 looks pretty ok
    slices_per_hour = 60 / slice_minutes
    window_seconds = slice_minutes * 60

    logging.debug('Load QSOs per Hour by Band')
    cursor.execute('SELECT timestamp / %d * %d AS ts, band_id, COUNT(*) AS qso_count \n'
                   'FROM qso_log GROUP BY ts, band_id;' % (window_seconds, window_seconds))
    for row in cursor:
        if len(qsos_per_hour) == 0:
            qsos_per_hour.append([0] * constants.Bands.count())
            qsos_per_hour[-1][0] = row[0]
        while qsos_per_hour[-1][0] != row[0]:
            ts = qsos_per_hour[-1][0] + window_seconds
            qsos_per_hour.append([0] * constants.Bands.count())
            qsos_per_hour[-1][0] = ts
        qsos_per_hour[-1][row[1]] = row[2] * slices_per_hour
        qsos_by_band[row[1]] += row[2]

    for rec in qsos_per_hour:
        rec[0] = datetime.utcfromtimestamp(rec[0])
        # t = rec[0].strftime('%H:%M:%S')

    return qsos_per_hour, qsos_by_band


def get_qsos_by_section(cursor):
    logging.debug('Load QSOs by Section')
    qsos_by_section = {}
    cursor.execute('SELECT section, COUNT(section) AS qsos FROM qso_log GROUP BY section;')
    for row in cursor:
        qsos_by_section[row[0]] = row[1]
        logging.debug(f'Section {row[0]} {row[1]}')
    return qsos_by_section


def get_last_N_qsos(cursor, nQSOCount):
    logging.info('get_last_N_qsos for last %d QSOs' % (nQSOCount))
    qsos = []
    cursor.execute(
        'SELECT qso_id, timestamp, callsign, band_id, mode_id, operator.name, rx_freq, tx_freq, exchange, section, station.name \n'
        'FROM qso_log '
        'JOIN operator ON operator.id = operator_id\n'
        'JOIN station ON station.id = station_id\n'
        'ORDER BY timestamp DESC LIMIT %d;' % (nQSOCount))
    for row in cursor:
        qsos.append((row[1]  # raw timestamp 0
                         , row[2]  # call 1
                         , constants.Bands.BANDS_TITLE[row[3]]  # band 2
                         , constants.Modes.SIMPLE_MODES_LIST[constants.Modes.MODE_TO_SIMPLE_MODE[row[4]]]  # mode 3
                         , row[5]  # operator callsign 4
                         , row[8]  # exchange 5
                         , row[9]  # section 6
                         , row[10]  # station name 7
                     ))
        message = 'QSO: time=%sZ call=%s exchange=%s %s mode=%s band=%s operator=%s station=%s' % (
            datetime.utcfromtimestamp(row[1]).strftime('%Y %b %d %H:%M:%S')
            , row[2]  # callsign
            , row[8]  # exchange
            , row[9]  # section
            , constants.Modes.SIMPLE_MODES_LIST[constants.Modes.MODE_TO_SIMPLE_MODE[row[4]]]
            , constants.Bands.BANDS_TITLE[row[3]]
            , row[5]  # operator
            , row[10]  # station
        )
        logging.info('%s' % (message))
    return qsos
