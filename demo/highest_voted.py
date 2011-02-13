#!/usr/bin/env python

# a hack so you can run it 'python demo/stats.py'
import sys
sys.path.append('.')
sys.path.append('..')
from stackauth import StackAuth
from stackexchange import Site, StackOverflow, Sort, DESC

so = Site(StackOverflow)

print 'The highest voted question on StackOverflow is:'
question = so.questions(sort=Sort.Votes, order=DESC)[0]
print '\t%s\t%d' % (question.title, question.score)
print
print 'Look, see:', question.url
