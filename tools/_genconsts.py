from __future__ import print_function

import stackauth, string

sites = stackauth.StackAuth().sites()
source = ['''import stackexchange
class __SEAPI(str):
    def __call__(self):
        return stackexchange.Site(self)''']

for site in sites:
    name = ''.join(c for c in site.name if c.isalnum())
    source.append('%s = __SEAPI(\'%s\')' % (name, site.api_endpoint[7:]))

print('\n'.join(source))
