#!/bin/bash
OUTPUTDIR=$1
OUTPUTFILENAME=$2
INPUTFILENAMES=$3
INDEX=$4
CMSSW_VER=$5

ARGS="${@:7}"

WD=$PWD

echo "[wrapper] OUTPUTDIR   = " ${OUTPUTDIR}
echo "[wrapper] OUTPUTFILENAME  = " ${OUTPUTFILENAME}
echo "[wrapper] INPUTFILENAMES  = " ${INPUTFILENAMES}
echo "[wrapper] INDEX       = " ${INDEX}

echo "[wrapper] printing env"
printenv
echo 

echo "[wrapper] hostname  = " `hostname`
echo "[wrapper] date      = " `date`
echo "[wrapper] linux timestamp = " `date +%s`

echo
echo
echo
rm package.tar.gz
timeout 15m xrdcp root://redirector.t2.ucsd.edu///store/user/smay/FCNC/MY_DIR/package.tar.gz .
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
tar xvf package.tar.gz
rm package.tar.gz
cp config.json $CMSSW_VER/src/flashgg/Systematics/test/MY_DIR//
cd $CMSSW_VER/src/flashgg
echo "[wrapper] in directory: " ${PWD}
scramv1 b ProjectRename
scram b -j1
eval $(scram runtime -sh)
pip install --user htcondor
cd $WD
mkdir MY_DIR/
echo "ls $X509_USER_PROXY"
ls $X509_USER_PROXY
mkdir .dasmaps
mv das_maps_dbs_prod.js .dasmaps/

echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] running: XRDCP"
XRDCP

echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] running: COMMAND filenames=${INPUTFILENAMES} ${ARGS}"
COMMAND filenames=${INPUTFILENAMES} ${ARGS}

if [ "$?" != "0" ]; then
    echo "Removing output file because cmsRun crashed with exit code $?"
    for file in $(find -name '*.root'); do
        rm $file
    done
fi

cd MY_DIR
echo
echo
echo "Job finished with exit code ${retval}"
echo "Files in ouput folder"
ls -ltr

eval `scram unsetenv -sh`
for file in $(find -name '*.root'); do
    echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] Attempting to gfal-copy file: $file to gsiftp://gftp.t2.ucsd.edu/${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root"
    gfal-copy -p -f -t 4200 --verbose file://`pwd`/$file gsiftp://gftp.t2.ucsd.edu/${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root --checksum ADLER32
done
