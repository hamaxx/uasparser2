import json
from uasparser import UASparser

up = UASparser()


uas_list = []

ua_file = open('user_agents_sample.txt', 'r').read().split('\n')
ua_file += open('user_agents.txt', 'r').read().split('\n')[:10000]

c = 0
for uas in ua_file:
	if uas:
		c += 1
		if c % 1000 == 0:
			print c, '/', len(ua_file)

		uas_list.append((uas, up.parse(uas)))

json.dump(uas_list, open('uas.json', 'w'))
