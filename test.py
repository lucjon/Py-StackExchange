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

## 2.) Get question #4 150
print 'Downloading question #4...'
question = site.question(4)
print repr(question)

## 3.) Find recent questions
print 'Finding recent questions...'
recent = site.recent_questions()
print repr(recent)

## 4.) Find all site badges
print 'Finding site badges...'
badges = site.all_badges()
print repr(badges)

## f.) Print rate info
print '-> Finished. (requests, total) = %s' % repr(site.rate_limit)
