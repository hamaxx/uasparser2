import json
import time
from uasparser2 import UASparser

test_uas = json.load(open('uas.json', 'r'))

t0 = time.time()
up = UASparser()
print 'load:', time.time() - t0

t0 = time.time()
for _ in xrange(10):
	print '.',
	for uas, obj in test_uas.iteritems():
		try:
			new_obj = up.parse(uas)

			assert new_obj == obj
		except:
			print
			for k, v in obj.iteritems(): print k, '\t', v, '\t', new_obj[k]
			raise

print
print 'parse:', time.time() - t0
