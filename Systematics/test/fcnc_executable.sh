#!/bin/bash
OUTPUTDIR=$1
OUTPUTFILENAME=$2
INPUTFILENAMES=$3
INDEX=$4
CMSSW_VER=$5

ARGS="${@:7}"

function stageout {
    COPY_SRC=$1
    COPY_DEST=$2
    retries=0
    COPY_STATUS=1
    until [ $retries -ge 3 ]
    do
        echo "Stageout attempt $((retries+1)): env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}"
        env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}
        COPY_STATUS=$?
        if [ $COPY_STATUS -ne 0 ]; then
            echo "Failed stageout attempt $((retries+1))"
        else
            echo "Successful stageout with $retries retries"
            break
        fi
        retries=$[$retries+1]
        echo "Sleeping for 30m"
        sleep 30m
    done
    if [ $COPY_STATUS -ne 0 ]; then
        echo "Removing output file because gfal-copy crashed with code $COPY_STATUS"
        env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-rm --verbose ${COPY_DEST}
        REMOVE_STATUS=$?
        if [ $REMOVE_STATUS -ne 0 ]; then
            echo "Uhh, gfal-copy crashed and then the gfal-rm also crashed with code $REMOVE_STATUS"
            echo "You probably have a corrupt file sitting on hadoop now."
            exit 1
        fi
    fi
}


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
OUTPUTDIRSTORE=$(echo $OUTPUTDIR | sed "s#^/hadoop/cms/store#/store#")
for file in $(find -name '*.root'); do
    COPY_DEST="davs://redirector.t2.ucsd.edu:1094${OUTPUTDIRSTORE}/${OUTPUTFILENAME}_${INDEX}.root"
    echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] Attempting to gfal-copy file: $file to $COPY_DEST"
    stageout $file $COPY_DEST
done
