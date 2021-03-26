from __future__ import print_function

import ROOT
import glob
import sys

#files = glob.glob("/hadoop/cms/store/user/smay/FCNC/workspaces*v5.7*/*/*.root")
files = glob.glob("/hadoop/cms/store/user/smay/FCNC/workspaces*v5.10*/*/*.root")
print("Found %d files" % (len(files)))

bad_files = []

idx = 0
for file in files:
    idx += 1
    f = ROOT.TFile.Open(file)
    print("On file %d/%d" % (idx, len(files)), end='\r')
    if not f:
        print("File %s is BAD!" % file)
        bad_files.append(file)

print("%d/%d files checked have some issue" % (len(bad_files), len(files)))

with open("delete_bad_file.sh", "w") as f_out:
    for file in bad_files:
        f_out.write("rm %s\n" % file) 
