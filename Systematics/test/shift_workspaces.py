import os, sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", help = "tag to identify this set of babies", type=str)
args = parser.parse_args()

def ws_name(coupling, year, tag, proc, mass_point):
    return "workspaces_%s_%s_%s/ws_merged_sm_higgs_%s_%s_%s_%s.root" % (coupling, year, tag, coupling, proc, mass_point, year)

def ws_name_fcnc(coupling, year, tag, mass_point = -1):
    if mass_point > 0:
        return "workspaces_%s_%s_%s/ws_merged_fcnc_%s_tt_st_%s_%s.root" % (coupling, year, tag, coupling, mass_point, year)
    else:
        return "workspaces_%s_%s_%s/ws_merged_fcnc_%s_tt_st_%s.root" % (coupling, year, tag, coupling, year)

def identify_missing_ws(coupling, year, tag, proc):
    ws = {}
    for mass_point in ["120", "125", "130"]:
        if not os.path.exists(ws_name(coupling, year, tag, proc, mass_point)):
            ws[mass_point] = False
        else:
            ws[mass_point] = True

    if not ws["125"]:
        print "[WARNING] We assume the M125 ws exists for all samples, but not present for %s, %s, %s, %s" % (coupling, year, tag, proc)

    for mass_point in ws.keys():
        if not ws[mass_point]:
            command = "python mgg_shifter.py --inputFile %s --inputMass 125 --targetMass %s" % (ws_name(coupling, year, tag, proc, "125"), mass_point)
            print command
            os.system(command)

couplings = ["Hut", "Hct"]
years = ["2016", "2017", "2018"]
procs = ["tth", "zh", "wh", "vbf", "bbh", "thw", "thq", "ggh"]
mass_points = ["120", "125", "130"]

for coupling in couplings:
    for year in years:
        # sm higgs
        for proc in procs:
            identify_missing_ws(coupling, year, args.tag, proc)

        # fcnc
        copy_ws = "cp %s %s" % (ws_name_fcnc(coupling, year, args.tag), ws_name_fcnc(coupling, year, args.tag, "125"))
        shift_120 = "python mgg_shifter.py --inputFile %s --inputMass 125 --targetMass 120" % (ws_name_fcnc(coupling, year, args.tag, "125"))
        shift_130 = "python mgg_shifter.py --inputFile %s --inputMass 125 --targetMass 130" % (ws_name_fcnc(coupling, year, args.tag, "125"))
        for command in [copy_ws, shift_120, shift_130]:
            print command
            os.system(command)
