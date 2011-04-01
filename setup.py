# Setuptools is required for the use_2to3 option below. You should install it
# from the Distribute home page, http://packages.python.org/distribute/
import sys
from setuptools import setup

options = {}
if sys.version_info > (3, 0):
    # Automatically run 2to3 when installing under Python 3
    options['use_2to3'] = True


setup(
	name = 'py-stackexchange',
	py_modules = ['stackexchange.core', 'stackexchange.sites', 'stackexchange.web', 'stackauth'],
	version = '1.1-2',
	description = 'A Python binding to the StackExchange (Stack Overflow, Server Fault, etc.) website APIs.',
	author = 'Lucas Jones',
	author_email = 'lucas@lucasjones.co.uk',
	url = 'http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python',
	download_url = 'https://github.com/lucjon/Py-StackExchange/tarball/master',
	keywords = ['stackexchange', 'se', 'stackoverflow'],
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Development Status :: 4 - Beta',
		'Environment :: Other Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet',
	],
	long_description = '''Update: a bug-fix release.

Please see http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python for a full description.''',
        **options
)
