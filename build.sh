# Clear old distutils stuff
rm -rf build dist MANIFEST &> /dev/null
# Re-generate site constants
python _genconsts.py > stacksites.py
# Build installers, etc. and upload to PyPI
python setup.py register sdist bdist_wininst upload
