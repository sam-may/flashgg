#! /bin/bash

if [ -f package.tar.xz ]; then
    rm ./package.tar.xz
fi

XZ_OPT='-9e -T24' tar -Jc --exclude='.git' --exclude='my*.root' --exclude='*.tar*' --exclude='merged_ntuple*.root' --exclude='*.out' --exclude='*.err' --exclude='*.log' --exclude *MicroAOD/BatchSubmit/tasks/* --exclude *MetaData/data/Era201*/*.json --exclude '*Taggers/data/DNN_models/*' --exclude '*Taggers/data/*dijet*' --exclude '*76X*.root' --exclude '*76X*.xml' --exclude '*Taggers/data/DNN_models/*' --exclude '*Taggers/data/HHTagger/*' --exclude '*Taggers/data/ttHKiller/*' -f package.tar.gz ../../../../../$CMSSW_VERSION
