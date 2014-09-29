#!/usr/bin/env python
from __future__ import print_function

import sys
sys.path.append('.')
sys.path.append('..')
import stackexchange, stackauth

if len(sys.argv) < 3:
    print('Usage: versus.py YOUR_SO_UID THEIR_SO_UID')
    sys.exit(1)

so = stackexchange.Site(stackexchange.StackOverflow, impose_throttling=True)

user1, user2 = (int(x) for x in sys.argv[1:])
rep1, rep2 = {}, {}
username1, username2 = (so.user(x).display_name for x in (user1, user2))
total_rep1, total_rep2 = 0, 0

sites = []

for site in stackauth.StackAuth().api_associated(so, user1):
    rep1[site.on_site.name] = site.reputation
    sites.append(site.on_site.name)
for site in stackauth.StackAuth().api_associated(so, user2):
    rep2[site.on_site.name] = site.reputation

for site in sites:
    total_rep1 += rep1[site]
    if site in rep2:
        total_rep2 += rep2[site]

    max_user = username1
    max_rep, other_rep = rep1[site], rep2.get(site, 0)
    if rep2.get(site, 0) > rep1[site]:
        max_user = username2
        max_rep, other_rep = other_rep, max_rep
    
    diff = max_rep - other_rep

    print('%s: %s wins (+%d)' % (site, max_user, diff))

print('Overall: %s wins (+%d)' % (username1 if total_rep1 >= total_rep2 else username2, max(total_rep1, total_rep2) - min(total_rep1, total_rep2)))


