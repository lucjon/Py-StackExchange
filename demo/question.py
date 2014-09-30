#!/usr/bin/env python
from __future__ import print_function

# Same directory hack
import sys
sys.path.append('.')
sys.path.append('..')

try:
    get_input = raw_input
except NameError:
    get_input = input

user_api_key = get_input("Please enter an API key if you have one (Return for none):")
if not user_api_key: user_api_key = None

import stackexchange
site = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key)
site.be_inclusive()

id = int(get_input("Enter a question ID: "))
question = site.question(id)

print('--- %s ---' % question.title)
print(question.body)
print()
print('%d answers.' % len(question.answers))
