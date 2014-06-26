#!/bin/bash
echo "Please don't run this as a user. This generates a new release for PyPI. Press ^C to exit or Enter to continue."
read

if ! tools/test && [ "$IGNORE_TEST" != "yes" ]; then
	echo "The test suite failed. Fix it!"
	exit 1
fi


# Clear old distutils stuff
rm -rf build dist MANIFEST &> /dev/null
# Re-generate site constants
python _genconsts.py > stackexchange/sites.py
# Build installers, etc. and upload to PyPI
python setup.py register sdist bdist_wininst upload
