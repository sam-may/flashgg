import os, sys
import glob

couplings = ["Hut", "Hct"]
years = ["2016", "2017", "2018"]

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--base_tag", help = "tag for original workspaces", type=str)
parser.add_argument("--new_tag", help = "tag for new fcnc workspaces to replace old ones", type=str)
args = parser.parse_args()

for coupling in couplings:
    for year in years:
        files = glob.glob("workspaces_%s_%s_%s/*" % (coupling, year, args.base_tag))
        files = [x for x in files if "fcnc" not in x]
        for file in files:
            command = "cp %s %s" % (file, "workspaces_%s_%s_%s/" % (coupling, year, args.new_tag))
            print command
            os.system(command)

