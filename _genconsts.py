import stackauth

sites = stackauth.StackAuth().sites()
source = []

for site in sites:
	name = site.name
	name = name.replace(' ', '')
	name = name.replace('-', '')
	source.append('%s = \'%s\'' % (name, site.api_endpoint[7:]))

print ('\n'.join(source))
