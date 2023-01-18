"""
this file contains useful constants for n1mm_view application.
"""

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2020 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

import time
import logging
import config

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.LOG_LEVEL)
logging.Formatter.converter = time.gmtime

class Bands:
    """
    this is all the bands that are supported.
    contest bands only for now.
    """

    BANDS_LIST = ['N/A', '1.8', '3.5', '7', '14', '21', '28', '50', '144', '420']
    BANDS_TITLE = ['No Band', '160M', '80M', '40M', '20M', '15M', '10M', '6M', '2M', '70cm']
    BANDS = {elem: index for index, elem in enumerate(BANDS_LIST)}

    @classmethod
    def get_band_number(cls, band_name):
        return Bands.BANDS.get(band_name)

    @classmethod
    def count(cls):
        return len(Bands.BANDS_LIST)


class Modes:
    """
    all the modes that are supported.
    """
    MODES_LIST = ['N/A', 'CW', 'AM', 'FM', 'LSB', 'USB', 'RTTY', 'PSK31', 'PSK63', 'FT8', 'FT4']
    MODES = {elem: index for index, elem in enumerate(MODES_LIST)}

    """
    simplified modes for score reporting: CW, PHONE, DATA
    """
    SIMPLE_MODES_LIST = ['N/A', 'CW', 'PHONE', 'DATA']
    MODE_TO_SIMPLE_MODE = [0, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3]
    SIMPLE_MODE_POINTS = [0, 2, 1, 2]  # n/a, CW, phone, digital
    SIMPLE_MODES = {'N/A': 0, 'CW': 1,
                    'AM': 2, 'FM': 2, 'LSB': 2, 'USB': 2,
                    'RTTY': 3, 'PSK31': 3, 'PSK63': 3, 'FT8': 3, 'FT4': 3, 'MFSK': 3,
                    }

    @classmethod
    def get_mode_number(cls, mode_name):
        mode_number = Modes.MODES.get(mode_name)
        if mode_number is None:
            logging.warning('unknown mode {}'.format(mode_name))
            mode_number = 0
        return mode_number

    @classmethod
    def count(cls):
        return len(Modes.MODES)

    @classmethod
    def get_simple_mode_number(cls, mode_name):
        return Modes.SIMPLE_MODES.get(mode_name)


"""
Every section that is valid for field day, except "DX"
"""
CONTEST_SECTIONS = {
    'AB': 'Alberta',
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'BC': 'British Columbia',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'EB': 'East Bay',
    'EMA': 'Eastern Massachusetts',
    'ENY': 'Eastern New York',
    'EPA': 'Eastern Pennsylvania',
    'EWA': 'Eastern Washington',
    'GA': 'Georgia',
    'GTA': 'Greater Toronto Area',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'LAX': 'Los Angeles',
    # 'MAR': 'Maritime',  # OBSOLETE 2023-01-01
    'MB': 'Manitoba',
    'MDC': 'Maryland - DC',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NB': 'New Brunswick',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NFL': 'Northern Florida',
    'NH': 'New Hampshire',
    'NLI': 'New York City - Long Island',
    'NL': 'Newfoundland/Labrador',
    'NM': 'New Mexico',
    'NNJ': 'Northern New Jersey',
    'NNY': 'Northern New York',
    'NS': 'Nova Scotia',
    'NT': 'Northern Territories',
    'NTX': 'North Texas',
    'NV': 'Nevada',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'ONE': 'Ontario East',
    'ONN': 'Ontario North',
    'ONS': 'Ontario South',
    'ORG': 'Orange',
    'OR': 'Oregon',
    'PAC': 'Pacific',
    'PE': 'Prince Edward Island',
    'PR': 'Puerto Rico',
    'QC': 'Quebec',
    'RI': 'Rhode Island',
    'SB': 'Santa Barbara',
    'SC': 'South Carolina',
    'SCV': 'Santa Clara Valley',
    'SDG': 'San Diego',
    'SD': 'South Dakota',
    'SFL': 'Southern Florida',
    'SF': 'San Francisco',
    'SJV': 'San Joaquin Valley',
    'SK': 'Saskatchewan',
    'SNJ': 'Southern New Jersey',
    'STX': 'South Texas',
    'SV': 'Sacramento Valley',
    'TN': 'Tennessee',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WCF': 'West Central Florida',
    'WI': 'Wisconsin',
    'WMA': 'Western Massachusetts',
    'WNY': 'Western New York',
    'WPA': 'Western Pennsylvania',
    'WTX': 'West Texas',
    'WV': 'West Virginia',
    'WWA': 'Western Washington',
    'WY': 'Wyoming',
}
