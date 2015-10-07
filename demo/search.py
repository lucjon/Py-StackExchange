#!/usr/bin/env python
from __future__ import print_function

# a hack so you can run it 'python demo/search.py'
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
so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        term = get_input('Please provide a search term:')
    else:
        term = ' '.join(sys.argv[1:])
    print('Searching for %s...' % term,)
    sys.stdout.flush()

    qs = so.search(intitle=term)

    print('\r--- questions with "%s" in title ---' % (term))
    
    for q in qs:
        print('%8d %s' % (q.id, q.title))

