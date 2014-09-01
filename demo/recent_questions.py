#!/usr/bin/env python

# Same directory hack
import sys
sys.path.append('.')
sys.path.append('..')

import stackexchange, thread
so = stackexchange.Site(stackexchange.StackOverflow)
so.be_inclusive()

sys.stdout.write('Loading...')
sys.stdout.flush()

questions = so.recent_questions(pagesize=10, filter='_b')
print '\r #  vote ans view'

cur = 1
for question in questions:
	print '%2d %3d  %3d  %3d \t%s' % (cur, question.score, len(question.answers), question.view_count, question.title)
	cur += 1

num = int(raw_input('Question no.: '))
qu  = questions[num - 1]
print '--- %s' % qu.title
print '%d votes, %d answers, %d views.' % (qu.score, len(qu.answers), qu.view_count)
print 'Tagged: ' + ', '.join(qu.tags)
print
print qu.body[:250] + ('...' if len(qu.body) > 250 else '')
