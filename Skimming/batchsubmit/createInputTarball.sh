#! /bin/bash

if [ -f input_$1.tar.gz ]; then
    rm ./input_$1.tar.gz
fi

tar -hcf input_$1.tar --exclude='.git' --exclude='my*.root' --exclude='*.tar*' --exclude='batchsubmit*' ../../../../../CMSSW_8_0_28
gzip ./input_$1.tar
