#!/usr/bin/python

import os
import pygame
import sqlite3
import time
import threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import pylab

from n1mm_view_constants import *

DISPLAY_DWELL_TIME = 5
DATA_DWELL_TIME = 60

GREEN = pygame.Color(0, 255, 0)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GRAY = pygame.Color(192, 192, 192)

image_index = 0

qso_operators = []
qso_stations = []
qso_band_modes = []
operator_qso_rates = []

QSO_OPERATORS_IMAGE_INDEX = 0
QSO_STATIONS_IMAGE_INDEX = 1
QSO_BANDS_IMAGE_INDEX = 2
QSO_MODES_IMAGE_INDEX = 3
QSO_COUNTS_IMAGE_INDEX = 4
QSO_RATES_IMAGE_INDEX = 5
IMAGE_COUNT = 6
images = [None] * IMAGE_COUNT


def log(message):
    print '%f %s' % (time.clock(), message)


def load_data():
    """
    load data from the database tables
    """
    log('load data')
    global cursor
    global qso_operators, qso_stations, qso_band_modes, operator_qso_rates

    try:
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
        slice_minutes = 10
        slices_per_hour = 60 / slice_minutes

        # this is useful for debugging, but not so useful beyond that.
        # the timestamp should be 60 seconds behind current time.
        end_time = int(time.time()) - 60
        #print 'calculated end_time is %d' % end_time

        # get timestamp from the last record in the database
        #cursor.execute('SELECT timestamp FROM qso_log ORDER BY id DESC LIMIT 1')
        #print time.clock()
        #for row in cursor:
        #    end_time = row[0]
        #print 'database end_time is %d' % end_time

        start_time = end_time - slice_minutes * 60
        print start_time, end_time

        cursor.execute('SELECT operator.name, COUNT(operator_id) qso_count FROM qso_log\n'
                       'JOIN operator ON operator.id = operator_id\n'
                       'WHERE timestamp >= ? AND timestamp <= ?\n'
                       'GROUP BY operator_id ORDER BY qso_count DESC LIMIT 10;', (start_time, end_time))
        operator_qso_rates = [['Operator','Rate']]
        total = 0
        for row in cursor:
            rate = row[1] * slices_per_hour
            total += rate
            operator_qso_rates.append([row[0], '%4d' % rate])
        operator_qso_rates.append(['Total', '%4d' % total])

        log('load data done')
    except sqlite3.OperationalError:
        log('could not load data, database error')


def init_display():
    global screen, size

    disp_no = os.getenv("DISPLAY")
    if disp_no:
        print "I'm running under X display = {0}".format(disp_no)

    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    drivers = ['fbcon', 'directfb', 'svgalib', 'directx', 'windib']
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            continue
        found = True
        print 'using {0} driver'.format(driver)
        break

    if not found:
        raise Exception('No suitable video driver found!')

    pygame.mouse.set_visible(0)
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print "display size: %d x %d" % (size[0], size[1])
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    # Clear the screen to start
    screen.fill(BLACK)
    # Initialise font support
    pygame.font.init()
    # Render the screen
    #pygame.display.update()


def make_pie(values, labels, title):
    # make this pie chart as tall as the display.
    log('make_pie(...,...,%s)' % title)
    inches = size[1] / 100.0
    fig = pylab.figure(figsize=(inches, inches), dpi=100, tight_layout=True, facecolor='#000000')
    ax = fig.add_subplot(111)
    ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'color': 'white'})
    ax.set_title(title, color='white', size='xx-large', weight='bold')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[0:5], labels[0:5], title='Top %s' % title, loc='lower left')
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    plt.close(fig)

    canvas_size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, canvas_size, "RGB")
    log('make_pie(...,...,%s) done' % title)
    return surf


def show_graph(surf):
    global size
    xoffset = (size[0] - surf.get_width()) / 2
    # yoffset = (size[1] - surf.get_height()) / 2
    yoffset = 0
    screen.fill((0, 0, 0))
    screen.blit(surf, (xoffset, yoffset))


def qso_operators_graph():
    global qso_operators
    # calculate QSO by Operator
    labels = []
    values = []
    for d in qso_operators:
        labels.append(d[0])
        values.append(d[1])
    return make_pie(values, labels, "QSOs by Operator")


def qso_stations_graph():
    # calculate QSO by Station
    labels = []
    values = []
    for d in qso_stations:
        labels.append(d[0])
        values.append(d[1])
    return make_pie(values, labels, "QSOs by Station")


def qso_bands_graph():
    # calculate QSOs by Band
    labels = []
    values = []
    band_data = [[band, 0] for band in range(0, len(BANDS_LIST))]
    for qso_band_mode in qso_band_modes:
        band = qso_band_mode[0] / 10
        band_data[band][1] = qso_band_mode[1] + band_data[band][1]

    for bd in sorted(band_data[1:], key=lambda count: count[1], reverse=True):
        if bd[1] > 0:
            labels.append(BANDS_TITLE[bd[0]])
            values.append(bd[1])
    return make_pie(values, labels, "QSOs by Band")


def qso_modes_graph():
    # calculate QSOs by Mode
    labels = []
    values = []
    mode_data = [[mode, 0] for mode in range(0, len(MODES_LIST))]
    for qso_band_mode in qso_band_modes:
        mode = qso_band_mode[0] % 10
        mode_data[mode][1] = qso_band_mode[1] + mode_data[mode][1]

    for md in sorted(mode_data[1:], key=lambda count: count[1], reverse=True):
        if md[1] > 0:
            labels.append(SIMPLE_MODES_LIST[md[0]])
            values.append(md[1])
    return make_pie(values, labels, "QSOs by Mode")


def qso_summary_table():
    return draw_table(make_score_table(), "QSOs Summary")

def qso_rates_table():
    return draw_table(operator_qso_rates, "QSO/Hour Rates")


def draw_clock():
    font_size = 100
    font = pygame.font.Font(None, font_size)
    text = font.render(time.strftime('%H:%M:%S', time.gmtime()), True, GREEN, BLACK)
    textpos = text.get_rect()
    textpos.bottom = size[1] - 1
    textpos.right = size[0] - 1
    screen.blit(text, textpos)


def draw_table(cell_text, title):
    log('draw_table(...,%s)' % title)
    font_size = 100
    font = pygame.font.Font(None, font_size)

    text_y_offset = 4
    text_x_offset = 4
    line_width = 4

    # calculate column widths
    rows = len(cell_text)
    cols = len(cell_text[1])
    col_widths = [0] * cols
    widest = 0
    for row in cell_text:
        col_num = 0
        for col in row:
            size = font.size(col)
            text_width = size[0] + 2 * text_x_offset
            if text_width > col_widths[col_num]:
                col_widths[col_num] = text_width
            if text_width > widest:
                widest = text_width
            col_num += 1

    # cheat on column widths -- set all to the widest.
    # maybe someday I'll fix this to dynamically set each column width.  or something.
    column_width = widest
    row_height = font.get_height()
    width = cols * column_width + line_width / 2
    height = (rows + 1) * row_height + line_width / 2
    surf = pygame.Surface((width, height))

    surf.fill(BLACK)
    text_color = GRAY
    head_color = WHITE
    grid_color = GRAY

    # draw the title
    text = font.render(title, True, head_color)
    textpos = text.get_rect()
    textpos.y = 0
    textpos.centerx = width / 2
    surf.blit(text, textpos)

    starty = row_height
    origin = (0, row_height)

    # draw the grid
    x = 0
    y = starty
    for r in range(0, rows + 1):
        sp = (x, y)
        ep = (x + width, y)
        pygame.draw.line(surf, grid_color, sp, ep, line_width)
        y += row_height

    x = 0
    y = starty
    for c in range(0, cols + 1):
        sp = (x, y)
        ep = (x, y + height)
        pygame.draw.line(surf, grid_color, sp, ep, line_width)
        x += column_width

    y = starty + text_y_offset
    row_number = 0
    for row in cell_text:
        row_number += 1
        x = origin[0]
        column_number = 0
        for col in row:
            column_number += 1
            x += column_width
            if row_number == 1 or column_number == 1:
                text = font.render(col, True, head_color)
            else:
                text = font.render(col, True, text_color)
            textpos = text.get_rect()
            textpos.y = y - text_y_offset
            textpos.right = x - text_x_offset
            surf.blit(text, textpos)
        y += row_height
    log('draw_table(...,%s) done' % title)
    return surf


def make_score_table():
    """
    create the score table from data
    """
    cell_data = [[0 for m in SIMPLE_MODES_LIST] for b in BANDS_TITLE]

    for qso_band_mode in qso_band_modes:
        band = qso_band_mode[0] / 10
        mode = qso_band_mode[0] % 10
        cell_data[band][mode] = qso_band_mode[1]
        cell_data[0][mode] += qso_band_mode[1]
        cell_data[band][0] += qso_band_mode[1]

    total = 0
    for c in cell_data[0][1:]:
        total += c
    cell_data[0][0] = total

    # the totals are in the 0th row and 0th column, move them to last.
    cell_text = []
    cell_text.append(['', '   CW', 'Phone', ' Data', 'Total'])
    band_num = 0
    for row in cell_data[1:]:
        band_num += 1
        row_text = ['%5s' % BANDS_TITLE[band_num]]

        for col in row[1:]:
            row_text.append('%5d' % col)
        row_text.append('%5d' % row[0])
        cell_text.append(row_text)

    row = cell_data[0]
    row_text = ['Total']
    for col in row[1:]:
        row_text.append('%5d' % col)
    row_text.append('%5d' % row[0])
    cell_text.append(row_text)
    return cell_text


def next_chart():
    global image_index, images
    surf = images[image_index]
    if surf != None:
        show_graph(surf)
    image_index += 1
    if image_index >= IMAGE_COUNT:
        image_index = 0
    draw_clock()
    pygame.display.flip()


def refresh_data():
    """
    reload the data from the database, (re)generate graphics
    """
    log('refresh_data')
    global images, cursor
    db = sqlite3.connect('n1mm-mon.db')
    cursor = db.cursor()
    log('database connected')
    load_data()
    images[QSO_OPERATORS_IMAGE_INDEX] = qso_operators_graph()
    images[QSO_STATIONS_IMAGE_INDEX] = qso_stations_graph()
    images[QSO_BANDS_IMAGE_INDEX] = qso_bands_graph()
    images[QSO_MODES_IMAGE_INDEX] = qso_modes_graph()
    images[QSO_COUNTS_IMAGE_INDEX] = qso_summary_table()
    images[QSO_RATES_IMAGE_INDEX] = qso_rates_table()
    db.close()
    log('images refreshed')


class UpdateThread (threading.Thread):
    """
    run the chart updates in their own thread, so the UI does not block.
    """
    def run(self):
        refresh_data()


def main():
    print 'dashboard startup'
    print
    log('startup')

    # open the database
    global db, cursor

    global size

    init_display()

    log('display setup')

    refresh_data()

    next_chart()

    pygame.time.set_timer(pygame.USEREVENT, 1000)
    run = True

    display_update_timer = DISPLAY_DWELL_TIME
    data_update_timer = DATA_DWELL_TIME

    while run:
        for event in [pygame.event.wait()] + pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.USEREVENT:
                data_update_timer -= 1
                if data_update_timer < 1:
                    thread = UpdateThread()
                    thread.start()
                    data_update_timer = DATA_DWELL_TIME
                display_update_timer -= 1
                if display_update_timer < 1:
                    display_update_timer = DISPLAY_DWELL_TIME
                    next_chart()
                draw_clock()
                pygame.display.flip()
            elif event.type == pygame.KEYDOWN:
                if event.key == ord('q'):
                    run = False
                elif event.key == ord('n'):
                    next_chart()
                    display_update_timer = DISPLAY_DWELL_TIME
                    pygame.display.flip()

    pygame.time.set_timer(pygame.USEREVENT, 0)

    pygame.display.quit()

    print
    print "dashboard exit"
    print


if __name__ == '__main__':
    main()
