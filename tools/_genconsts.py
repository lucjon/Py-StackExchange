import stackauth

sites = stackauth.StackAuth().sites()
source = ['''import stackexchange
class __SEAPI(str):
	def __call__(self):
		return stackexchange.Site(self)''']

for site in sites:
	name = site.name
	name = name.replace(' ', '')
	name = name.replace('-', '')
	source.append('%s = __SEAPI(\'%s\')' % (name, site.api_endpoint[7:]))

print(('\n'.join(source)))
