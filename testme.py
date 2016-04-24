#!/usr/bin/python

import datetime
import logging
import os
import pygame
import sqlite3
import time

import matplotlib
#  This makes the code analyzer angry, as python standards say to put imports ahead of all executable code.
#  But... it MUST be RIGHT HERE so matplotlib does not try to use the wrong backend.
matplotlib.use('Agg')
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import HourLocator, DateFormatter

#from matplotlib.patches import Polygon
#from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap

from n1mm_view_constants import *
from n1mm_view_config import *

GREEN = pygame.Color('#00ff00')
BLACK = pygame.Color('#000000')
WHITE = pygame.Color('#ffffff')
GRAY = pygame.Color('#cccccc')

cursor = None
db = None
qso_operators = []
qso_stations = []
qso_band_modes = []
operator_qso_rates = []
qsos_per_hour = []
qsos_by_band = []
first_qso_time = 0
last_qso_time = 0

size = None
graph_size = None


def init_display():
    """
    set up the pygame display, full screen
    """
    global screen, size, graph_size, view_font, view_font_height, bigger_font

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
            #  logging.warn('Driver: %s failed.' % driver)
            continue
        found = True
        logging.info('using %s driver' % driver)
        break

    if not found:
        raise Exception('No suitable video driver found!')

    pygame.mouse.set_visible(0)
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    logging.info('display size: %d x %d' % size)
    if driver != 'directx':  # debugging hack runs in a window on Windows
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    else:
        size = (1680, 1050)
        screen = pygame.display.set_mode(size)

    # Clear the screen to start
    screen.fill(BLACK)
    # Initialise font support
    pygame.font.init()
    view_font = pygame.font.Font('veraMoBd.ttf', 64)
    bigger_font = pygame.font.SysFont('veraMoBd.ttf', 180)
    view_font_height = view_font.get_height()
    graph_size = (pygame.display.Info().current_w, pygame.display.Info().current_h - view_font_height)


def itomdyhms(timeint):
    """
    make an integer time past the epoch into a nicely formatted string with the date
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timeint))


def itohms(timeint):
    """
    make an integer time past the epoch into a nicely formatted string
    """
    return time.strftime('%H:%M:%S', time.gmtime(timeint))


def load_data():
    """
    load data from the database tables
    """
    global cursor
    global qso_operators, qso_stations, qso_band_modes, operator_qso_rates
    global qsos_per_hour, qsos_by_band, first_qso_time, last_qso_time

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

    # get timestamp from the first record in the database
    cursor.execute('SELECT timestamp FROM qso_log ORDER BY id LIMIT 1')
    first_qso_time = int(time.time()) - 60
    for row in cursor:
        first_qso_time = row[0]

    # get timestamp from the last record in the database
    cursor.execute('SELECT timestamp FROM qso_log ORDER BY id DESC LIMIT 1')
    last_qso_time = int(time.time()) - 60
    for row in cursor:
        last_qso_time = row[0]

    start_time = last_qso_time - slice_minutes * 60
    # print start_time, last_qso_time

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

    qsos_per_hour = []
    qsos_by_band = [0] * len(BANDS_LIST)
    slice_minutes = 15
    slices_per_hour = 60 / slice_minutes
    window_seconds = slice_minutes * 60

    cursor.execute('SELECT timestamp / %d * %d AS ts, band_id, COUNT(*) AS qso_count \n'
                   'FROM qso_log GROUP BY ts, band_id;' % (window_seconds, window_seconds))
    for row in cursor:
        if len(qsos_per_hour) == 0:
            qsos_per_hour.append([0] * len(BANDS_LIST))
            qsos_per_hour[-1][0] = row[0]
            # print "inserted first row with timestamp %d" % row[0]
        while qsos_per_hour[-1][0] != row[0]:
            # print 'the last rec ts is %d, but I need ts %d' %(recs[-1][0], row[0])
            ts = qsos_per_hour[-1][0] + window_seconds
            qsos_per_hour.append([0] * len(BANDS_LIST))
            qsos_per_hour[-1][0] = ts
        qsos_per_hour[-1][row[1]] = row[2] * slices_per_hour
        qsos_by_band[row[1]] += row[2]

    # print qsos_by_band

    for rec in qsos_per_hour:
        rec[0] = datetime.datetime.utcfromtimestamp(rec[0])
        t = rec[0].strftime('%H:%M:%S')
        # print '%s %3d %3d %3d %3d %3d %3d %3d %3d %3d' % (t, rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8], rec[9])
    #print len(qsos_per_hour)


def draw_map():
    title = 'Sections Worked'
    width_inches = graph_size[0] / 100.0
    height_inches = graph_size[1] / 100.0
    fig = plt.Figure(figsize=(width_inches, height_inches), dpi=100, tight_layout=True, facecolor='black')
    ax = fig.add_subplot(111, axisbg='#888888')
    ax.set_title(title, color='white', size='xx-large', weight='bold')

    degrees_width = 118.0
    degrees_height = 55.0
    center_lat = 44.5
    center_lon = -110.0
    my_map = Basemap(ax=ax,
                     projection='merc',  # default is cyl
                     ellps='WGS84',
                     lat_0=center_lat, lon_0=center_lon,
                     llcrnrlat=center_lat - degrees_height / 2.0,
                     llcrnrlon=center_lon - degrees_width / 2.0,
                     urcrnrlat=center_lat + degrees_height / 2.0,
                     urcrnrlon=center_lon + degrees_width / 2.0,
                     resolution='i',  # 'c', 'l', 'i', 'h', 'f'
                     )

    # my_map.drawcoastlines(color='white', linewidth=0.5)
    # my_map.drawcountries(color='white', linewidth=0.5)
    # my_map.drawstates(color='white')
    my_map.drawmapboundary(fill_color='#000033')
    my_map.fillcontinents(color='#336633', lake_color='#000033')

    # mark our QTH
    x,y = my_map(QTH_LONGITUDE, QTH_LATITUDE)
    my_map.plot(x, y, 'o', color='r')

    # shapes
    sections = ['AB', 'BC', 'GTA', 'MAR', 'MB','NL', 'NT', 'ONE', 'ONN', 'ONS', 'QC', 'SK']

    num_sections = len(sections)
    color_map = plt.get_cmap('Dark2')
    color_palette = color_map(1. * np.arange(num_sections) / num_sections)

    section_shapes = {}
    for section_name in sections:
        my_map.readshapefile('../shapes/CanadaSections/x/%s' % section_name, section_name, drawbounds=False)
        shape = my_map.__dict__.get(section_name)
        patches = []
        for ss in shape:
            patches.append(matplotlib.patches.Polygon(np.array(ss), True))
        section_shapes[section_name] = matplotlib.collections.PatchCollection(patches, facecolor='m', edgecolor='k', linewidths=0.25, zorder=2)

    cidx = 0
    for section_name in sections:
        pc = section_shapes[section_name]
        pc.set_facecolor(color_palette[cidx])
        ax.add_collection(pc)
        cidx += 1

    my_map.nightshade(datetime.datetime.utcnow(), alpha=0.25)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    plt.close(fig)

    canvas_size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, canvas_size, "RGB")

    return surf


def junk():
    print "calling basemap"
    m = Basemap(
        projection='tmerc',
        lon_0=-85.,
        lat_0=45.,
        ellps = 'WGS84',
        llcrnrlon=-160.,llcrnrlat=25.,urcrnrlon=-60.,urcrnrlat=75.,
        lat_ts=0,
        resolution='i',
        suppress_ticks=True)
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='#ddaa66',lake_color='aqua')
    m.drawcoastlines()
    print "called basemap"
    m.drawmapboundary(color='w')


def load_image(name):
    return pygame.image.load(name)


def show_graph(surf):
    """
    display a surface on the screen.
    """
    logging.debug('show_graph')
    global size
    xoffset = (size[0] - surf.get_width()) / 2
    # yoffset = (size[1] - surf.get_height()) / 2
    yoffset = 0
    screen.fill((0, 0, 0))
    screen.blit(surf, (xoffset, yoffset))


def wait_for_key():
    run = True
    while run:
        for event in [pygame.event.wait()] + pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYDOWN:
                run = False


def main():
    global db, cursor
    global size

    db = sqlite3.connect('n1mm_view.db')
    cursor = db.cursor()

    load_data()
    init_display()
    # show_graph(x())
    #show_graph(load_image('logo.png'))
    show_graph(draw_map())
    pygame.display.flip()
    wait_for_key()
    pygame.display.quit()
    db.close()


def zmain():
    map = Basemap()
    map.drawcoastlines()
    plt.show()

if __name__ == '__main__':
    main()
