Fast and reliable User Agent parser for python
==============================================
Author: Jure Ham (jure.ham@zemanta.com)

- Tested with more the 50.000 unique user agents.
- Up to date data provided by http://user-agent-string.info/
- Built-in cache.
- Support for python 3


Forked from:
---------
A python version of http://user-agent-string.info/download/UASparser

By Hicro Kee (http://hicrokee.com) email: hicrokee AT gmail DOT com

Modified by Michal Molhanec http://molhanec.net

Install:
-------
	pip install uasparser2

Usage:
------
	from uasparser2 import UASParser

	uas_parser = UASParser(cache_dir='/path/to/your/cache/folder', cache_ttl=3600*24*7, mem_cache_size=1000)

	result = uas_parser.parse('YOUR_USERAGENT_STRING')

	# If input data is not avaible in cache folde, UASparser will download and prepare it on init.
	# Force data update by calling:

	uas_parser.update_data()


Speed comparison:
-----------------
Parsing 100,000 user agents (10,000 unique) from our server logs:

original uasparser: 7264.2 sec

uasparser2 without cache: 171.7 sec

uasparser2 with cache(size 1000): 34.6 sec


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/hamaxx/uasparser2/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

