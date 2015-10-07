#!/usr/bin/env python
from __future__ import print_function

# a hack so you can run it 'python demo/narcissism.py'
import sys
sys.path.append('.')
sys.path.append('..')
from stackauth import StackAuth
from stackexchange import Site, StackOverflow

user_id = 41981 if len(sys.argv) < 2 else int(sys.argv[1])
print('StackOverflow user %d\'s accounts:' % user_id)

stack_auth = StackAuth()
so = Site(StackOverflow, impose_throttling=True)
accounts = stack_auth.api_associated(so, user_id)
reputation = {}

for account in accounts:
    print('  %s / %d reputation' % (account.on_site.name, account.reputation))

    # This may seem a slightly backwards way of storing it, but it's easier for finding the max
    reputation[account.reputation] = account.on_site.name

print('Most reputation on: %s' % reputation[max(reputation)])
