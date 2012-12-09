"""
userparse2
	By Jure Ham (jure.ham@zemanta.com)

Based on:
	A python version of http://user-agent-string.info/download/UASparser

	By Hicro Kee (http://hicrokee.com)
	email: hicrokee AT gmail DOT com

	Modified by Michal Molhanec http://molhanec.net

Usage:
	from uasparser import UASparser

	uas_parser = UASparser('/path/to/your/cache/folder')

	result = uas_parser.parse('YOUR_USERAGENT_STRING',entire_url='ua_icon,os_icon') #only 'ua_icon' or 'os_icon' or both are allowed in entire_url
"""

from collections import OrderedDict
import urllib2
import os
import re
try:
	import cPickle as pickle
except:
	import pickle

class UASException(Exception):
	pass

class UASparser:

	ini_url  = 'http://user-agent-string.info/rpc/get_data.php?key=free&format=ini'
	info_url = 'http://user-agent-string.info'

	cache_file_name = 'uasparser2_cache'
	cache_dir = ''
	data = None

	empty_result = {
		'typ':'unknown',
		'ua_family':'unknown',
		'ua_name':'unknown',
		'ua_url':'unknown',
		'ua_company':'unknown',
		'ua_company_url':'unknown',
		'ua_icon':'unknown.png',
		'ua_info_url':'unknown',
		'os_family':'unknown',
		'os_name':'unknown',
		'os_url':'unknown',
		'os_company':'unknown',
		'os_company_url':'unknown',
		'os_icon':'unknown.png',
	}

	def __init__(self, cache_dir=None):
		"""
		Create an UASparser to parse useragent strings.
		cache_dir should be appointed or set to the path of program by default
		"""
		self.cache_dir = cache_dir or os.path.abspath( os.path.dirname(__file__) )
		if not os.access(self.cache_dir, os.W_OK):
			raise UASException("Cache directory %s is not writable.")
		self.cache_file_name = os.path.join( self.cache_dir, self.cache_file_name)

		self.loadData()

	def parse(self, useragent):
		"""
		Get the information of an useragent string
		Args:
			useragent: String, an useragent string
			entire_url: String, write the key labels which you want to get an entire url split by comma, expected 'ua_icon' or 'os_icon'.
		"""

		def match_robots(data, result):
			for test in data['robots'].values():
				if test['ua'] == useragent:
					result += test['details'].items()
					return True
			return False

		def match_browser(data, result):
			for test in data['browser']:
				test_rg = test['re'].findall(useragent)
				if test_rg:
					test['details']['ua_name'] = '%s %s' % (test['details']['ua_family'], test_rg[0])
					result += test['details'].items()
					return True
			return False

		def match_os(data, result):
			for test in data['os']:
				if test['re'].findall(useragent):
					result += test['details'].items()
					return True
			return False

		if not useragent:
			raise UASException("Excepted argument useragent is not given.")

		data = self.data
		result = self.empty_result.items()

		if not match_robots(data, result):
			match_os(data, result)
			match_browser(data, result)

		return dict(result)

	def _parseIniFile(self, file):
		"""
		Parse an ini file into a dictionary structure
		"""

		def toPythonReg(reg):
			reg_l = reg[1:reg.rfind('/')] # modify the re into python format
			reg_r = reg[reg.rfind('/')+1:]
			flag = 0
			if 's' in reg_r: flag = flag | re.S
			if 'i' in reg_r: flag = flag | re.I

			return re.compile(reg_l,flag)

		def get_matching_object(reg_list, details_list, details_template, browser_types=None, browser_os=None, os_dict=None):
			m_data = []
			m_details = {}

			for k, r_obj in reg_list.iteritems():
				reg = toPythonReg(r_obj[0])
				m_id = int(r_obj[1])

				obj = {'re': reg, 'details': {}}

				if browser_os and os_dict and m_id in browser_os:
					key = int(browser_os[m_id][0])
					if key in os_dict:
						obj['details'] = dict(os_dict[key]['details'])

				for i, det in enumerate(details_list[m_id]):
					if details_template[i][0] == 'ua_info_url':
						det = self.info_url + det

					if browser_types and details_template[i][0] == 'typ':
						det = browser_types[int(det)][0]

					obj['details'][details_template[i][0]] = det

				m_data.append(obj)
				m_details[m_id] = obj

			return m_data, m_details

		def get_robots_object(robots_list, os_list, browser_template, os_template):
			r_data = OrderedDict()
			for r_id, robot in robots_list.iteritems():
				obj = {}

				re = robot[0]
				details_browser = robot[1:7] + robot[8:]
				details_os = os_list[robot[7]] if robot[7] else []

				obj['ua'] = re
				obj['details'] = {'typ': 'Robot'}

				for i, tem in enumerate(browser_template):
					det = details_browser[i] if len(details_browser) > i else tem[1]
					if tem[0] == 'ua_info_url':
						det = self.info_url + det
					obj['details'][tem[0]] = det

				for i, tem in enumerate(os_template):
					det = details_os[i] if len(details_os) > i else tem[1]
					obj['details'][os_template[i][0]] = det

				r_data[r_id] = obj

			return r_data

		data = {}
		current_section = ''
		section_pat = re.compile(r'^\[(\S+)\]$')
		option_pat = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

		ret_os = (('os_family','unknown'), ('os_name','unknown'), ('os_url','unknown'), ('os_company','unknown'),
				('os_company_url','unknown'), ('os_icon','unknown.png'))

		ret_browser = (('typ', 'unknown'), ('ua_family','unknown'), ('ua_url','unknown'),
				('ua_company','unknown'), ('ua_company_url','unknown'), ('ua_icon','unknown.png'), ('ua_info_url', 'unknown'))

		ret_robot = (('ua_family','unknown'), ('ua_name', 'unknown'), ('ua_url','unknown'),
				('ua_company','unknown'), ('ua_company_url','unknown'), ('ua_icon','unknown.png'), ('ua_info_url', 'unknown'))

		#step by line
		order = []
		for line in file.split("\n"):
			option = option_pat.findall(line)
			if option:
				key = int(option[0][0])
				val = option[0][1]

				if data[current_section].has_key(key):
					data[current_section][key].append(val)
				else:
					data[current_section][key] = [val,]
					order.append(key)
			else:
				section = section_pat.findall(line)
				if section:
					current_section = section[0]
					data[current_section] = OrderedDict()
					order = []

		robots = get_robots_object(data['robots'], data['os'], ret_robot, ret_os)
		os, os_dict = get_matching_object(data['os_reg'], data['os'], ret_os)
		browser, browser_dict = get_matching_object(data['browser_reg'], data['browser'], ret_browser, data['browser_type'], data['browser_os'], os_dict)

		return {
			'robots': robots,
			'os': os,
			'browser': browser,
		}

	def _fetchURL(self, url):
		"""
		Get remote context by a given url
		"""
		resq = urllib2.Request(url)
		context = urllib2.urlopen(resq)
		return context.read()

	def _checkCache(self):
		"""
		check whether the cache available or not?
		"""
		cache_file = self.cache_file_name
		if not os.path.exists(cache_file):
			return False

		return True

	def updateData(self):
		"""
		Check whether data is out-of-date
		"""

		try:
			cache_file = open(self.cache_file_name,'wb')
			ini_file = self._fetchURL(self.ini_url)
			ini_data = self._parseIniFile(ini_file)
		except:
			raise
			raise UASException("Failed to download cache data")

		self.data = ini_data
		pickle.dump(ini_data, cache_file)

		return True

	def loadData(self):
		"""
		start to load cache data
		"""
		if self._checkCache():
			self.data = pickle.load(open(self.cache_file_name,'rb'))
		else:
			self.updateData()
