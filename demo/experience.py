#!/usr/bin/env python
from __future__ import print_function

# a hack so you can run it 'python demo/experience.py'
import sys
sys.path.append('.')
sys.path.append('..')
from stackexchange import Site, StackOverflow

user_id = 41981 if len(sys.argv) < 2 else int(sys.argv[1])
print('StackOverflow user %d\'s experience:' % user_id)

so = Site(StackOverflow)
user = so.user(user_id)

print('Most experienced on %s.' % user.top_answer_tags.fetch()[0].tag_name)
print('Most curious about %s.' % user.top_question_tags.fetch()[0].tag_name)

total_questions = len(user.questions.fetch())
unaccepted_questions = len(user.unaccepted_questions.fetch())
accepted = total_questions - unaccepted_questions
rate = accepted / float(total_questions) * 100
print('Accept rate is %.2f%%.' % rate)
