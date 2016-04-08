#
# useful constants for N1MM mon application
#

# this is all the bands that are supported.
# contest bands only for now.
BANDS_LIST = ['N/A', '1.8', '3.5', '7', '14', '21', '28', '50', '144', '420']
BANDS_TITLE = ['No Band', '160M', '80M', '40M', '20M', '15M', '10M', '6M', '2M', '70cm']
BANDS = {elem: index for index, elem in enumerate(BANDS_LIST)}

# all the modes that are supported
MODES_LIST = ['N/A', 'CW', 'AM', 'FM', 'LSB', 'USB', 'RTTY', 'PSK31', 'PSK63']
MODES = {elem: index for index, elem in enumerate(MODES_LIST)}

# simplified modes to collect CW, PHONE, DATA

SIMPLE_MODES_LIST = ['N/A', 'CW', 'PHONE', 'DATA']
SIMPLE_MODE_POINTS = [0, 2, 1, 2]  # n/a, CW, phone, digital
SIMPLE_MODES = {'N/A': 0, 'CW': 1,
                'AM': 2, 'FM': 2, 'LSB': 2, 'USB': 2,
                'RTTY': 3, 'PSK31': 3, 'PSK63': 3,
                }
