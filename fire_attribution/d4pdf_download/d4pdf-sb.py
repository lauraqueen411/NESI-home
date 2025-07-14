#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import optparse
import netrc
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import http.cookiejar
import html.parser
import getpass

class CASLoginParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.action = None
        self.data = {}

    def handle_starttag(self, tagname, attribute):
        if tagname.lower() == 'form':
            attribute = dict(attribute)
            if 'action' in attribute:
                self.action = attribute['action']
        elif tagname.lower() == 'input':
            attribute = dict(attribute)
            if 'name' in attribute and 'value' in attribute:
                self.data[attribute['name']] = attribute['value']

class DIASAccess():
    def __init__(self, username, password):
        self.__cas_url = 'https://auth.diasjp.net/cas/login?'
        self.__username = username
        self.__password = password
        cj = http.cookiejar.CookieJar()
        self.__opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def open(self, url, data=None):
        response = self.__opener.open(url, data)
        response_url = response.geturl()

        if response_url != url and response_url.startswith(self.__cas_url):
            # redirected to CAS login page
            response = self.__login_cas(response)
            if data != None:
                # If POST (data != None), need reopen
                response.close()
                response = self.__opener.open(url, data)

        return response

    def __login_cas(self, response):
        parser = CASLoginParser()
        parser.feed(str(response.read()))
        parser.close()

        if parser.action == None:
            raise LoginError('Not login page')

        action_url = urllib.parse.urljoin(response.geturl(), parser.action)
        data = parser.data
        data['username'] = self.__username
        data['password'] = self.__password

        response.close()
        response = self.__opener.open(action_url, 
                                      urllib.parse.urlencode(data).encode('utf-8'))

        if response.geturl() == action_url:
            raise LoginError('Authorization fail')

        return response

class LoginError(Exception):
    def __init__(self, e):
        Exception.__init__(self, e)

x_25deg = [x * 2.5 for x in range(144)]
x_125deg = [x * 1.25 for x in range(288)]
x_tl319 = [x * 0.5625 for x in range(640)]
x_zonal = [None]
x_japan = [x * 0.56250 + 119.81250 for x in range(55)]
x_gcm_regional = [x * 0.56250 + 104.62500 for x in range(118)]
x_regional = [None] * 191

y_25deg = [y * 2.5 - 90.0 for y in range(73)]
y_125deg = [y * 1.25 - 90.0 for y in range(145)]
y_tl319 = [-89.57009, -89.01318, -88.45297, -87.89203, -87.33080,
           -86.76944, -86.20800, -85.64651, -85.08499, -84.52345,
           -83.96190, -83.40033, -82.83876, -82.27718, -81.71559,
           -81.15400, -80.59240, -80.03080, -79.46920, -78.90760,
           -78.34600, -77.78439, -77.22278, -76.66117, -76.09956,
           -75.53795, -74.97634, -74.41473, -73.85311, -73.29150,
           -72.72988, -72.16827, -71.60665, -71.04504, -70.48342,
           -69.92181, -69.36019, -68.79857, -68.23695, -67.67534,
           -67.11372, -66.55210, -65.99048, -65.42886, -64.86725,
           -64.30563, -63.74401, -63.18239, -62.62077, -62.05915,
           -61.49753, -60.93591, -60.37429, -59.81267, -59.25105,
           -58.68943, -58.12781, -57.56619, -57.00457, -56.44295,
           -55.88133, -55.31971, -54.75809, -54.19647, -53.63485,
           -53.07323, -52.51161, -51.94999, -51.38837, -50.82675,
           -50.26513, -49.70351, -49.14189, -48.58026, -48.01864,
           -47.45702, -46.89540, -46.33378, -45.77216, -45.21054,
           -44.64892, -44.08730, -43.52567, -42.96405, -42.40243,
           -41.84081, -41.27919, -40.71757, -40.15595, -39.59433,
           -39.03270, -38.47108, -37.90946, -37.34784, -36.78622,
           -36.22460, -35.66298, -35.10136, -34.53973, -33.97811,
           -33.41649, -32.85487, -32.29325, -31.73163, -31.17000,
           -30.60838, -30.04676, -29.48514, -28.92352, -28.36190,
           -27.80028, -27.23865, -26.67703, -26.11541, -25.55379,
           -24.99217, -24.43055, -23.86892, -23.30730, -22.74568,
           -22.18406, -21.62244, -21.06082, -20.49919, -19.93757,
           -19.37595, -18.81433, -18.25271, -17.69109, -17.12946,
           -16.56784, -16.00622, -15.44460, -14.88298, -14.32136,
           -13.75973, -13.19811, -12.63649, -12.07487, -11.51325,
           -10.95162, -10.39000,  -9.82838,  -9.26676,  -8.70514,
            -8.14352,  -7.58189,  -7.02027,  -6.45865,  -5.89703,
            -5.33541,  -4.77379,  -4.21216,  -3.65054,  -3.08892,
            -2.52730,  -1.96568,  -1.40405,  -0.84243,  -0.28081,
             0.28081,   0.84243,   1.40405,   1.96568,   2.52730,
             3.08892,   3.65054,   4.21216,   4.77379,   5.33541,
             5.89703,   6.45865,   7.02027,   7.58189,   8.14352,
             8.70514,   9.26676,   9.82838,  10.39000,  10.95162,
            11.51325,  12.07487,  12.63649,  13.19811,  13.75973,
            14.32136,  14.88298,  15.44460,  16.00622,  16.56784,
            17.12946,  17.69109,  18.25271,  18.81433,  19.37595,
            19.93757,  20.49919,  21.06082,  21.62244,  22.18406,
            22.74568,  23.30730,  23.86892,  24.43055,  24.99217,
            25.55379,  26.11541,  26.67703,  27.23865,  27.80028,
            28.36190,  28.92352,  29.48514,  30.04676,  30.60838,
            31.17000,  31.73163,  32.29325,  32.85487,  33.41649,
            33.97811,  34.53973,  35.10136,  35.66298,  36.22460,
            36.78622,  37.34784,  37.90946,  38.47108,  39.03270,
            39.59433,  40.15595,  40.71757,  41.27919,  41.84081,
            42.40243,  42.96405,  43.52567,  44.08730,  44.64892,
            45.21054,  45.77216,  46.33378,  46.89540,  47.45702,
            48.01864,  48.58026,  49.14189,  49.70351,  50.26513,
            50.82675,  51.38837,  51.94999,  52.51161,  53.07323,
            53.63485,  54.19647,  54.75809,  55.31971,  55.88133,
            56.44295,  57.00457,  57.56619,  58.12781,  58.68943,
            59.25105,  59.81267,  60.37429,  60.93591,  61.49753,
            62.05915,  62.62077,  63.18239,  63.74401,  64.30563,
            64.86725,  65.42886,  65.99048,  66.55210,  67.11372,
            67.67534,  68.23695,  68.79857,  69.36019,  69.92181,
            70.48342,  71.04504,  71.60665,  72.16827,  72.72988,
            73.29150,  73.85311,  74.41473,  74.97634,  75.53795,
            76.09956,  76.66117,  77.22278,  77.78439,  78.34600,
            78.90760,  79.46920,  80.03080,  80.59240,  81.15400,
            81.71559,  82.27718,  82.83876,  83.40033,  83.96190,
            84.52345,  85.08499,  85.64651,  86.20800,  86.76944,
            87.33080,  87.89203,  88.45297,  89.01318,  89.57009]
y_zonal = y_tl319
y_japan = [ 19.93757,  20.49919,  21.06082,  21.62244,  22.18406,
            22.74568,  23.30730,  23.86892,  24.43055,  24.99217,
            25.55379,  26.11541,  26.67703,  27.23865,  27.80028,
            28.36190,  28.92352,  29.48514,  30.04676,  30.60838,
            31.17000,  31.73163,  32.29325,  32.85487,  33.41649,
            33.97811,  34.53973,  35.10136,  35.66298,  36.22460,
            36.78622,  37.34784,  37.90946,  38.47108,  39.03270,
            39.59433,  40.15595,  40.71757,  41.27919,  41.84081,
            42.40243,  42.96405,  43.52567,  44.08730,  44.64892,
            45.21054,  45.77216,  46.33378,  46.89540,  47.45702,
            48.01864,  48.58026,  49.14189,  49.70351,  50.26513]
y_gcm_regional = [  9.82838,  10.39000,  10.95162,  11.51325,  12.07487,
                   12.63649,  13.19811,  13.75973,  14.32136,  14.88298,
                   15.44460,  16.00622,  16.56784,  17.12946,  17.69109,
                   18.25271,  18.81433,  19.37595,  19.93757,  20.49919,
                   21.06082,  21.62244,  22.18406,  22.74568,  23.30730,
                   23.86892,  24.43055,  24.99217,  25.55379,  26.11541,
                   26.67703,  27.23865,  27.80028,  28.36190,  28.92352,
                   29.48514,  30.04676,  30.60838,  31.17000,  31.73163,
                   32.29325,  32.85487,  33.41649,  33.97811,  34.53973, 
                   35.10136,  35.66298,  36.22460,  36.78622,  37.34784,
                   37.90946,  38.47108,  39.03270,  39.59433,  40.15595,
                   40.71757,  41.27919,  41.84081,  42.40243,  42.96405,
                   43.52567,  44.08730,  44.64892,  45.21054,  45.77216,
                   46.33378,  46.89540,  47.45702,  48.01864,  48.58026,
                   49.14189,  49.70351,  50.26513,  50.82675,  51.38837,
                   51.94999,  52.51161,  53.07323,  53.63485,  54.19647,
                   54.75809,  55.31971,  55.88133,  56.44295,  57.00457,
                   57.56619,  58.12781,  58.68943,  59.25105,  59.81267,
                   60.37429,  60.93591,  61.49753,  62.05915,  62.62077,
                   63.18239,  63.74401,  64.30563,  64.86725,  65.42886]
y_regional = [None] * 155

ensembles = {'GCM_HPB': ['m001', 'm002', 'm003', 'm004', 'm005',
                         'm006', 'm007', 'm008', 'm009', 'm010',
                         'm011', 'm012', 'm013', 'm014', 'm015',
                         'm016', 'm017', 'm018', 'm019', 'm020',
                         'm021', 'm022', 'm023', 'm024', 'm025',
                         'm026', 'm027', 'm028', 'm029', 'm030',
                         'm031', 'm032', 'm033', 'm034', 'm035',
                         'm036', 'm037', 'm038', 'm039', 'm040',
                         'm041', 'm042', 'm043', 'm044', 'm045',
                         'm046', 'm047', 'm048', 'm049', 'm050',
                         'm051', 'm052', 'm053', 'm054', 'm055',
                         'm056', 'm057', 'm058', 'm059', 'm060',
                         'm061', 'm062', 'm063', 'm064', 'm065',
                         'm066', 'm067', 'm068', 'm069', 'm070',
                         'm071', 'm072', 'm073', 'm074', 'm075',
                         'm076', 'm077', 'm078', 'm079', 'm080',
                         'm081', 'm082', 'm083', 'm084', 'm085',
                         'm086', 'm087', 'm088', 'm089', 'm090',
                         'm091', 'm092', 'm093', 'm094', 'm095',
                         'm096', 'm097', 'm098', 'm099', 'm100'],
             'GCM_HFB_4K': ['m101', 'm102', 'm103', 'm104', 'm105',
                            'm106', 'm107', 'm108', 'm109', 'm110',
                            'm111', 'm112', 'm113', 'm114', 'm115'],
             'GCM_HFB_2K': ['m101', 'm102', 'm103', 'm104', 'm105',
                            'm106', 'm107', 'm108', 'm109'],
             'GCM_HFB_1.5K': ['m001', 'm002', 'm003', 'm004', 'm005',
                              'm006', 'm007', 'm008', 'm009'],
             'RCM_HPB': ['m001', 'm002', 'm003', 'm004', 'm005',
                         'm006', 'm007', 'm008', 'm009', 'm010',
                         'm021', 'm022', 'm023', 'm024', 'm025',
                         'm026', 'm027', 'm028', 'm029', 'm030',
                         'm041', 'm042', 'm043', 'm044', 'm045',
                         'm046', 'm047', 'm048', 'm049', 'm050',
                         'm061', 'm062', 'm063', 'm064', 'm065',
                         'm066', 'm067', 'm068', 'm069', 'm070',
                         'm081', 'm082', 'm083', 'm084', 'm085',
                         'm086', 'm087', 'm088', 'm089', 'm090'],
             'RCM_HFB_4K': ['m101', 'm102', 'm103', 'm104', 'm105',
                            'm106', 'm107', 'm108', 'm109', 'm110',
                            'm111', 'm112', 'm113', 'm114', 'm115'],
             'RCM_HFB_2K': ['m101', 'm102', 'm103', 'm104', 'm105',
                            'm106', 'm107', 'm108', 'm109'],
             'RCM_HFB_1.5K': ['m001', 'm002', 'm003', 'm004', 'm005',
                              'm006', 'm007', 'm008', 'm009']}

category_gcm_base = {
    'atm_avr_mon_1.25deg':	{'x': x_125deg,
                                 'y': y_125deg,
                                 'z': 24,
                                 't': '1mo',
                                 'byte': 4},
    'atm_zonal_avr_mon':	{'x': x_zonal,
                                 'y': y_zonal,
                                 'z': 24,
                                 't': '1mo',
                                 'byte': 4},
    'precipi_avr_1hr':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1hr',
                                 'byte': 4},
    'sfc_avr_3hr':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '3hr',
                                 'byte': 4},
    'sfc_avr_day':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1dy',
                                 'byte': 4},
    'sfc_avr_mon':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1mo',
                                 'byte': 4},
    'sfc_japan_avr_1hr':	{'x': x_japan,
                                 'y': y_japan,
                                 'z': 1,
                                 't': '1hr',
                                 'byte': 4},
    'sfc_max_day':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1dy',
                                 'byte': 4},
    'sfc_min_day':		{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1dy',
                                 'byte': 4},
    'sfc_souseid_avr_day':	{'x': x_tl319,
                                 'y': y_tl319,
                                 'z': 1,
                                 't': '1dy',
                                 'byte': 4}}
category_gcm_general = category_gcm_base.copy()
category_gcm_general.update({
    'atm_24levs_snp_12hr_2.5deg':	{'x': x_25deg,
                                         'y': y_25deg,
                                         'z': 24,
                                         't': '12hr',
                                         'byte': 4},
    'atm_snp_6hr_1.25deg':		{'x': x_125deg,
                                         'y': y_125deg,
                                         'z': 12,
                                         't': '6hr',
                                         'byte': 4},
    'atm_snp_6hr_2byte':		{'x': x_tl319,
                                         'y': y_tl319,
                                         'z': 1,
                                         't': '6hr',
                                         'byte': 2},
    'epflux_avr_day':			{'x': x_zonal,
                                         'y': y_zonal,
                                         'z': 24,
                                         't': '1dy',
                                         'byte': 4},
    'sfc_avr_6hr_1.25deg':		{'x': x_125deg,
                                         'y': y_125deg,
                                         'z': 1,
                                         't': '6hr',
                                         'byte': 4},
    'sfc_snp_6hr_2byte':		{'x': x_tl319,
                                         'y': y_tl319,
                                         'z': 1,
                                         't': '6hr',
                                         'byte': 2}})
category_gcm_1_5K = category_gcm_base.copy()
category_gcm_1_5K.update({
    'atm_avr_mon':			{'x': x_tl319,
                                         'y': y_tl319,
                                         'z': 24,
                                         't': '1mo',
                                         'byte': 4},
    'sfc_avr_6hr':			{'x': x_tl319,
                                         'y': y_tl319,
                                         'z': 1,
                                         't': '6hr',
                                         'byte': 4},
    'atm_eta_regional_snp_6hr':		{'x': x_gcm_regional,
                                         'y': y_gcm_regional,
                                         'z': 47,
                                         't': '6hr',
                                         'byte': 4},
    'sfc_regional_snp_6hr':		{'x': x_gcm_regional,
                                         'y': y_gcm_regional,
                                         'z': 1,
                                         't': '6hr',
                                         'byte': 4}})
category_rcm_base = {
    'ph2m':                             {'x': x_regional,
                                         'y': y_regional,
                                         'z': 1,
                                         't': '1hr',
                                         'byte': 4},
    'sib':                              {'x': x_regional,
                                         'y': y_regional,
                                         'z': 1,
                                         't': '1hr',
                                         'byte': 4},
    'surf':                             {'x': x_regional,
                                         'y': y_regional,
                                         'z': 1,
                                         't': '1hr',
                                         'byte': 4}}
category_rcm_general = category_rcm_base.copy()
category_rcm_general.update({
    'dx20_3d':				{'x': x_regional,
                                         'y': y_regional,
                                         'z': 40,
                                         't': '6hr',
                                         'byte': 4}})
category_rcm_1_5K = category_rcm_base.copy()

inventory = {'GCM': {'HPB': {'ensemble': ensembles['GCM_HPB'],
                             'category': category_gcm_general,
                             'start': 195101,
                             'end': 201112},
                     'HPB_NAT': {'ensemble': ensembles['GCM_HPB'],
                                 'category': category_gcm_general,
                                 'start': 195101,
                                 'end': 201012},
                     'HFB_4K_CC' : {'ensemble': ensembles['GCM_HFB_4K'],
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_4K_GF' : {'ensemble': ensembles['GCM_HFB_4K'], 
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_4K_HA' : {'ensemble': ensembles['GCM_HFB_4K'],
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_4K_MI' : {'ensemble': ensembles['GCM_HFB_4K'],
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_4K_MP' : {'ensemble': ensembles['GCM_HFB_4K'],
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_4K_MR' : {'ensemble': ensembles['GCM_HFB_4K'],
                                    'category': category_gcm_general,
                                    'start': 205101,
                                    'end': 211112},
                     'HFB_2K_CC' : {'ensemble': ensembles['GCM_HFB_2K'],
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_2K_GF' : {'ensemble': ensembles['GCM_HFB_2K'], 
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_2K_HA' : {'ensemble': ensembles['GCM_HFB_2K'],
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_2K_MI' : {'ensemble': ensembles['GCM_HFB_2K'],
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_2K_MP' : {'ensemble': ensembles['GCM_HFB_2K'],
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_2K_MR' : {'ensemble': ensembles['GCM_HFB_2K'],
                                    'category': category_gcm_general,
                                    'start': 203101,
                                    'end': 209112},
                     'HFB_1.5K_CC' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012},
                     'HFB_1.5K_GF' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012},
                     'HFB_1.5K_HA' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012},
                     'HFB_1.5K_MI' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012},
                     'HFB_1.5K_MP' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012},
                     'HFB_1.5K_MR' : {'ensemble': ensembles['GCM_HFB_1.5K'],
                                      'category': category_gcm_1_5K,
                                      'start': 207801,
                                      'end': 211012}},
             'RCM': {'HPB' : {'ensemble': ensembles['RCM_HPB'],
                              'category': category_rcm_general,
                              'start': 195009,
                              'end': 201108},
                     'HFB_4K_CC' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_4K_GF' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_4K_HA' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_4K_MI' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_4K_MP' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_4K_MR' : {'ensemble': ensembles['RCM_HFB_4K'],
                                    'category': category_rcm_general,
                                    'start': 205009,
                                    'end': 211108},
                     'HFB_2K_CC' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_2K_GF' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_2K_HA' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_2K_MI' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_2K_MP' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_2K_MR' : {'ensemble': ensembles['RCM_HFB_2K'],
                                    'category': category_rcm_general,
                                    'start': 203009,
                                    'end': 209108},
                     'HFB_1.5K_CC' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008},
                     'HFB_1.5K_GF' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008},
                     'HFB_1.5K_HA' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008},
                     'HFB_1.5K_MI' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008},
                     'HFB_1.5K_MP' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008},
                     'HFB_1.5K_MR' : {'ensemble': ensembles['RCM_HFB_1.5K'],
                                    'category': category_rcm_1_5K,
                                    'start': 208009,
                                    'end': 211008}}}

variables = {
    'GCM': {
        'atm_avr_mon_1.25deg': [
            'U',
            'V',
            'OMEGA',
            'Z',
            'T',
            'Q',
            'RH',
            'CVR',
            'CWC',
            'RSHRT',
            'RLONG',
            'QU',
            'QV',
            'OZON',
            'UU',
            'VV',
            'UV',
            'WMSK'],
        'atm_avr_mon': [
            'U',
            'V',
            'OMEGA',
            'Z',
            'T',
            'Q',
            'RH',
            'CVR',
            'CWC',
            'RSHRT',
            'RLONG',
            'QU',
            'QV',
            'OZON',
            'UU',
            'VV',
            'UV',
            'WMSK'],
        'atm_zonal_avr_mon': [
            'U',
            'V',
            'OMEGA',
            'Z',
            'T',
            'Q',
            'RH',
            'CVR',
            'CWC',
            'RSHRT',
            'RLONG',
            'QU',
            'QV',
            'OZON',
            'UU',
            'VV',
            'UV',
            'WMSK'],
        'precipi_avr_1hr': [
            'PRECIPI'],
        'sfc_avr_3hr': [
            'ROF',
            'ROFS'],
        'sfc_avr_6hr_1.25deg': [
            'PRECIPI',
            'PPCI',
            'FLSH',
            'FLLH',
            'ULWT'],
        'sfc_avr_6hr': [
            'PRECIPI',
            'PPCI',
            'FLSH',
            'FLLH',
            'ULWT'],
        'sfc_avr_day': [
            'TA',
            'PRECIPI'],
        'sfc_avr_mon': [
            'TA',
            'TGEF',
            'SLP',
            'PS',
            'UA',
            'VA',
            'WIND',
            'RHA',
            'QA',
            'PRECIPI',
            'SNP',
            'PPCI',
            'EVSPS',
            'UMOM',
            'VMOM',
            'FLLH',
            'FLSH',
            'DLWB',
            'ULWB',
            'DSWB',
            'USWB',
            'CSDSWB',
            'CSUSWB',
            'CSDLWB',
            'DSWT',
            'USWT',
            'ULWT',
            'CSULWT',
            'CSUSWT',
            'PWATER',
            'TCLOUD',
            'TCWC',
            'WSL010',
            'H2OSLT',
            'ROFS',
            'ROF',
            'EVDWVEG',
            'EVDWSL',
            'TRNSL',
            'H2OSL1',
            'H2OSL2',
            'H2OSL3',
            'TMPSL1',
            'TMPSL2',
            'TMPSL3',
            'TMPSL4',
            'CVRSNWA',
            'SWE',
            'DEPSNW',
            'TMPSNW',
            'EVDWSN',
            'SN2SL',
            'AICE',
            'YICE',
            'YSNW',
            'VINTQU',
            'VINTQV',
            'TOTALHP',
            'TOTALHM'],
        'sfc_japan_avr_1hr': [
            'SLP',
            'UAOPN',
            'VAOPN',
            'TA',
            'QA',
            'DLWB',
            'DSWB',
            'TCLOUD'],
        'sfc_max_day': [
            'TA',
            'RHA',
            'WIND'],
        'sfc_min_day': [
            'TA',
            'RHA'],
        'sfc_snp_6hr_2byte': [
            'SLP',
            'UAOPN',
            'VAOPN',
            'TA',
            'QA',
            'PS',
            'PRECIPI'],
        'sfc_souseid_avr_day': [
            'TMPGRD',
            'WIND',
            'RHA',
            'TCLOUD',
            'FLLH',
            'TRNSL',
            'EVPSL',
            'PRCSL',
            'SN2SL',
            'H2OSL1',
            'H2OSL2',
            'H2OSL3',
            'SWE'],
        'atm_24levs_snp_12hr_2.5deg': [
            'U',
            'V',
            'T',
            'Z',
            'OMEGA'],
        'atm_snp_6hr_1.25deg': [
            'U',
            'V',
            'T',
            'Q',
            'Z',
            'CWC',
            'OMEGA'],
        'atm_snp_6hr_2byte': [
            'U850',
            'U700',
            'U500',
            'U300',
            'V850',
            'V700',
            'V500',
            'V300',
            'T850',
            'T700',
            'T500',
            'T300',
            'OMG700',
            'OMG500'],
        'epflux_avr_day': [
            'U',
            'V',
            'T',
            'OMEGA',
            'UV',
            'VT',
            'WU',
            'U_V',
            'V_T',
            'W_U'],
        'atm_eta_regional_snp_6hr': [
            'U',
            'V',
            'T',
            'Q'],
        'sfc_regional_snp_6hr': [
            'TSEAS',
            'TMPSL1',
            'TMPSL2',
            'TMPSL3',
            'TMPSL4',
            'TMPGRD',
            'PS',
            'WETSL1',
            'WETSL2',
            'WETSL3',
            'Z0']},
    'RCM': {
        'surf': [
            'smqr',
            'smqi',
            'smqs',
            'smqg',
            'smqh',
            'rain',
            'psea',
            'psurf',
            'u',
            'v',
            'u+v',
            'tmp',
            'ttd',
            'cll',
            'clm',
            'clh',
            'cla',
            'tpw'],
        'ph2m': [
            'w_g1',
            'w_g2',
            'uflsh',
            'ufllh',
            'ursdb',
            'ursub',
            'urldb',
            'urlub',
            'urbeam',
            'urdiff',
            'usolar',
            'qvgrd',
            'tin1',
            'tin2',
            'tin3',
            'tin4',
            'a_tsfc',
            'i_tsfc',
            'a_vel'],
        'sib': [
            'tsc',
            'tsg',
            'tss',
            'tsd1',
            'tsd2',
            'tsd3',
            'sw1',
            'sw2',
            'sw3',
            'si1',
            'si2',
            'si3',
            'tss1',
            'rofs',
            'rofb',
            'ltrs',
            'lint',
            'lsbl',
            'snmt',
            'wtr_s1',
            'wtr_s2',
            'wtr_s3',
            'wtr_s4',
            'swe_s1',
            'swe_s2',
            'swe_s3',
            'swe_s4',
            'swe_t',
            'sndep'],
        'dx20_3d': [
            'DNSG2',
            'U',
            'V',
            'W',
            'PT',
            'TIN',
            'TSD4',
            'CVRS',
            'QV',
            'W_G',
            'QC',
            'QR',
            'ETURB',
            'PTSQ',
            'QWSQ',
            'PTQW',
            'PRS',
            'QCI',
            'QS',
            'QG',
            'PSEA']}}

if __name__ == '__main__':
    usage = '''
  %prog [options] {GCM|RCM}/experiment/category variable [variable...]
  %prog --target
  %prog --variable {GCM|RCM}/experiment/category'''
    version = '%prog 21.1215'
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-f', '--from', dest='start',
                      help='specify the start time of period',
                      metavar='YYYY-MM')
    parser.add_option('-t', '--to', dest='end',
                      help='specify the end time of period',
                      metavar='YYYY-MM')
    parser.add_option('-e', '--ensemble', action='append',
                      help='specify the ensemble member',
                      metavar='NNN')
    parser.add_option('-X', dest='x',
                      help='specify the x range', metavar='Xs,Xe')
    parser.add_option('-Y', dest='y',
                      help='specify the y range', metavar='Ys,Ye')
    parser.add_option('-W', '--west', dest='west', type='float',
                      help='specify the west longitude (only for GCM)',
                      metavar='Longitude')
    parser.add_option('-E', '--east', dest='east', type='float',
                      help='specify the east longitude (only for GCM)',
                      metavar='Longitude')
    parser.add_option('-S', '--south', dest='south', type='float',
                      help='specify the south latitude (only for GCM)',
                      metavar='Latitude')
    parser.add_option('-N', '--north', dest='north', type='float',
                      help='specify the north latitude (only for GCM)',
                      metavar='Latitude')
    parser.add_option('-o', '--output',
                      help='specify the output file', 
                      metavar='FILE')
    parser.add_option('-n', '--netrc', default=None,
                      help='specify the netrc file', metavar='FILE')
    parser.add_option('-u', '--user', default=None,
                      help='specify the DIAS account name',
                      metavar='USERNAME')
    parser.add_option('--target', action='store_true', default=False,
                      help='print available targets')
    parser.add_option('--variable', action='store_true', default=False,
                      help='print available variables for specified target')

    (options, args) = parser.parse_args()

    if options.target:
        for a in sorted(inventory):
            for e in sorted(inventory[a]):
                for c in sorted(inventory[a][e]['category']):
                    print('%s/%s/%s' % (a, e, c))
        sys.exit(0)

    if len(args) < 1 or not options.variable and len(args) < 2:
        parser.error('too few arguments')

    (region, exp, cat) = args[0].split('/')
    if region not in inventory or \
       exp not in inventory[region] or \
       cat not in inventory[region][exp]['category']:
        parser.error('unknown {GCM|RCM}/experiment/category: ' + args[0])

    if options.variable:
        for v in variables[region][cat]:
            print(v)
        sys.exit(0)

    if options.ensemble is None:
        enses = inventory[region][exp]['ensemble']
    else:
        enses = []
        for e in options.ensemble:
            if 'm%03d' % int(e) \
                    in inventory[region][exp]['ensemble']:
                enses.append('m%03d' % int(e))
            else:
                parser.error('Not ensemble member: ' + e + '\n')

    t_start = inventory[region][exp]['start']
    t_end = inventory[region][exp]['end']

    if options.start is not None:
        m = re.match('(\d{4})-(\d{2})', options.start)
        if m is None or int(m.group(2)) < 1 or int(m.group(2)) > 12:
            parser.error('Illegal time format: ' + options.start)
        elif t_start <= int(m.group(1)) * 100 + int(m.group(2)):
            t_start = int(m.group(1)) * 100 + int(m.group(2))
        else:
            sys.stderr.write('Warning: start time must be after %d-%02d\n'
                             % (int(t_start / 100), t_start % 100))

    if options.end is not None:
        m = re.match('(\d{4})-(\d{2})', options.end)
        if m is None or int(m.group(2)) < 1 or int(m.group(2)) > 12:
            parser.error('Illegal time format: ' + options.end)
        elif t_end >= int(m.group(1)) * 100 + int(m.group(2)):
            t_end = int(m.group(1)) * 100 + int(m.group(2))
        else:
            sys.stderr.write('Warning: end time must be before %d-%02d\n'
                             % (int(t_end / 100), t_end % 100))

    if t_start > t_end:
        parser.error('time range conflict: %04d-%02d > %04d-%02d'
                     % (int(t_start / 100), t_start % 100, 
                        int(t_end / 100), t_end % 100))

    x_start = 0
    x_end = len(inventory[region][exp]['category'][cat]['x']) - 1
    y_start = 0
    y_end = len(inventory[region][exp]['category'][cat]['y']) - 1

    if options.x is not None:
        xr = options.x.split(',')
        if xr[0] == '':
            xs = 0
        else:
            xs = int(xr[0])
        if xr[1] == '':
            xe = len(inventory[region][exp]['category'][cat]['x']) - 1
        else:
            xe = int(xr[1])

        if xs > xe:
            parser.error('x range conflict: %d > %d' % (xs, xe))

        if xs < 0 or xs >= len(inventory[region][exp]['category'][cat]['x']):
            parser.error('out of range: start of x: %d' % xs)
        else:
            x_start = xs

        if xe < 0 or xe >= len(inventory[region][exp]['category'][cat]['x']):
            parser.error('out of range: end of x: %d' % xe)
        else:
            x_end = xe
            
    if options.y is not None:
        yr = options.y.split(',')
        if yr[0] == '':
            ys = 0
        else:
            ys = int(yr[0])
        if yr[1] == '':
            ye = len(inventory[region][exp]['category'][cat]['y']) - 1
        else:
            ye = int(yr[1])

        if ys > ye:
            parser.error('y range conflict: %d > %d' % (ys, ye))

        if ys < 0 or ys >= len(inventory[region][exp]['category'][cat]['y']):
            parser.error('out of range: start of y: %d' % ys)
        else:
            y_start = ys

        if ye < 0 or ye >= len(inventory[region][exp]['category'][cat]['y']):
            parser.error('out of range: end of y: %d' % ye)
        else:
            y_end = ye

    if options.x is None and options.west is not None:
        if inventory[region][exp]['category'][cat]['x'][0] is not None:
            l = len(inventory[region][exp]['category'][cat]['x'])
            if options.west == \
                    inventory[region][exp]['category'][cat]['x'][l - 1]:
                x_start = l - 1
            else:
                for xs in range(l):
                    if options.west \
                            < inventory[region][exp]['category'][cat]['x'][xs]:
                        x_start = xs - 1
                        if x_start < 0:
                            x_start = 0
                        break
                else:
                    parser.error('out of range: west: %f' % options.west)

    if options.x is None and options.east is not None:
        if inventory[region][exp]['category'][cat]['x'][0] is not None:
            if options.east == inventory[region][exp]['category'][cat]['x'][0]:
                x_end = 0
            else:
                l = len(inventory[region][exp]['category'][cat]['x'])
                for xe in range(l - 1, -1, -1):
                    if options.east \
                            > inventory[region][exp]['category'][cat]['x'][xe]:
                        x_end = xe + 1
                        if x_end > l - 1:
                            x_end = l - 1
                        break
                else:
                    parser.error('out of range: east: %f' % options.east)

    if options.y is None and options.south is not None:
        if inventory[region][exp]['category'][cat]['y'][0] is not None:
            l = len(inventory[region][exp]['category'][cat]['y'])
            if options.south == \
                    inventory[region][exp]['category'][cat]['y'][l - 1]:
                y_start = l - 1
            else:
                for ys in range(l):
                    if options.south \
                            < inventory[region][exp]['category'][cat]['y'][ys]:
                        y_start = ys - 1
                        if y_start < 0:
                            y_start = 0
                        break
                else:
                    parser.error('out of range: south: %f' % options.south)

    if options.y is None and options.north is not None:
        if inventory[region][exp]['category'][cat]['y'][0] is not None:
            if options.north == inventory[region][exp]['category'][cat]['y'][0]:
                y_end = 0
            else:
                l = len(inventory[region][exp]['category'][cat]['y'])
                for ye in range(l - 1, -1, -1):
                    if options.north \
                            > inventory[region][exp]['category'][cat]['y'][ye]:
                        y_end = ye + 1
                        if y_end > l - 1:
                            y_end = l - 1
                        break
                else:
                    parser.error('out of range: north: %f' % options.north)

    if region == 'GCM':
        west = inventory[region][exp]['category'][cat]['x'][x_start]
        if west is None:
            west = 0.0
        east = inventory[region][exp]['category'][cat]['x'][x_end]
        if east is None:
            east = 360.0
        north = inventory[region][exp]['category'][cat]['y'][y_end]
        south = inventory[region][exp]['category'][cat]['y'][y_start]

    if x_start > x_end or y_start > y_end:
        sys.exit('no data extracted')

    for v in args[1:]:
        if v not in variables[region][cat]:
            parser.error('unknown variable: ' + v)

    vs = ','.join(args[1:])

    host = 'd4pdf.diasjp.net'
    url = 'http://' + host + '/extract.cgi'

    (login, password) = (None, None)

    try:
        auth = netrc.netrc(options.netrc).authenticators(host)
        if auth is not None:
            (login, account, password) = auth
    except (IOError):
        pass

    if options.user is not None:
        login = options.user
        password = 'Wateryowl1997!'

    if login is None:
        login = input('Username: ')

    if password is None:
        password = getpass.getpass('Password: ')

    access = DIASAccess(login, password)
    if region == 'GCM':
        data = urllib.parse.urlencode({'region': region,
                                 'experiment': exp,
                                 'category': cat,
                                 'ensemble': ','.join(enses),
                                 'from': str(t_start),
                                 'to': str(t_end),
                                 'west': str(west),
                                 'east': str(east),
                                 'north': str(north),
                                 'south': str(south),
                                 'variables': vs})
    else:
        data = urllib.parse.urlencode({'region': region,
                                 'experiment': exp,
                                 'category': cat,
                                 'ensemble': ','.join(enses),
                                 'from': str(t_start),
                                 'to': str(t_end),
                                 'x': ','.join([str(x_start), str(x_end)]),
                                 'y': ','.join([str(y_start), str(y_end)]),
                                 'variables': vs})

    response = access.open(url, data.encode('utf-8'))

    if options.output is not None:
        f = open(options.output, 'wb')
    else:
        f = sys.stdout

    while True:
        buf = response.read(32768)
        if not buf:
            break

        f.write(buf)

    if options.output is not None:
        f.close()

    response.close()
