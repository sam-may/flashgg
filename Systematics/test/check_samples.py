import os, sys
import glob

procs = ["wh","zh","tth","thq","thw","vbf","ggh"]
for coupling in ["Hut", "Hct"]:
    for proc in procs:
        for year in ["2016", "2017", "2018"]:
            samples = glob.glob("workspaces_%s_%s_v4.3*/*%s*.root" % (coupling, year, proc))
            if len(samples) != 3:
                print "Only have these samples for %s %s %s" % (coupling, year, proc)
                for sample in samples:
                    print sample
            #os.system("ls -atlrh workspaces_%s_%s_v4.3*/*%s*.root" % (coupling, year, proc))
