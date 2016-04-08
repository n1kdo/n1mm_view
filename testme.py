#!/usr/bin/python

import sqlite3
import time

cursor = None
db = None
qso_operators = []
qso_stations = []
qso_band_modes = []
operator_qso_rates = []
size = None


def load_data():
    """
    load data from the database tables
    """
    global cursor
    global qso_operators, qso_stations, qso_band_modes, operator_qso_rates

    # load qso_operators
    qso_operators = []
    cursor.execute('SELECT name, qso_count FROM qso_operator JOIN operator\n'
                   'ON qso_operator.operator_id = operator.id ORDER BY qso_count DESC;')
    for row in cursor:
        qso_operators.append((row[0], row[1]))

    # load qso_stations
    qso_stations = []
    cursor.execute('SELECT name, qso_count FROM qso_station JOIN station\n'
                   'ON qso_station.station_id = station.id ORDER BY qso_count DESC;')
    for row in cursor:
        qso_stations.append((row[0], row[1]))

    # load qso_band_modes
    qso_band_modes = []
    cursor.execute('SELECT band_mode_id, qso_count FROM qso_band_mode;')
    for row in cursor:
        qso_band_modes.append((row[0], row[1]))

    # calculate QSOs per hour rate for all active operators
    # the higher the slice_minutes number is, the better the
    # resolution of the rate, but the slower to update.
    slice_minutes = 6
    slices_per_hour = 60 / slice_minutes

    # this is useful for debugging, but not so useful beyond that.
    # the timestamp should be 60 seconds behind current time.
    end_time = int(time.time()) - 60
    print 'calculated end_time is %d' % end_time

    # get timestamp from the last record in the database
    cursor.execute('SELECT timestamp FROM qso_log ORDER BY id DESC LIMIT 1')
    print time.clock()
    end_time = int(time.time()) - 60
    for row in cursor:
        end_time = row[0]
    print 'database end_time is %d' % end_time

    start_time = end_time - slice_minutes * 60
    print start_time, end_time

    cursor.execute('SELECT operator.name, COUNT(operator_id) qso_count FROM qso_log\n'
                   'JOIN operator ON operator.id = operator_id\n'
                   'WHERE timestamp >= ? AND timestamp <= ?\n'
                   'GROUP BY operator_id ORDER BY qso_count DESC LIMIT 10;', (start_time, end_time))

    operator_qso_rates = [['Operator', 'Rate']]
    total = 0

    for row in cursor:
        rate = row[1] * slices_per_hour
        total += rate
        operator_qso_rates.append([row[0], '%4d' % rate])
    operator_qso_rates.append(['Total', '%4d' % total])

    print operator_qso_rates


def main():
    print 'dashboard startup'

    # open the database
    global db, cursor

    global size

    db = sqlite3.connect('n1mm_view.db')
    cursor = db.cursor()

    load_data()

    db.close()


if __name__ == '__main__':
    main()
