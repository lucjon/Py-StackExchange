#!/usr/bin/env python
from __future__ import print_function

# a hack so you can run it 'python demo/stats.py'
import sys
sys.path.append('.')
sys.path.append('..')

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow, impose_throttling=True)
stats = so.stats()

print('Total questions:\t%d' % stats.total_questions)
print('\tAnswered:\t%d' % (stats.total_questions - stats.total_unanswered))
print('\tUnanswered:\t%d' % (stats.total_unanswered))

percent = (stats.total_unanswered / float(stats.total_questions)) * 100
print('%.2f%% unanswered. (%.2f%% answered!)' % (percent, 100 - percent))
