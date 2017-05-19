#!/bin/sh
#
# Echo some config variables.
#

# If the command name occurs in the failsteps config variable,
# print an error message to stdout and return failure.

{
set -o nounset
set -o errexit

inconfig=$1
outconfig=$2

cmdname=`basename $0`
failsteps=`srs-config -default none -c $inconfig failsteps`
outfile=`srs-config -c $inconfig outfile`

v1=`srs-config -c $inconfig v1`
v2=`srs-config -c $inconfig v2`
v3=`srs-config -c $inconfig v3`

echo $cmdname v1=$v1 v2=$v2 v3=$v3 >> $outfile

if echo ",$failsteps," | grep -q ",$cmdname," ; then
  echo $cmdname failed >> $outfile 2>&1 
  exit 1
fi

echo v1 ${v1}+ > $outconfig

echo INCLUDE $inconfig >> $outconfig

exit
}
