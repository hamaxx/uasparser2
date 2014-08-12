"""
userparse2
    By Jure Ham (jure.ham@zemanta.com)

Based on:
    A python version of http://user-agent-string.info/download/UASparser

    By Hicro Kee (http://hicrokee.com)
    email: hicrokee AT gmail DOT com

    Modified by Michal Molhanec http://molhanec.net

Usage:
    from uasparser2 import UASparser

    uas_parser = UASparser('/path/to/your/cache/folder', mem_cache_size=1000)

    result = uas_parser.parse('YOUR_USERAGENT_STRING')
"""

import urllib2
import os
import re

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


DEFAULT_TMP_DIR = '/tmp'


class UASException(Exception):
    pass


class UASCache(object):

    cache = None
    cache_size = 0

    stats_hit = 0
    stats_miss = 0

    def __init__(self, cache_size):
        if cache_size <= 0:
            return

        self.cache = OrderedDict()
        self.cache_size = cache_size

    def insert(self, key, val):
        if self.cache_size <= 0:
            return

        try:
            del self.cache[key]

            self.stats_hit += 1
        except KeyError:
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)

            self.stats_miss += 1

        self.cache[key] = val

    def get(self, key):
        if self.cache_size <= 0:
            return

        try:
            return self.cache[key]
        except KeyError:
            return None


class UASparser(object):

    ini_url = 'http://user-agent-string.info/rpc/get_data.php?key=free&format=ini'
    info_url = 'http://user-agent-string.info'

    cache_file_name = 'uasparser21_cache.pickle'
    cache_dir = ''

    data = None

    mem_cache = None

    empty_result = {
        'typ': 'unknown',
        'ua_family': 'unknown',
        'ua_name': 'unknown',
        'ua_url': 'unknown',
        'ua_company': 'unknown',
        'ua_company_url': 'unknown',
        'ua_icon': 'unknown.png',
        'ua_info_url': 'unknown',
        'device_type': 'unknown',
        'device_icon': 'unknown.png',
        'device_info_url': 'unknown',
        'os_family': 'unknown',
        'os_name': 'unknown',
        'os_url': 'unknown',
        'os_company': 'unknown',
        'os_company_url': 'unknown',
        'os_icon': 'unknown.png',
    }

    def __init__(self, cache_dir=None, mem_cache_size=0):
        """
        Create an UASparser to parse useragent strings.
        cache_dir should be appointed or set to the path of program by default
        """

        self.cache_dir = cache_dir or DEFAULT_TMP_DIR
        if not os.access(self.cache_dir, os.W_OK):
            raise UASException("Cache directory %s is not writable." % self.cache_dir)
        self.cache_file_name = os.path.join(self.cache_dir, self.cache_file_name)

        self.mem_cache = UASCache(mem_cache_size)

        self.loadData()

    def parse(self, useragent):
        """
        Get the information of an useragent string
        Args:
            useragent: String, an useragent string
        """

        def match_robots(data, result):
            try:
                res = data['robots'][useragent]
                result.update(res['details'])
                return True
            except KeyError:
                return False

        def match_browser(data, result):
            for test in data['browser']['reg']:
                test_rg = test['re'].search(useragent)
                if test_rg and test_rg.lastindex > 0:
                    browser_version = test_rg.group(1).decode('utf-8', 'ignore')

                    result.update(data['browser']['details'][test['details_key']])
                    result['ua_name'] = '%s %s' % (result['ua_family'], browser_version)

                    os_key = test['os_details_key']
                    if os_key:
                        result.update(data['os']['details'][os_key])

                        return True
                    return False

            return False

        def match_os(data, result):
            for test in data['os']['reg']:
                if test['re'].findall(useragent):
                    result.update(data['os']['details'][test['details_key']])

                    return True
            return False

        def match_device(data, result):
            for test in data['device']['reg']:
                if test['re'].findall(useragent):
                    result.update(data['device']['details'][test['details_key']])
                    return True
            return False

        if not useragent:
            raise UASException("Excepted argument useragent is not given.")

        result = self.mem_cache.get(useragent)

        if not result:
            data = self.data
            result = dict(self.empty_result)

            match_robots(data, result) or match_browser(data, result) or match_os(data, result)
            # Finally try to match the device type.
            if not match_device(data, result):
                # Try to match using the type
                if result['typ'] in ("Other", "Library", "Validator", "Useragent Anonymizer"):
                    result.update(data['device']['details'][1])
                elif result['typ'] in ("Mobile Browser", "Wap Browser"):
                    result.update(data['device']['details'][3])
                else:
                    result.update(data['device']['details'][2])

        self.mem_cache.insert(useragent, result)

        return result

    def _parseIniFile(self, file_content):
        def toPythonReg(reg):
            reg_l = reg[1:reg.rfind('/')]
            reg_r = reg[reg.rfind('/') + 1:]
            flag = 0
            if 's' in reg_r:
                flag = flag | re.S
            if 'i' in reg_r:
                flag = flag | re.I

            return re.compile(reg_l, flag)

        def read_ini_file(file_content):
            data = {}

            current_section = ''
            section_pat = re.compile(r'^\[(\S+)\]$')
            option_pat = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

            for line in file_content.split("\n"):
                option = option_pat.findall(line)
                if option:
                    key = int(option[0][0])
                    val = option[0][1].decode('utf-8', 'ignore')

                    if key in data[current_section]:
                        data[current_section][key].append(val)
                    else:
                        data[current_section][key] = [val]
                else:
                    section = section_pat.findall(line)
                    if section:
                        current_section = section[0]
                        data[current_section] = OrderedDict()

            return data

        def get_matching_object(reg_list, details, details_template, browser_types=None, browser_os=None):
            m_data = []
            m_details = {}

            for k, r_obj in reg_list.iteritems():
                reg = toPythonReg(r_obj[0])
                m_id = int(r_obj[1])

                obj = {'re': reg, 'details_key': m_id, 'os_details_key': None}

                # OS details from browser
                if browser_os and m_id in browser_os:
                    key = int(browser_os[m_id][0])
                    obj['os_details_key'] = key

                m_data.append(obj)

            for m_id, details in details.iteritems():
                obj = {}

                for i, det in enumerate(details):
                    if details_template[i] == 'ua_info_url':
                        det = self.info_url + det

                    if browser_types and details_template[i] == 'typ':
                        det = browser_types[int(det)][0]

                    obj[details_template[i]] = det

                m_details[m_id] = obj

            return {
                'reg': m_data,
                'details': m_details,
            }

        def get_robots_object(robots, os_details, browser_template, os_template):
            r_data = {}
            for r_id, robot in robots.iteritems():
                obj = {}

                re = robot[0]
                details_browser = robot[1:7] + robot[8:]
                details_os = os_details[robot[7]] if robot[7] else []

                obj['ua'] = re
                obj['details'] = {'typ': 'Robot'}

                for i, name in enumerate(browser_template):
                    det = details_browser[i] if len(details_browser) > i else self.empty_result[name]

                    if name == 'ua_info_url':
                        det = self.info_url + det

                    obj['details'][name] = det

                for i, name in enumerate(os_template):
                    det = details_os[i] if len(details_os) > i else self.empty_result[name]
                    obj['details'][name] = det

                r_data[re] = obj

            return r_data

        os_template = ['os_family', 'os_name', 'os_url', 'os_company', 'os_company_url', 'os_icon']
        browser_template = ['typ', 'ua_family', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        robot_template = ['ua_family', 'ua_name', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        device_template = ['device_type', 'device_icon', 'device_info_url']

        data = read_ini_file(file_content)

        robots = get_robots_object(data['robots'], data['os'], robot_template, os_template)
        os = get_matching_object(data['os_reg'], data['os'], os_template)
        browser = get_matching_object(
            data['browser_reg'], data['browser'], browser_template, data['browser_type'], data['browser_os']
        )
        device = get_matching_object(data['device_reg'], data['device'], device_template)

        return {
            'robots': robots,
            'os': os,
            'browser': browser,
            'device': device,
        }

    def _fetchURL(self, url):
        resq = urllib2.Request(url)
        context = urllib2.urlopen(resq)
        return context.read()

    def _checkCache(self):
        cache_file = self.cache_file_name
        if not os.path.exists(cache_file):
            return False

        return True

    def updateData(self):
        try:
            cache_file = open(self.cache_file_name, 'wb')
            ini_file = self._fetchURL(self.ini_url)
            ini_data = self._parseIniFile(ini_file)
        except:
            raise UASException("Failed to download cache data")

        self.data = ini_data
        pickle.dump(ini_data, cache_file)

        return True

    def loadData(self):
        if self._checkCache():
            try:
                self.data = pickle.load(open(self.cache_file_name, 'rb'))
            except Exception:
                self.updateData()
        else:
            self.updateData()
