import os
import sys
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

from uasparser2 import UASparser

test_uas = json.load(open('test/uas.json', 'r'))

t0 = time.time()
up = UASparser(mem_cache_size=0)
print 'load:', time.time() - t0

t0 = time.time()
for uas, obj in test_uas:
    try:
        new_obj = up.parse(uas)

        assert new_obj == obj
    except Exception:
        print
        print uas
        for k in set(new_obj.keys()) | set(obj.keys()):
            if obj.get(k) != new_obj.get(k):
                print k, '\t', obj.get(k, '').encode('utf-8'), '\t', new_obj.get(k, '').encode('utf-8')

print
print 'parse:', time.time() - t0

print 'cahce', up.mem_cache.stats_hit, up.mem_cache.stats_miss
