# holds code that returns graphs.
#
#
import calendar
import logging
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.feature.nightshade as nightshade
import cartopy.io.shapereader as shapereader
import matplotlib
import matplotlib.backends.backend_agg as agg
import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.dates import HourLocator, DateFormatter

from config import *
from constants import *

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2019, 2021, 2024 Jeffrey B. Otterson and n1mm_view maintainers'
__license__ = 'Simplified BSD'

RED = pygame.Color('#ff0000')
GREEN = pygame.Color('#33cc33')
BLUE = pygame.Color('#3333cc')
BRIGHT_BLUE = pygame.Color('#6666ff')
YELLOW = pygame.Color('#cccc00')
CYAN = pygame.Color('#00cccc')
MAGENTA = pygame.Color('#cc00cc')
ORANGE = pygame.Color('#ff9900')
BLACK = pygame.Color('#000000')
WHITE = pygame.Color('#ffffff')
GRAY = pygame.Color('#cccccc')

# Initialize font support
pygame.font.init()
view_font = pygame.font.Font('VeraMoBd.ttf', config.VIEW_FONT)
bigger_font = pygame.font.SysFont('VeraMoBd.ttf', config.BIGGER_FONT)
view_font_height = view_font.get_height()

_map = None


def init_display():
    """
    set up the pygame display, full screen
    """

    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    # x11 needed for Raspbian Stretch.  Put fbcon before directfb to not hang composite output
    drivers = ['x11', 'dga', 'fbcon', 'directfb', 'svgalib', 'ggi', 'wayland', 'kmsdrm', 'aalib', 'directx', 'windib',
               'windows']
    found = False
    driver = None
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error as ex:
            logging.warning(f'pygame error {ex}')
            logging.warning('Driver: %s failed.' % driver)
            continue
        found = True
        logging.info('using %s driver', driver)
        break

    if not found or driver is None:
        raise Exception('No suitable video driver found!')

    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    pygame.mouse.set_visible(0)
    if driver != 'directx':  # debugging hack runs in a window on Windows
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    else:
        logging.info('running in windowed mode')
        # set window origin for windowed usage
        os.putenv('SDL_VIDEO_WINDOW_POS', '0,0')
        # size = (size[0]-10, size[1] - 30)
        screen = pygame.display.set_mode(size, pygame.NOFRAME)

    logging.debug('display size: %d x %d', size[0], size[1])
    # Clear the screen to start
    screen.fill(BLACK)
    return screen, size


def show_graph(screen, size, surf):
    """
    display a surface on the screen.
    """
    logging.debug('show_graph()')
    if surf is not None:
        x_offset = (size[0] - surf.get_width()) / 2
        screen.fill((0, 0, 0))
        screen.blit(surf, (x_offset, 0))
    logging.debug('show_graph() done')


def save_image(image_data, image_size, filename):
    surface = pygame.image.frombuffer(image_data, image_size, 'RGB')
    logging.info('Saving file to %s', filename)       
    pygame.image.save(surface, filename)
    pass


def make_pie(size, values, labels, title):
    """
    make a pie chart using matplotlib.
    return the chart as a pygame surface
    make the pie chart a square that is as tall as the display.
    """
    logging.debug('make_pie(...,...,%s)', title)
    inches = size[1] / 100.0
    fig = plt.figure(figsize=(inches, inches), dpi=100, tight_layout={'pad': 0.10}, facecolor='k')
    ax = fig.add_subplot(111)
    ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'color': 'w'}, wedgeprops={'linewidth': 0.25},
           colors=('b', 'g', 'r', 'c', 'm', 'y', '#ff9900', '#00ff00', '#663300'))
    ax.set_title(title, color='white', size=48, weight='bold')

    handles, labels = ax.get_legend_handles_labels()
    legend = ax.legend(handles[0:5], labels[0:5], title='Top %s' % title, loc='lower left')  # best
    frame = legend.get_frame()
    frame.set_color((0, 0, 0, 0.75))
    frame.set_edgecolor('w')
    legend.get_title().set_color('w')
    for text in legend.get_texts():
        plt.setp(text, color='w')

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    plt.close(fig)

    canvas_size = canvas.get_width_height()
    logging.debug('make_pie(...,...,%s) done', title)
    return raw_data, canvas_size


def qso_operators_graph(size, qso_operators):
    """
    create the QSOs by Operators pie chart
    """
    # calculate QSO by Operator
    if qso_operators is None or len(qso_operators) == 0:
        return None, (0, 0)
    labels = []
    values = []
    for d in qso_operators:
        labels.append(d[0])
        values.append(d[1])
    return make_pie(size, values, labels, "QSOs by Operator")


def qso_operators_table(size, qso_operators):
    """
    create the Top 5 QSOs by Operators table
    """
    if len(qso_operators) == 0:
        return None, (0, 0)

    count = 0
    cells = [['Operator', 'QSOs']]
    for d in qso_operators:
        cells.append(['%s' % d[0], '%5d' % d[1]])
        count += 1
        if count >= 5:
            break

    if count == 0:
        return None, (0, 0)
    else:
        return draw_table(size, cells, "Top 5 Operators", bigger_font)

def qso_operators_table_all(size, qso_operators):
    """
    create the QSOs by All Operators table
    """
    if len(qso_operators) == 0:
        return None, (0, 0)

    count = 0
    cells = [['Operator', 'QSOs']]
    for d in qso_operators:
        cells.append(['%s' % d[0], '%5d' % d[1]])
        count += 1

    if count == 0:
        return None, (0, 0)
    else:
        return draw_table(size, cells, "QSOs by All Operators", bigger_font)

def qso_stations_graph(size, qso_stations):
    """
    create the QSOs by Station pie chart
    """
    if qso_stations is None or len(qso_stations) == 0:
        return None, (0, 0)
    labels = []
    values = []
    # for d in qso_stations:
    for d in sorted(qso_stations, key=lambda count: count[1], reverse=True):
        labels.append(d[0])
        values.append(d[1])
    return make_pie(size, values, labels, "QSOs by Station")


def qso_bands_graph(size, qso_band_modes):
    """
    create the QSOs by Band pie chart
    """
    if qso_band_modes is None or len(qso_band_modes) == 0:
        return None, (0, 0)

    labels = []
    values = []
    band_data = [[band, 0] for band in range(0, Bands.count())]
    total = 0
    for i in range(0, Bands.count()):
        band_data[i][1] = qso_band_modes[i][1] + qso_band_modes[i][2] + qso_band_modes[i][3]
        total += band_data[i][1]

    if total == 0:
        return None, (0, 0)

    for bd in sorted(band_data[1:], key=lambda count: count[1], reverse=True):
        if bd[1] > 0:
            labels.append(Bands.BANDS_TITLE[bd[0]])
            values.append(bd[1])
    return make_pie(size, values, labels, "QSOs by Band")


def qso_modes_graph(size, qso_band_modes):
    """
    create the QSOs by Mode pie chart
    """
    if qso_band_modes is None or len(qso_band_modes) == 0:
        return None, (0, 0)

    labels = []
    values = []
    mode_data = [[mode, 0] for mode in range(0, len(Modes.SIMPLE_MODES_LIST))]
    total = 0
    for i in range(0, Bands.count()):
        for mode_num in range(1, len(Modes.SIMPLE_MODES_LIST)):
            mode_data[mode_num][1] += qso_band_modes[i][mode_num]
            total += qso_band_modes[i][mode_num]

    if total == 0:
        return None, (0, 0)

    for md in sorted(mode_data[1:], key=lambda count: count[1], reverse=True):
        if md[1] > 0:
            labels.append(Modes.SIMPLE_MODES_LIST[md[0]])
            values.append(md[1])
    return make_pie(size, values, labels, "QSOs by Mode")


def make_score_table(qso_band_modes):
    """
    create the score table from data
    """
    cell_data = [[0 for m in Modes.SIMPLE_MODES_LIST] for b in Bands.BANDS_TITLE]

    for band_num in range(1, Bands.count()):
        for mode_num in range(1, len(Modes.SIMPLE_MODES_LIST)):
            cell_data[band_num][mode_num] = qso_band_modes[band_num][mode_num]
            cell_data[band_num][0] += qso_band_modes[band_num][mode_num]
            cell_data[0][mode_num] += qso_band_modes[band_num][mode_num]

    total = 0
    for c in cell_data[0][1:]:
        total += c
    cell_data[0][0] = total

    # the totals are in the 0th row and 0th column, move them to last.
    cell_text = [['', '   CW', 'Phone', ' Data', 'Total']]
    band_num = 0
    for row in cell_data[1:]:
        band_num += 1
        row_text = ['%5s' % Bands.BANDS_TITLE[band_num]]

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


def qso_summary_table(size, qso_band_modes):
    """
    create the QSO Summary Table
    """
    return draw_table(size, make_score_table(qso_band_modes), "QSOs Summary")


def qso_rates_table(size, operator_qso_rates):
    """
    create the QSO Rates by Operator table
    """
    if operator_qso_rates is None or len(operator_qso_rates) < 3:
        return None, (0, 0)
    else:
        return draw_table(size, operator_qso_rates, "QSO/Hour Rates")


def qso_rates_chart(size, qsos_per_hour):
    """
    make the qsos per hour per band chart
    returns a pygame surface
    """
    title = 'QSOs per Hour by Band'
    qso_counts = [[], [], [], [], [], [], [], [], [], []]

    if qsos_per_hour is None or len(qsos_per_hour) == 0:
        return None, (0, 0)

    data_valid = len(qsos_per_hour) != 0

    for qpm in qsos_per_hour:
        for i in range(0, Bands.count()):
            c = qpm[i]
            cl = qso_counts[i]
            cl.append(c)

    logging.debug('make_plot(...,...,%s)', title)
    width_inches = size[0] / 100.0
    height_inches = size[1] / 100.0
    fig = plt.Figure(figsize=(width_inches, height_inches), dpi=100, tight_layout={'pad': 0.10}, facecolor='black')

    if matplotlib.__version__[0] == '1':
        ax = fig.add_subplot(111, axis_bgcolor='black')
    else:
        ax = fig.add_subplot(111, facecolor='black')

    ax.set_title(title, color='white', size=48, weight='bold')

    st = calendar.timegm(EVENT_START_TIME.timetuple())
    lt = calendar.timegm(qsos_per_hour[-1][0].timetuple())
    if data_valid:
        dates = matplotlib.dates.date2num(qso_counts[0])
        colors = ['r', 'g', 'b', 'c', 'm', 'y', '#ff9900', '#00ff00', '#663300']
        labels = Bands.BANDS_TITLE[1:]
        if lt < st:
            start_date = dates[0]  # matplotlib.dates.date2num(qsos_per_hour[0][0].timetuple())
            end_date = dates[-1]  # matplotlib.dates.date2num(qsos_per_hour[-1][0].timetuple())
        else:
            start_date = matplotlib.dates.date2num(EVENT_START_TIME)
            end_date = matplotlib.dates.date2num(EVENT_END_TIME)
        ax.set_xlim(start_date, end_date)

        ax.stackplot(dates, qso_counts[1], qso_counts[2], qso_counts[3], qso_counts[4], qso_counts[5], qso_counts[6],
                     qso_counts[7], qso_counts[8], qso_counts[9], labels=labels, colors=colors, linewidth=0.2)
        ax.grid(True)
        legend = ax.legend(loc='best', ncol=Bands.count() - 1)
        legend.get_frame().set_color((0, 0, 0, 0))
        legend.get_frame().set_edgecolor('w')
        for text in legend.get_texts():
            plt.setp(text, color='w')
        ax.spines['left'].set_color('w')
        ax.spines['right'].set_color('w')
        ax.spines['top'].set_color('w')
        ax.spines['bottom'].set_color('w')
        ax.tick_params(axis='y', colors='w')
        ax.tick_params(axis='x', colors='w')
        ax.set_ylabel('QSO Rate/Hour', color='w', size='x-large', weight='bold')
        ax.set_xlabel('UTC Hour', color='w', size='x-large', weight='bold')
        hour_locator = HourLocator()
        hour_formatter = DateFormatter('%H')
        ax.xaxis.set_major_locator(hour_locator)
        ax.xaxis.set_major_formatter(hour_formatter)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    plt.close(fig)
    canvas_size = canvas.get_width_height()
    return raw_data, canvas_size


def draw_table(size, cell_text, title, font=None):
    """
    draw a table
    """
    logging.debug('draw_table(...,%s)', title)
    if font is None:
        table_font = view_font
    else:
        table_font = font

    text_y_offset = 4
    text_x_offset = 4
    line_width = 4

    # calculate column widths
    rows = len(cell_text)
    cols = len(cell_text[0])
    col_widths = [0] * cols
    widest = 0
    for row in cell_text:
        col_num = 0
        for col in row:
            text_size = table_font.size(col)
            text_width = text_size[0] + 2 * text_x_offset
            if text_width > col_widths[col_num]:
                col_widths[col_num] = text_width
            if text_width > widest:
                widest = text_width
            col_num += 1

    header_width = table_font.size(title)[0]
    table_width = sum(col_widths) + line_width / 2
    row_height = table_font.get_height()
    height = (rows + 1) * row_height + line_width / 2
    surface_width = table_width
    x_offset = 0
    if header_width > surface_width:
        surface_width = header_width
        x_offset = (header_width - table_width) / 2

    surf = pygame.Surface((surface_width, height))

    surf.fill(BLACK)
    text_color = GRAY
    head_color = WHITE
    grid_color = GRAY

    # draw the title
    text = table_font.render(title, True, head_color)
    textpos = text.get_rect()
    textpos.y = 0
    textpos.centerx = surface_width / 2
    surf.blit(text, textpos)

    starty = row_height
    origin = (x_offset, row_height)

    # draw the grid
    x = x_offset
    y = starty
    for r in range(0, rows + 1):
        sp = (x, y)
        ep = (x + table_width, y)
        pygame.draw.line(surf, grid_color, sp, ep, line_width)
        y += row_height

    x = x_offset
    y = starty
    for cw in col_widths:
        sp = (x, y)
        ep = (x, y + height)
        pygame.draw.line(surf, grid_color, sp, ep, line_width)
        x += cw
    sp = (x, y)
    ep = (x, y + height)
    pygame.draw.line(surf, grid_color, sp, ep, line_width)

    y = starty + text_y_offset
    row_number = 0
    for row in cell_text:
        row_number += 1
        x = origin[0]
        column_number = 0
        for col in row:
            x += col_widths[column_number]
            column_number += 1
            if row_number == 1 or column_number == 1:
                text = table_font.render(col, True, head_color)
            else:
                text = table_font.render(col, True, text_color)
            textpos = text.get_rect()
            textpos.y = y - text_y_offset
            textpos.right = x - text_x_offset
            surf.blit(text, textpos)
        y += row_height
    logging.debug('draw_table(...,%s) done', title)
    size = surf.get_size()
    data = pygame.image.tostring(surf, 'RGB')

    return data, size


def draw_map(size, qsos_by_section):
    """
    make the choropleth with Cartopy & section shapefiles
    """
    logging.debug('draw_section map()')
    width_inches = size[0] / 100.0
    height_inches = size[1] / 100.0
    fig = plt.Figure(figsize=(width_inches, height_inches), dpi=100, facecolor='black')

    projection = ccrs.PlateCarree()
    ax = fig.add_axes([0, 0, 1, 1], projection=projection)
    ax.set_extent([-168, -52, 10, 60], ccrs.Geodetic())
    ax.add_feature(cfeature.OCEAN, color='#000080')
    ax.add_feature(cfeature.LAKES, color='#000080')
    ax.add_feature(cfeature.LAND, color='#113311')

    ax.coastlines('50m')
    ax.annotate('Sections Worked', xy=(0.5, 1), xycoords='axes fraction', ha='center', va='top',
                color='white', size=48, weight='bold')
    
    ax.text(0.83, 0, datetime.datetime.utcnow().strftime("%d %b %Y %H:%M %Zz"),
            transform=ax.transAxes, style='italic', size=14, color='white')
    ranges = [0, 1, 2, 10, 20, 50, 100]  # , 500]  # , 1000]
    num_colors = len(ranges)
    color_palette = matplotlib.cm.viridis(np.linspace(0.33, 1, num_colors + 1))

    for section_name in CONTEST_SECTIONS.keys():
        qsos = qsos_by_section.get(section_name)
        if qsos is None:
            qsos = 0

        color_index = 0
        for range_max in ranges:
            if range_max == -1 or qsos <= range_max:
                break
            color_index += 1
            if color_index == num_colors:
                break

        shape_file_name = 'shapes/{}.shp'.format(section_name)
        reader = shapereader.Reader(shape_file_name)
        shapes = reader.records()
        while True:
            shape = next(shapes, None)
            if shape is None:
                break
            shape.attributes['name'] = section_name
            section_color = 'k' if color_index == 0 else color_palette[color_index]
            ax.add_geometries([shape.geometry], projection, linewidth=0.7, edgecolor="w", facecolor=section_color)

    # show terminator
    date = datetime.datetime.utcnow()  # this might have some timezone problems?
    ax.add_feature(nightshade.Nightshade(date, alpha=0.5))

    # show QTH marker
    ax.plot(QTH_LONGITUDE, QTH_LATITUDE, '.', color='r')

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    fig.clf()
    plt.close(fig)
    canvas_size = canvas.get_width_height()
    logging.debug('draw_map() done')
    return raw_data, canvas_size
