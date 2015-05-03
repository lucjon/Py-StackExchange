#!/usr/bin/env python
from __future__ import print_function
from six.moves import input

# Same directory hack
import sys
sys.path.append('.')
sys.path.append('..')

user_api_key = input("Please enter an API key if you have one (Return for none):")
if not user_api_key: user_api_key = None

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
so.be_inclusive()

sys.stdout.write('Loading...')
sys.stdout.flush()

questions = so.recent_questions(pagesize=10, filter='_b')
print('\r #  vote ans view')

cur = 1
for question in questions[:10]:
    print('%2d %3d  %3d  %3d \t%s' % (cur, question.score, len(question.answers), question.view_count, question.title))
    cur += 1

num = int(input('Question no.: '))
qu  = questions[num - 1]
print('--- %s' % qu.title)
print('%d votes, %d answers, %d views.' % (qu.score, len(qu.answers), qu.view_count))
print('Tagged: ' + ', '.join(qu.tags))
print()
print(qu.body[:250] + ('...' if len(qu.body) > 250 else ''))
