import sys, os
import time
import json

from metis.Sample import DirectorySample, Sample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser

class file:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
    def get_name(self):
        return self.name
    def get_nevents(self):
        return 1

def submit_fcnc_workspaces(datasets, metadata):
    total_summary = {}
    while True:
        all_complete = False
        for dataset, info in datasets.items():
            sample = DirectorySample( dataset = dataset, location = info["input_loc"])
            task = CondorTask(
                    sample = sample,
                    open_dataset = False,
                    flush = True,
                    files_per_output = metadata["fpo"],
                    output_name = "workspace_FCNC.root",
                    tag = metadata["job_tag"] + "_" + info["year"],
                    cmssw_version = metadata["cmssw_ver"],
                    executable = metadata["executable"],
                    tarfile = "dummy_tar",
                    condor_submit_params = { "sites" : "T2_US_UCSD" },
                    special_dir = metadata["hadoop_path"],
                    arguments = info["args"]
                    )
            task.process()
            if not task.complete():
                all_complete = False
            total_summary[dataset] = task.get_task_summary()
        #StatsParser(data = total_summary, webdir = "~/public_html/dump/FCNC_Workspaces_" + metadata["job_tag"] + "/").do()
        os.system("chmod -R 755 ~/public_html/dump/FCNC_Workspaces/")
        if all_complete:
            print("\n Job={} finished\n".format(metadata["job_tag"]))
            break
        print("Sleeping 1000 seconds ...")
        time.sleep(1000)

    return

def submit_workspaces(datasets, metadata):
    total_summary = {}
    while True:
        all_complete = False
        for dataset, info in datasets.items():
            files = info["files"]
            files = [file(name=x) for x in files]
            print "Args: ", info["args"]
            sample = Sample(dataset = info["proc"] + "_" + info["year"] + "_" + info["sample_name"], files = files)
            sample.info["nevts"] = 0
            task = CondorTask(
                    sample = sample,
                    open_dataset = False,
                    flush = True,
                    files_per_output = metadata["fpo"],
                    output_name = "workspace_FCNC.root",
                    tag = metadata["job_tag"],
                    cmssw_version = metadata["cmssw_ver"],
                    executable = metadata["executable"],
                    tarfile = "dummy_tar",
                    condor_submit_params = {"sites" : "T2_US_UCSD,T2_US_CALTECH,T2_US_MIT,T2_US_WISCONSIN,T2_US_Nebraska,T2_US_Vanderbilt,T2_US_Florida,T3_US_UCR,T3_US_OSG,T3_US_Baylor,T3_US_Colorado,T3_US_Rice,T3_US_PuertoRico,T3_US_Cornell,T3_US_FIT,T3_US_FIU,T3_US_OSU,T3_US_Rutgers,T3_US_TAMU,T3_US_TAMU,T3_US_TTU,T3_US_UCD,T3_US_UMD,T3_US_UMiss"},
                    #condor_submit_params = { "sites" : "T2_US_UCSD,T2_US_CALTECH,T2_US_MIT,T2_US_WISCONSIN,T2_US_Nebraska,T2_US_Purdue,T2_US_Vanderbilt,T2_US_Florida" },
                    special_dir = metadata["hadoop_path"],
                    arguments = info["args"]
                    )
            task.process()
            if not task.complete():
                all_complete = False
            total_summary[dataset] = task.get_task_summary()
        os.system("chmod -R 755 ~/public_html/dump/FCNC_Workspaces/")
        if all_complete:
            print("\n Job={} finished\n".format(metadata["job_tag"]))
            break
        print("Sleeping 1000 seconds ...")
        time.sleep(1000)

    return


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=str)
    p.add_argument("--datasets", type=str)
    p.add_argument("--proc", type=str)
    arguments = p.parse_args()

    with open(arguments.metadata, "r") as f_in:
        metadata = json.load(f_in)
    with open(arguments.datasets, "r") as f_in:
        datasets = json.load(f_in)

    if arguments.proc == "fcnc":
        submit_fcnc_workspaces(datasets, metadata)
    else:
        submit_workspaces(datasets, metadata)
