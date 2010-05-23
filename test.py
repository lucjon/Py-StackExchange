#!/usr/bin/env python
import sys
import stackexchange as sx_api

site = sys.argv[1] if len(sys.argv) > 1 else 'StackOverflow'
print 'Assuming site is %s' % site
site = sx_api.Site(getattr(sx_api, site))
site.include_body = True

## 1.) Try and get user #150
print 'Downloading user information for user #150...'
user = site.user(150)
print repr(user)
