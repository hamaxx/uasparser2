import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

from uasparser2 import UASparser

up = UASparser()


uas_list = []

ua_file = open('test/user_agents.txt', 'r').read().split('\n')

c = 0
for uas in ua_file:
	if uas:
		c += 1
		if c % 1000 == 0:
			print c, '/', len(ua_file)

		uas_list.append((uas, up.parse(uas)))

json.dump(uas_list, open('test/uas.json', 'w'))
