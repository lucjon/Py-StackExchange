#!/bin/bash

function usage {
	echo -n "$1="
	if [ "$(eval echo '$'$1)" == "yes" ]; then
		echo -ne "\e[1myes\e[0m|no"
	else
		echo -ne "yes|\e[1mno\e[0m"
	fi
}

echo "Please don't run this as a user. This generates a new release for PyPI. Press ^C to exit or Enter to continue."
echo "Options set by environment variables: `usage IGNORE_TEST` ; `usage BUILD_WINDOWS` ; `usage DRY_RUN`."
read

# Re-generate site constants
#constsfile=$(mktemp)
#if PYTHONPATH=. python tools/_genconsts.py > "$constsfile"; then
#	cp "$constsfile" stackexchange/sites.py
#fi
#rm "$constsfile"

if ! ( [ "$IGNORE_TEST" == "yes" ] || tools/test ); then
	echo "The test suite failed. Fix it!"
	exit 1
fi

if [ "$BUILD_WINDOWS" == "yes" ]; then
	wintarget=bdist_wininst
fi

uploadtarget=upload
if [ "$DRY_RUN" == "yes" ]; then
	unset uploadtarget
fi


# Clear old distutils stuff
rm -rf build dist MANIFEST &> /dev/null

# Build installers, etc. and upload to PyPI
python setup.py register sdist $wintarget $uploadtarget
