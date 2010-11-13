from distutils.core import setup

setup(
	name = 'py-stackexchange',
	py_modules = ['stackexchange', 'stackcore', 'stackauth', 'stackweb'],
	version = '1.0',
	description = 'A Python binding to the StackExchange (Stack Overflow, Server Fault, etc.) website APIs.',
	author = 'Lucas Jones',
	author_email = 'lucas@lucasjones.co.uk',
	url = 'http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python',
	download_url = 'https://github.com/lucjon/Py-StackExchange/tarball/master',
	keywords = ['stackexchange', 'se', 'stackoverflow'],
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Development Status :: 4 - Beta',
		'Environment :: Other Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet',
	],
	long_description = 'Please see http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python for a full description.'
)
