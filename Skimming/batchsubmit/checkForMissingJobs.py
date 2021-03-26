import sys
import os

fin = open(sys.argv[1])

groups = [[]]
for line in fin:
    if line.strip()=="" and groups[-1]!=[]:
        groups.append([])
        continue
    groups[-1].append(line)

if groups[0] == []:
    groups = groups[1:]

if groups[-1] == []:
    groups = groups[:-1]

header = groups[0]
jobs = groups[1:]
missing_jobs = []

for job in jobs:
    args = job[2]
    if args.startswith("#"):
        continue
    if not args.startswith("arguments"):
        print job
        raise Exception(args)
    args = args.split("=")[1].split()
    if not os.path.exists(args[2]):
        missing_jobs.append(job)
        print args[2]

if len(missing_jobs) > 0:
    fout = open(sys.argv[1].replace(".cmd","_resubmit.cmd"), 'w')
    for line in header:
        fout.write(line)
    for job in missing_jobs:
        fout.write("\n")
        for line in job:
            fout.write(line)

    fout.close()
