#!/usr/bin/env python

# Setuptools is required for the use_2to3 option below. You should install it
# from the Distribute home page, http://packages.python.org/distribute/
import sys
from setuptools import setup

options = {}
#if sys.version_info > (3, 0):
    # Automatically run 2to3 when installing under Python 3
    #options['use_2to3'] = True


setup(
    name = 'py-stackexchange',
    py_modules = ['stackexchange.core', 'stackexchange.sites', 'stackexchange.web', 'stackexchange.models', 'stackexchange.site', 'stackauth'],
    version = '2.2.007',
    description = 'A Python binding to the StackExchange (Stack Overflow, Server Fault, etc.) website APIs.',
    author = 'Lucas Jones',
    author_email = 'lucas@lucasjones.co.uk',
    url = 'http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python',
    download_url = 'https://github.com/lucjon/Py-StackExchange/tarball/master',
    keywords = ['stackexchange', 'se', 'stackoverflow'],
    install_requires = ['six >= 1.8.0'],
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
        long_description = '''**IMPORTANT**: Py-StackExchange now targets version 2.x of the StackExchange API, which introduces some small but breaking changes --- in particular, you will need to register for a new API key. Read the wiki page https://github.com/lucjon/Py-StackExchange/wiki/Updating-to-v2.x for more information.

Please see http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python for a full description.''',
        **options
)
