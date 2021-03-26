PACKAGE=package.tar.gz
OUTPUTDIR=$1
OUTPUTFILENAME=$2
INPUTFILENAMES=$3
INDEX=$4
CMSSW_VER=$5
ARGS=$7

# probably need a few other args, like nEvents and xSec (or maybe not?)

echo "[wrapper] OUTPUTDIR	= " ${OUTPUTDIR}
echo "[wrapper] OUTPUTFILENAME	= " ${OUTPUTFILENAME}
echo "[wrapper] INPUTFILENAMES	= " ${INPUTFILENAMES}
echo "[wrapper] INDEX		= " ${INDEX}

echo "[wrapper] hostname  = " `hostname`
echo "[wrapper] date      = " `date`
echo "[wrapper] linux timestamp = " `date +%s`

######################
# Set up environment #
######################

export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

# Untar
rm package.tar.gz
#wget http://gftp-2.t2.ucsd.edu:1094/store/user/smay/FCNC/tarballs/microAOD_package_microAOD_v1.1_20May2020.tar.gz
xrdcp root://redirector.t2.ucsd.edu//store/user/smay/FCNC/tarballs/microAOD_package_microAOD_v1.1_20May2020.tar.gz .
mv microAOD_package_microAOD_v1.1_20May2020.tar.gz package.tar.gz
tar -xvf package.tar.gz
rm package.tar.gz

# Build
cd $CMSSW_VER/src/flashgg
echo "[wrapper] in directory: " ${PWD}
echo "[wrapper] attempting to build"
eval `scramv1 runtime -sh`
scramv1 b ProjectRename
scram b
eval `scramv1 runtime -sh`
pip install --user htcondor
cd $CMSSW_BASE/src/flashgg

echo "process.source = cms.Source(\"PoolSource\",
fileNames=cms.untracked.vstring(\"${INPUTFILENAMES}\".replace('/hadoop', 'file:/hadoop').split(\",\"))
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32( -1 ) )
" >> MicroAOD/test/microAODstd.py

echo ${ARGS//|/ }

# Create tag file
echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] running: cmsRun MicroAOD/test/microAODstd.py ${ARGS//|/ }"
cmsRun MicroAOD/test/microAODstd.py ${ARGS//|/ }
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "CMSSWERROR!! cmsRun crashed with an error. Deleting output file."
    rm myMicroAODOutputFile.root
fi

echo "[wrapper] output root files are currently: "
ls -lh *.root

if [[ $OUTPUTFILENAME = *"test_skim"* ]]; then

    echo "process.source = cms.Source(\"PoolSource\",
fileNames=cms.untracked.vstring(\"file:myMicroAODOutputFile.root\")
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32( -1 ) )
" >> Skimming/test/skim_cfg.py

    if [[ $ARGS = *"DoubleEG"* ]]; then
        sed -i 's/isMC = True/isMC = False/g' Skimming/test/skim_cfg.py
    fi

    if [[ $ARGS = *"EGamma"* ]]; then
        sed -i 's/isMC = True/isMC = False/g' Skimming/test/skim_cfg.py
    fi
    
    echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] running: cmsRun Skimming/test/skim_cfg.py ${ARGS//|/ }"
    cmsRun Skimming/test/skim_cfg.py ${ARGS//|/ }
    RETVAL=$?
    if [ $RETVAL -ne 0 ]; then
        echo "CMSSWERROR!! cmsRun crashed with an error. Deleting output file."
        rm test_skim.root
    fi

fi

# Copy output
eval `scram unsetenv -sh` # have to add this because CMSSW and gfal interfere with each other or something...
file="test_skim.root"
echo "[wrapper `date +\"%Y%m%d %k:%M:%S\"`] Attempting to gfal-copy file: $file to gsiftp://gftp.t2.ucsd.edu/${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root"
gfal-copy -p -f -t 4200 --verbose file://`pwd`/$file gsiftp://gftp.t2.ucsd.edu/${OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root --checksum ADLER32
