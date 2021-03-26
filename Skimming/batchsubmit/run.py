import glob
import os
import subprocess
import time
import sys

tag = "2016_skim_v3_jetPt20"

submitJobs = False  # set to False if you've already submitted jobs and just want to monitor, or if you just want to check for missing files
sweeprootExisting = True # set to False to skip sweeprooting on existing files. For if you just want to check for new cms4/resubmit
removeLogs = False # remove all condor log files after successful completion

def getCompletedFiles():
    global tag, samples
    files = set()
    for s in samples:
        files.update(set(glob.glob("/hadoop/cms/store/user/bemarsh/flashgg/MicroAOD_skim/{0}/*/*/*.root".format(tag))))
    return files

def sweepRoot(files):
    global samples, tag

    cmd = "sweeproot/sweepRoot -b -o Events"
    for fname in files:
        cmd += " "+fname
        sweeprooted.add(fname)

    # print '\n'+cmd
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, err = p.communicate()
    # print out
    for line in out.split('\n'):
        if line.startswith("BAD FILE"):
            print '\n'+line
            sweeprooted.remove(line.split(":")[1].strip())
            subprocess.call("hadoop fs -rm -r "+line.split(":")[1].replace("/hadoop",""), shell=True)
    

def deleteLogFiles():
    global tag
    subprocess.call("rm -r /data/tmp/bemarsh/condor_job_logs/{0}*/*.out".format(tag), shell=True)
    subprocess.call("rm -r /data/tmp/bemarsh/condor_job_logs/{0}*/*.err".format(tag), shell=True)
    subprocess.call("rm -r /data/tmp/bemarsh/condor_submit_logs/{0}*/*.log".format(tag), shell=True)
    
    
def watchCondorJobs(sweeprootWhileWaiting=False):
    global sweeprooted, haveDeletedLogs
    print "* Waiting and watching..."
    NJOBS = 1
    while NJOBS > 0:
        out = subprocess.check_output(["condor_q", "bemarsh"]).split('\n')[-2]
        NJOBS = int(out.split()[0])
        nidle = int(out.split(";")[1].split(",")[2].strip().split()[0])
        nrunning = int(out.split(";")[1].split(",")[3].strip().split()[0])
        nheld = int(out.split(";")[1].split(",")[4].strip().split()[0])
        print "  {0} jobs left. {1} idle, {2} running, {3} held".format(NJOBS, nidle, nrunning, nheld)
        if nheld > 0:
            print "* Releasing held jobs..."
            os.system("condor_release bemarsh")
        if NJOBS > 0:
            print "  Checking again in 5 min..."
            curTime = time.time()
            if sweeprootWhileWaiting:
                newFiles = getCompletedFiles().difference(sweeprooted)
                if len(newFiles) > 0:
                    print "  Sweeprooting {0} files while waiting...".format(len(newFiles)),
                    sweepRoot(newFiles)
                    if removeLogs:
                        deleteLogFiles()
                    print "Done!"
            remainingTime = 5*60 - (time.time()-curTime)
            # remainingTime = 10 - (time.time()-curTime)
            if remainingTime > 0:
                time.sleep(remainingTime)
    print "* condor jobs finished!"


        
print "* Running skimmer for tag \"{0}\"".format(tag)
samples = []
for fname in glob.glob("configs_{0}/*.cmd".format(tag)):
    fname = fname.split("/")[1]
    if "resubmit" in fname:
        continue
    pos = fname.find(tag)
    samp = fname[pos+len(tag)+1:].split(".")[0]
    samples.append(samp)

print "* Found {0} samples:".format(len(samples))
for s in samples:
    print "   ", s

if not sweeprootExisting:
    sweeprooted = getCompletedFiles().copy()
else:
    sweeprooted = set()

if submitJobs:
    print "* Submitting condor jobs"
    for s in samples:
        print s
        subprocess.call("condor_submit configs_{0}/config_{0}_{1}.cmd".format(tag, s), shell=True)


NresubmitFiles = 1
while NresubmitFiles > 0:
    watchCondorJobs(sweeprootWhileWaiting=True)

    newFiles = getCompletedFiles().difference(sweeprooted)
    if len(newFiles)>0:
        print "* sweeprooting remaining files..."
        sweepRoot(newFiles)
                 
    subprocess.call("rm -f configs_{0}/*resubmit*.cmd".format(tag), shell=True)
    for s in samples:
        subprocess.call("python checkForMissingJobs.py configs_{0}/config_{0}_{1}.cmd".format(tag,s), shell=True)

    resubmitFiles = glob.glob("configs_{0}/*resubmit*.cmd".format(tag))
    NresubmitFiles = len(resubmitFiles)
    if NresubmitFiles > 0:
        for f in resubmitFiles:
            subprocess.call("condor_submit "+f+" > /dev/null", shell=True)

print "* WOO! All files are good!"
