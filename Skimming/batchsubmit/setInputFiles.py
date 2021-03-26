import sys

infiles = ",".join(['"'+s+'"' for s in sys.argv[1].split(",")])

text = open("Skimming/test/skim_cfg.py").read()
text = text.replace('"PUTFILENAMEHERE"',infiles)

if "mcRun2" in infiles:
    text = text.replace("isMC = False","isMC = True")

fid = open("temp_cfg.py",'w')
fid.write(text)
fid.close()
