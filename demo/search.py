#!/usr/bin/env python

# a hack so you can run it 'python demo/stats.py'
import sys
sys.path.append('.')
sys.path.append('..')

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow)

if len(sys.argv) < 2:
	print 'Usage: search.py TERM'
else:
	term = ' '.join(sys.argv[1:])
	print 'Searching for %s...' % term,
	sys.stdout.flush()

	qs = so.search(intitle=term)

	print '\r--- questions with "%s" in title ---' % (term)
	
	for q in qs:
		print '%8d %s' % (q.id, q.title)

