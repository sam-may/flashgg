#!/bin/bash

#
# args
#

GID=$1
TAG=$2
OUTFILE=$3
INFILES=$4

echo "[wrapper] GID         = " ${GID}
echo "[wrapper] TAG         = " ${TAG}
echo "[wrapper] INFILES     = " ${INFILES}
echo "[wrapper] OUTFILE     = " ${OUTFILE}

echo "[wrapper] hostname  = " `hostname`
echo "[wrapper] date      = " `date`
echo "[wrapper] linux timestamp = " `date +%s`

#
# untar input sandbox
#

echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`]"
echo "[wrapper] extracting input sandbox"
tar -zxf input_${TAG}.tar.gz
cp setInputFiles.py CMSSW_8_0_28/src/flashgg

export SCRAM_ARCH=slc6_amd64_gcc530
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd CMSSW_8_0_28/src/flashgg
echo "[wrapper] in directory: " ${PWD}
echo "[wrapper] attempting to build"
eval `scramv1 runtime -sh`
scramv1 b ProjectRename
scram b
eval `scramv1 runtime -sh`

echo "PATH: " $PATH
echo "LD_LIBRARY_PATH: " $LD_LIBRARY_PATH

# sed -i -- "s#PUTFILENAMEHERE#${FILE}#g" Skimming/test/skim_cfg.py
python setInputFiles.py ${INFILES}
echo "*************** cmsRun config file ******************"
cat temp_cfg.py
echo "*****************************************************"

echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] running: cmsRun -n4 temp_cfg.py"
cmsRun -n4 temp_cfg.py
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "CMSSWERROR!! cmsRun crashed with an error. Deleting output file."
    rm test_skim.root
fi

if [ -f test_skim.root ]; then
    SIZE=`stat --printf="%s\n" test_skim.root`
    if [ "$SIZE" -lt 10000 ]; then
        echo "[wrapper] invalid dumper output. quitting."
        exit 1
    fi
else
    echo "[wrapper] no dumper output produced. quitting."
    exit 1
fi

echo "[wrapper] output is"
ls -ltr

#
# clean up
#

COPYDIR=`dirname ${OUTFILE}`
if [ ! -d "${COPYDIR}" ]; then
    echo "creating output directory " ${COPYDIR}
    mkdir ${COPYDIR}
fi

echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`]"

echo "[wrapper] copying file"
gfal-copy -p -f -t 4200 --verbose file://`pwd`/test_skim.root gsiftp://gftp.t2.ucsd.edu${OUTFILE}

echo "[wrapper] cleaning up"
for FILE in `find . -not -name "*stderr" -not -name "*stdout"`; do rm -rf $FILE; done
echo "[wrapper] cleaned up"
ls
echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`]"
