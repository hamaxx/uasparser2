import json
import time
import random
from uasparser2 import UASparser

in_uas = json.load(open('uas.json', 'r'))

t0 = time.time()
up = UASparser()
print 'load:', time.time() - t0

test_uas = []

random.seed(123)
test_list = in_uas.items()
random.shuffle(test_list)

for s in xrange(1, 2000):
	limit = max(int(float(len(test_list)) / (s ** 0.9)), 1)
	for i in xrange(0, limit):
		ua = test_list[i]
		test_uas.append(ua)

random.seed(321)
random.shuffle(test_uas)

t0 = time.time()
for uas, obj in test_uas:
	try:
		new_obj = up.parse(uas)

		assert new_obj == obj
	except:
		print
		for k, v in obj.iteritems(): print k, '\t', v, '\t', new_obj[k]
		raise

print
print 'parse:', time.time() - t0
