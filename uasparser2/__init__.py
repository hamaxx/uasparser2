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

import os
import platform
import re
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from .imcache import SimpleCache
from .decorators import deprecated


VERSION = '0.3'
CACHE_FILE_NAME = 'uasparser2_{lib_version}_{python_version}_cache.pickle'

DEFAULT_TMP_DIR = '/tmp'

INI_URL = 'http://user-agent-string.info/rpc/get_data.php?key=free&format=ini'
INFO_URL = 'http://user-agent-string.info'

EMPTY_RESULT = {
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


class UASException(Exception):
    pass


class UASParser(object):

    def __init__(self, cache_dir=None, mem_cache_size=1000, cache_ttl=None):
        """
        Create an UASparser to parse useragent strings.
        cache_dir should be appointed or set to the path of program by default
        Args:
            cache_dir: String, path to the cache dir for useragent parsing data, default is /tmp.
            cache_ttl: Int, ttl for useragent parsing data cache in seconds, default is never.
                       Cache ttl is only checked on init when data is loaded.
            mem_cache_size: Int, number of parsed useragents to cache, default is 1000.
        """

        self._cache_file_name = self._get_cache_file_name(cache_dir)
        self._cache_ttl = cache_ttl

        self._mem_cache_size = mem_cache_size
        self._mem_cache = self._mem_cache_size and SimpleCache(cache_size=self._mem_cache_size)

        self._ini_data_loader = _IniDataLoader()
        self._uas_matcher = None

        self.load_data()

    def _get_cache_file_name(self, cache_dir):
        cache_dir = cache_dir or DEFAULT_TMP_DIR

        if not os.access(cache_dir, os.W_OK):
            raise UASException("Cache directory %s is not writable." % cache_dir)

        return os.path.join(
            cache_dir,
            CACHE_FILE_NAME.format(
                lib_version=VERSION,
                python_version=platform.python_version(),
            )
        )

    def parse(self, useragent):
        """
        Get the information of an useragent string
        Args:
            useragent: String, an useragent string
        """
        if not useragent:
            raise UASException("Excepted argument useragent is not given.")

        if self._mem_cache:
            try:
                return self._mem_cache.get(useragent)
            except self._mem_cache.CacheMissException:
                pass

        result = self._uas_matcher.match(useragent)

        if self._mem_cache:
            self._mem_cache.put(useragent, result)

        return result

    def _fetch_url(self, url):
        context = urlopen(url)
        return context

    def _check_cache(self):
        cache_file = self._cache_file_name
        if not os.path.exists(cache_file):
            return False

        return True

    def _load_cache(self):
        try:
            cache_data = pickle.load(open(self._cache_file_name, 'rb'))
        except Exception:
            self.update_data()
            return

        if self._cache_ttl is not None and cache_data['timestamp'] < time.time() - self._cache_ttl:
            self.update_data()
            return

        self._uas_matcher = _UASMatcher(cache_data['data'])

    def update_data(self):
        try:
            cache_file = open(self._cache_file_name, 'wb')
            ini_file = self._fetch_url(INI_URL)
            ini_data = self._ini_data_loader.parse_ini_file(ini_file)
        except:
            raise UASException("Failed to download cache data")

        self._uas_matcher = _UASMatcher(ini_data)

        cache_data = {
            'data': ini_data,
            'timestamp': time.time(),
        }
        pickle.dump(cache_data, cache_file)

        if self._mem_cache:
            self._mem_cache = SimpleCache(cache_size=self._mem_cache_size)

        return True

    def load_data(self):
        if self._check_cache():
            self._load_cache()
        else:
            self.update_data()


class UASparser(UASParser):

    @deprecated
    def __init__(self, *args, **kwargs):
        super(UASparser, self).__init__(*args, **kwargs)

    @deprecated
    def updateData(self):
        return self.update_data()

    @deprecated
    def loadData(self):
        return self.load_data()


class _UASMatcher(object):

    def __init__(self, data):
        self._data = data

    def _match_robots(self, useragent, result):
        try:
            res = self._data['robots'][useragent]
            result.update(res['details'])
            return True
        except KeyError:
            return False

    def _match_browser(self, useragent, result):
        for test in self._data['browser']['reg']:
            test_rg = test['re'].search(useragent)
            if test_rg and test_rg.lastindex and test_rg.lastindex > 0:
                browser_version = test_rg.group(1)

                result.update(self._data['browser']['details'][test['details_key']])
                result['ua_name'] = '%s %s' % (result['ua_family'], browser_version)

                os_key = test['os_details_key']
                if os_key:
                    result.update(self._data['os']['details'][os_key])

                    return True
                return False

        return False

    def _match_os(self, useragent, result):
        for test in self._data['os']['reg']:
            if test['re'].findall(useragent):
                result.update(self._data['os']['details'][test['details_key']])

                return True
        return False

    def _match_device(self, useragent, result):
        for test in self._data['device']['reg']:
            if test['re'].findall(useragent):
                result.update(self._data['device']['details'][test['details_key']])
                return True

        # Try to match using the type
        if result['typ'] in ("Other", "Library", "Validator", "Useragent Anonymizer"):
            result.update(self._data['device']['details'][1])
        elif result['typ'] in ("Mobile Browser", "Wap Browser"):
            result.update(self._data['device']['details'][3])
        else:
            result.update(self._data['device']['details'][2])

        return False

    def match(self, useragent):
        result = dict(EMPTY_RESULT)

        self._match_robots(useragent, result) or \
            self._match_browser(useragent, result) or \
            self._match_os(useragent, result)

        self._match_device(useragent, result)

        return result


class _IniDataLoader(object):

    def _to_python_reg(self, reg):
        reg_l = reg[1:reg.rfind('/')]
        reg_r = reg[reg.rfind('/') + 1:]
        flag = 0
        if 's' in reg_r:
            flag = flag | re.S
        if 'i' in reg_r:
            flag = flag | re.I

        return re.compile(reg_l, flag)

    def _read_ini_file(self, file_buffer):
        data = {}

        current_section = ''
        section_pat = re.compile(r'^\[(\S+)\]$')
        option_pat = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

        for line in file_buffer:
            line = line.decode('utf-8', 'ignore')
            option = option_pat.findall(line)
            if option:
                key = int(option[0][0])
                val = option[0][1]

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

    def _get_matching_object(self, reg_list, details, details_template, browser_types=None, browser_os=None):
        m_data = []
        m_details = {}

        for k, r_obj in reg_list.items():
            reg = self._to_python_reg(r_obj[0])
            m_id = int(r_obj[1])

            obj = {'re': reg, 'details_key': m_id, 'os_details_key': None}

            # OS details from browser
            if browser_os and m_id in browser_os:
                key = int(browser_os[m_id][0])
                obj['os_details_key'] = key

            m_data.append(obj)

        for m_id, details in details.items():
            obj = {}

            for i, det in enumerate(details):
                if details_template[i] == 'ua_info_url':
                    det = INFO_URL + det

                if browser_types and details_template[i] == 'typ':
                    det = browser_types[int(det)][0]

                obj[details_template[i]] = det

            m_details[m_id] = obj

        return {
            'reg': m_data,
            'details': m_details,
        }

    def _get_robots_object(self, robots, os_details, browser_template, os_template):
        r_data = {}
        for r_id, robot in robots.items():
            obj = {}

            re = robot[0]
            details_browser = robot[1:7] + robot[8:]
            details_os = os_details[robot[7]] if robot[7] else []

            obj['ua'] = re
            obj['details'] = {'typ': 'Robot'}

            for i, name in enumerate(browser_template):
                det = details_browser[i] if len(details_browser) > i else EMPTY_RESULT[name]

                if name == 'ua_info_url':
                    det = INFO_URL + det

                obj['details'][name] = det

            for i, name in enumerate(os_template):
                det = details_os[i] if len(details_os) > i else EMPTY_RESULT[name]
                obj['details'][name] = det

            r_data[re] = obj

        return r_data

    def parse_ini_file(self, file_buffer):
        os_template = ['os_family', 'os_name', 'os_url', 'os_company', 'os_company_url', 'os_icon']
        browser_template = ['typ', 'ua_family', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        robot_template = ['ua_family', 'ua_name', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        device_template = ['device_type', 'device_icon', 'device_info_url']

        data = self._read_ini_file(file_buffer)

        robots = self._get_robots_object(data['robots'], data['os'], robot_template, os_template)
        os = self._get_matching_object(data['os_reg'], data['os'], os_template)
        browser = self._get_matching_object(
            data['browser_reg'], data['browser'], browser_template, data['browser_type'], data['browser_os']
        )
        device = self._get_matching_object(data['device_reg'], data['device'], device_template)

        return {
            'robots': robots,
            'os': os,
            'browser': browser,
            'device': device,
        }
