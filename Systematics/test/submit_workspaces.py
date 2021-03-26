import sys, os
import json
import datetime
import glob
import copy

d = datetime.datetime.today()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", help = "tag to identify this set of babies", type=str)
parser.add_argument("--years", help = "which year(s) to submit jobs for", type=str, default="2016,2017,2018")
parser.add_argument("--date", help = "date to distinguish this submission", type=str, default=d.strftime("%d-%B-%Y"))
parser.add_argument("--procs", help = "csv list of types of processes to submit", type=str, default = "sig,data,zh,fcnc")
parser.add_argument("--couplings", help = "csv list of couplings", type=str, default = "Hct,Hut")
parser.add_argument("--dry_run", help = "don't actually make tarball or submit", action="store_true")
parser.add_argument("--fcnc_wildcard", help = "wildcard to grab all fcnc samples", default = "/hadoop/cms/store/user/smay/FCNC/MicroAOD/*microAOD_v1.2_29May2020*/")
parser.add_argument("--fcnc_only", help = "only run on fcnc locally", action="store_true")
parser.add_argument("--save_tar", help = "don't remake tarball", action="store_true")
parser.add_argument("--no_syst", help = "don't run systematics", action="store_true")
parser.add_argument("--hadd_workspaces", help = "hadd all output workspaces", action="store_true")
args = parser.parse_args()

import parallel_utils
from flashgg_utils import *

sys.path.append("~/Utilities")

couplings = {}
for coupling in args.couplings.split(","):
    couplings[coupling] = {}

years = args.years.split(",")
syst = "False" if args.no_syst else "True"

meta_conds = {
        "2016" : "$CMSSW_BASE/src/flashgg/MetaData/data/MetaConditions/Era2016_RR-17Jul2018_v1.json",
        "2017" : "$CMSSW_BASE/src/flashgg/MetaData/data/MetaConditions/Era2017_RR-31Mar2018_v1.json",
        "2018" : "$CMSSW_BASE/src/flashgg/MetaData/data/MetaConditions/Era2018_RR-17Sep2018_v1.json"
}

for coupling in couplings.keys():
    for year in years:
        couplings[coupling][year] = {}
        couplings[coupling][year]["outdir"] = "workspaces_" + coupling + "_" + year + "_" + args.tag + "_" + args.date + "/"
        os.system("mkdir -p %s" %  couplings[coupling][year]["outdir"] )
        os.system("cp workspaceStd.py %s" %  couplings[coupling][year]["outdir"] )

tarfile = "package_" + args.tag + ".tar.gz"

if os.path.isfile(tarfile) and not args.save_tar:
    os.system("rm %s" % tarfile)

# Make 1 tarball
cmssw_ver = [x for x in os.path.expandvars("$CMSSW_BASE").split("/") if "CMSSW" in x][0]
if not args.dry_run and not args.save_tar:
    print "Using CMSSW version: ", cmssw_ver
    os.system("XZ_OPT='-3e -T24' tar -Jc --exclude='.git' --exclude='my*.root' --exclude='*.tar*' --exclude='merged_ntuple*.root' --exclude='*.out' --exclude='*.err' --exclude='*.log' --exclude '*Taggers/data/DNN_models/*' --exclude '*Taggers/data/*dijet*' --exclude '*76X*.root' --exclude '*76X*.xml' --exclude '*Taggers/data/DNN_models/*' --exclude '*Taggers/data/HHTagger/*' --exclude '*Taggers/data/ttHKiller/*' --exclude '*Systematics/test/workspaces*' --exclude '*.nfs*' --exclude '*Systematics/test/tasks*' -f %s ../../../../../%s/" % (tarfile, cmssw_ver))


productions = {}
procs = args.procs.split(",")
all_procs = "sig,data,zh,fcnc".split(",")
# Send tarball to multiple locations
for coupling in couplings.keys():
    for year in years:
        couplings[coupling][year]["stage_dir"] = "/hadoop/cms/store/user/smay/FCNC/" + couplings[coupling][year]["outdir"]
        os.system("mkdir -p %s" % couplings[coupling][year]["stage_dir"])
        if not args.dry_run and not args.save_tar:
            os.system("cp %s %s" % (tarfile, couplings[coupling][year]["stage_dir"] + "package.tar.gz"))
            os.system("hadoop fs -setrep -R 30 %s" % (couplings[coupling][year]["stage_dir"].replace("/hadoop","") + "package.tar.gz"))

        couplings[coupling][year]["datasets"] = {}
        for proc in all_procs:
            if proc == "fcnc":
                continue
            with open("wsJSONs/legacy_runII_v1_%s_%s.json" % (year, proc), "r") as f_in:
                datasets_to_add = json.load(f_in)
            for process, info in datasets_to_add["processes"].iteritems():
                if isinstance(info[0], list):
                    info = info[0]
                production = choose_production(info[0])                
                couplings[coupling][year]["datasets"][process] = { "sample" : info[0].split("/")[1], "catalog_name" : info[0], "cmdLine" : datasets_to_add["cmdLine"] , "production" : production}
                productions[info[0].split("/")[1]] = production
             

catalog_dict = { "2016" : "Era2016_RR-17Jul2018_v2", "2017" : "Era2017_RR-31Mar2018_v2", "2018" : "Era2018_RR-17Sep2018_v2" }
pu_dict = { 
    "2016" : "puTarget=6.557e-06,2.331e-05,6.347e-05,8.636e-05,0.0001235,0.0001654,0.0001932,0.0003625,0.0009901,0.002212,0.004983,0.0101,0.01683,0.0244,0.03264,0.0413,0.04865,0.05362,0.05642,0.0578,0.05863,0.05902,0.05837,0.05647,0.05367,0.0503,0.04647,0.04234,0.03807,0.03378,0.02953,0.02537,0.02139,0.0177,0.01437,0.01146,0.008964,0.006874,0.00515,0.003754,0.002652,0.001808,0.001186,0.0007463,0.0004497,0.0002591,0.0001426,7.497e-05,3.763e-05,1.806e-05,8.323e-06,3.713e-06,1.638e-06,7.458e-07,3.784e-07,2.312e-07,1.721e-07,1.463e-07,1.325e-07,1.227e-07,1.142e-07,1.06e-07,9.787e-08,8.98e-08,8.184e-08,7.409e-08,6.661e-08,5.949e-08,5.276e-08,4.648e-08,4.066e-08,3.533e-08,3.049e-08,2.614e-08,2.225e-08",
    "2017" : "puTarget=6.245e-06,2.63e-05,4.92e-05,9.084e-05,9.854e-05,0.0001426,0.0001557,0.0001656,0.0002269,0.0005395,0.001076,0.002034,0.003219,0.004616,0.006528,0.009201,0.01283,0.01707,0.02125,0.0251,0.02847,0.03118,0.03325,0.03486,0.03626,0.03758,0.0387,0.03937,0.03946,0.03892,0.03782,0.03627,0.03435,0.03211,0.02967,0.02719,0.02482,0.02264,0.0207,0.01907,0.01784,0.01709,0.01685,0.0171,0.01771,0.01849,0.01916,0.01945,0.01911,0.01804,0.01627,0.01399,0.01147,0.008976,0.006728,0.004848,0.003375,0.002281,0.001504,0.0009715,0.0006178,0.0003882,0.0002419,0.0001501,9.294e-05,5.768e-05,3.598e-05,2.263e-05,1.437e-05,9.233e-06,5.996e-06,3.933e-06,2.601e-06,1.731e-06,1.157e-06,7.743e-07,5.184e-07,3.466e-07,2.311e-07,1.535e-07,1.015e-07,6.676e-08,4.365e-08,2.836e-08,1.829e-08,1.171e-08,7.437e-09,4.685e-09,2.926e-09,1.812e-09,1.111e-09,6.754e-10,4.066e-10,2.424e-10,1.431e-10,8.363e-11,4.839e-11,2.771e-11,1.571e-11,8.814e-12",
    "2018" : "puTarget=1.105e-07,3.485e-06,2e-05,5.011e-05,8.593e-05,0.0001214,0.0001645,0.0002381,0.0003153,0.0004159,0.0006128,0.0009682,0.00154,0.002407,0.003656,0.005369,0.007596,0.01032,0.01345,0.0168,0.02011,0.02316,0.02579,0.02799,0.02987,0.03155,0.03314,0.03465,0.03608,0.03738,0.03851,0.03944,0.04016,0.04064,0.04085,0.04078,0.04035,0.03953,0.03828,0.03657,0.03442,0.03187,0.02899,0.0259,0.0227,0.01951,0.01645,0.01361,0.01106,0.008825,0.006927,0.005355,0.004082,0.003073,0.002289,0.001688,0.001234,0.0008952,0.0006447,0.0004608,0.0003269,0.00023,0.0001603,0.0001107,7.561e-05,5.108e-05,3.412e-05,2.253e-05,1.47e-05,9.484e-06,6.051e-06,3.819e-06,2.386e-06,1.475e-06,9.035e-07,5.48e-07,3.292e-07,1.958e-07,1.153e-07,6.722e-08,3.876e-08,2.21e-08,1.245e-08,6.927e-09,3.805e-09,2.062e-09,1.102e-09,5.807e-10,3.015e-10,1.542e-10,7.765e-11,3.85e-11,1.879e-11,9.023e-12,4.263e-12,1.981e-12,9.058e-13,4.072e-13,1.8e-13,7.823e-14"
}
lumi_dict = {
    "2016" : "targetLumi=35.9e+3",
    "2017" : "targetLumi=41.5e+3",
    "2018" : "targetLumi=59.8e+3"
}

catalogs = ["Era2016_RR-17Jul2018_v2", "Era2017_RR-31Mar2018_v2", "Era2018_RR-17Sep2018_v2"]
samples = get_samples_from_catalogs(catalogs, productions)

datasets = {
        "2016" : {},
        "2017" : {},
        "2018" : {}
        }

for dataset in datasets.keys():
    for proc in procs:
        datasets[dataset][proc] = {}

fcnc_map = {
    "FCNC_private_ST_HAD_HCT_2016_microAOD_v1.2_29May2020" : ("ST_HAD_HCT_2016_20200522_v1_STEP4_v1", "2016"),
    "TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8", "2018"),
    "TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8", "2018"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8", "2018"),
    "TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut-MadGraph5-pythia8", "2016"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8", "2016"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8", "2016"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8", "2016"),
    "TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aTleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8", "2017"),
    "TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hct-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hct-MadGraph5-pythia8", "2017"),
    "TT_FCNC-T2HJ_aThadronic_HToaa_eta_hct-MadGraph5-pythia8_TuneCUETP8M1_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-T2HJ_aThadronic_HToaa_eta_hct-MadGraph5-pythia8_TuneCUETP8M1", "2016"),
    "TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hut-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hut-MadGraph5-pythia8", "2017"),
    "TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8", "2017"),
    "ST_FCNC-TH_Thadronic_HToaa_eta_hct-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Thadronic_HToaa_eta_hct-MadGraph5-pythia8", "2018"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8", "2017"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hut_TuneCP5-MadGraph5-pythia8", "2018"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct_TuneCP5-MadGraph5-pythia8", "2017"),
    "TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8", "2016"),
    "TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hut-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hut-MadGraph5-pythia8", "2017"),
    "TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hct-MadGraph5-pythia8_TuneCUETP8M1_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hct-MadGraph5-pythia8_TuneCUETP8M1", "2016"),
    "TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hct-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hct-MadGraph5-pythia8", "2017"),
    "TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct-MadGraph5-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-T2HJ_aTleptonic_HToaa_eta_hct-MadGraph5-pythia8", "2016"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8", "2017"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hut-MadGraph5-pythia8", "2018"),
    "ST_FCNC-TH_Thadronic_HToaa_eta_hct-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Thadronic_HToaa_eta_hct-MadGraph5-pythia8", "2017"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8", "2017"),
    "ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Tleptonic_HToaa_eta_hct-MadGraph5-pythia8", "2018"),
    "ST_FCNC-TH_Thadronic_HToaa_eta_hut-MadGraph5-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_tauDecays_94X_mc2017_realistic_v14-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Thadronic_HToaa_eta_hut-MadGraph5-pythia8", "2017"),
    "FCNC_private_TT_T2HJ_HAD_HUT_2018_microAOD_v1.2_29May2020" : ("TT_T2HJ_HAD_HUT_2018_20200522_v1_STEP4_v1", "2018"),
    "FCNC_private_TT_T2HJ_HAD_HCT_2018_microAOD_v1.2_29May2020" : ("TT_T2HJ_HAD_HCT_2018_20200522_v1_STEP4_v1", "2018"),
    "FCNC_private_ST_HAD_HUT_2016_microAOD_v1.2_29May2020" : ("ST_HAD_HUT_2016_20200522_v1_STEP4_v1", "2016"),
    "FCNC_private_TT_aT2HJ_HAD_HUT_2018_microAOD_v1.2_29May2020" : ("TT_aT2HJ_HAD_HUT_2018_20200522_v1_STEP4_v1", "2018"),
    "FCNC_private_TT_aT2HJ_HAD_HCT_2018_microAOD_v1.2_29May2020" : ("TT_aT2HJ_HAD_HCT_2018_20200522_v1_STEP4_v1", "2018"),
    "TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hut-MadGraph5-pythia8_TuneCUETP8M1_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hut-MadGraph5-pythia8_TuneCUETP8M1", "2016"),
    "TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hut-MadGraph5-pythia8_TuneCUETP8M1_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hut-MadGraph5-pythia8_TuneCUETP8M1", "2016"),
    "ST_FCNC-TH_Thadronic_HToaa_eta_hut-MadGraph5-pythia8_RunIIAutumn18MiniAOD-tauDecays_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_microAOD_v1.2_29May2020" : ("ST_FCNC-TH_Thadronic_HToaa_eta_hut-MadGraph5-pythia8", "2018")
}

if "fcnc" in procs:
    for dataset in [dir for dir in glob.glob(args.fcnc_wildcard) if "FCNC" in dir]:
        sample = dataset.split("/")[-2] # assumes a trailing "/"
        smp_match, year = fcnc_map[sample]

        print dataset, smp_match, year

        datasets[year]["fcnc"][sample] = { "input_loc" : dataset }

        normalizationInfo = ""
        split_factor = 3

        normalizationInfo = " normalizationInfo=%.6f,%.6f splitFactor=%d" % (samples[smp_match]["xs"], (samples[smp_match]["xs"]*1000.) / samples[smp_match][year]["scale1fb"], split_factor)
        if "TT_FCNC" in dataset or "private_TT" in dataset: 
            genTopPtReweightInfo = " doGenTopPtReweighting=True "
        else:
            genTopPtReweightInfo = ""
        print dataset, genTopPtReweightInfo
        datasets[year]["fcnc"][sample]["args"] = normalizationInfo + genTopPtReweightInfo
        datasets[year]["fcnc"][sample]["year"] = year

for year in years:
    for proc in procs:
        if proc == "fcnc":
            continue
        with open("wsJSONs/legacy_runII_v1_%s_%s.json" % (year, proc), "r") as f_in:
            datasets_to_add = json.load(f_in)
        for sample, info in datasets_to_add["processes"].iteritems():
            if isinstance(info[0], list):
                info = info[0]
            sample_name = info[0].split("/")[1]
            catalog_name = info[0]
            cmdLine = datasets_to_add["cmdLine"]
            if "120" in sample or "125" in sample or "130" in sample:
                split_factor = 2
                cmdLine += " splitFactor=%d" % split_factor # multiply SM Higgs by 2 to account for optimization / final fit splits
            if sample_name in samples.keys():
                xs = samples[sample_name]["xs"]

                print "Sample name is %s" % sample_name
                if "THQ" in sample_name or "THW" in sample_name:
                    print "\n\n\n\n Adding Reweight to sample: %s\n\n\n\n" % sample_name
                    cmdLine += " WeightName=rwgt_12 "

                # Check for scale1fb first from the proper year
                if year in samples[sample_name].keys() and not (sample_name == "VBFHToGG_M125_13TeV_amcatnlo_pythia8" and year == "2016"): 
                    scale1fb = samples[sample_name][year]["scale1fb"]
                # If it doesn't exist, this means we are using the 2017 sample in place of a 2016/2018 sample that is missing
                    sample_year = year
                else:
                    print "Using 2017 sample for year: %s, sample: %s" % (year, sample_name)
                    scale1fb = samples[sample_name]["2017"]["scale1fb"]
                    sample_year = "2017"
                    #print "cmdLine before", cmdLine
                    cmdLine = cmdLine.replace("campaign=%s" % catalog_dict[year], "campaign=%s" % catalog_dict[sample_year])
                    cmdLine = cmdLine.replace(pu_dict[year], pu_dict[sample_year])

                production_names = []
                for production in samples[sample_name][sample_year].keys():
                    if production == "scale1fb":
                        continue
                    else:
                        production_names.append(production)
                if len(production_names) > 1 and not ("DoubleEG" in sample or "EGamma" in sample):
                    print "More than one possible production to pick for sample %s" % sample_name
                if len(production_names) == 0:
                    print "Did not identify production for sample %s, year %s" % (sample_name, year)
                    continue
                files = []
                nEvents = 0
                weights = 0

                for production in production_names:
                    files += samples[sample_name][sample_year][production]["files"]
                    nEvents += samples[sample_name][sample_year][production]["nevents"]
                    weights += samples[sample_name][sample_year][production]["weights"]

                datasets[year][proc][sample] = {
                        "sample_name" : sample_name,
                        "catalog_name" : catalog_name,
                        "cmdLine" : cmdLine,
                        "xs" : xs,
                        "scale1fb" : scale1fb,
                        "production_names" : production_names,
                        "files" : files,
                        "nEvents" : "nEvents",
                        "weights" : weights,
                        "args" : cmdLine + " dataset=%s" % catalog_name + " processId=%s" % sample,
                        "proc" : proc,
                        "year" : year,
                        }

            else:
                print "Could not find sample %s in flashgg catalog!!!" % sample_name


metadata = {
        "job_tag" : args.tag,
        "cmssw_ver" : cmssw_ver,
}

fpo = {
        "data" : 25,
        "sig" : 1,
        "fcnc" : 1,
        "zh" : 1,
}

command_list = []


for coupling, info in couplings.iteritems():
    if coupling == "Hut":
        coupling_selection = "fcncHutTagsOnly=True"
    elif coupling == "Hct":
        coupling_selection = "fcncHctTagsOnly=True"
    syst_selection = "doSystematics=%s" % syst
    for proc in procs:
        if proc == "fcnc":
            proc_name = "fcnc_%s_125" % coupling.lower()
        else:
            proc_name = proc
        #proc_name = "fcnc_125" if proc == "fcnc" else proc
        for year in years:
            if len(datasets[year].keys()) == 0:
                continue
            metadata_ = copy.deepcopy(metadata)
            metadata_["job_tag"] += "_" + coupling

            fcnc_executable = "%s/executable_%s.sh" % (info[year]["outdir"], proc)
            os.system("cp fcnc_executable.sh %s" % fcnc_executable)
            os.system("sed -i 's@MY_DIR@%s@g' %s" % (info[year]["outdir"], fcnc_executable))

            use_xrdcp = proc == "sig" or proc == "zh"
            if use_xrdcp:
                os.system("sed -i 's@XRDCP@%s@g' %s" % ("xrdcp root://cms-xrd-global.cern.ch:1094/${INPUTFILENAMES} .", fcnc_executable))
            else:
                os.system("sed -i 's@XRDCP@%s@g' %s" % ("", fcnc_executable))

            if proc == "fcnc":
                command = "$CMSSW_BASE/src/flashgg/Systematics/test/workspaceStd.py doHTXS=True useAAA=True doPdfWeights=False processId=%s %s %s %s %s %s" % (proc_name, coupling_selection, syst_selection, "outputFile=" + couplings[coupling][year]["outdir"] + "/output_FCNC_USER.root", "jobId=-1", "metaConditions=" + meta_conds[year]) 
            else:
                command = "$CMSSW_BASE/src/flashgg/Systematics/test/workspaceStd.py doHTXS=True doPdfWeights=False %s %s %s %s" % (coupling_selection, syst_selection, "outputFile=" + couplings[coupling][year]["outdir"] + "/output_FCNC_USER.root", "jobId=-1")
            os.system("sed -i 's@COMMAND@%s@g' %s" % (command, fcnc_executable))

            print(command)

            metadata_["executable"] = fcnc_executable
            metadata_["tarfile"] = info[year]["outdir"] + "package.tar.gz"
            metadata_["hadoop_path"] = info[year]["stage_dir"].replace("/hadoop/cms/store/user/smay/","")
            metadata_["args"] = ""
            metadata_["fpo"] = fpo[proc]

            metadata_file = info[year]["outdir"] + "%s_metadata.json" % proc
            with open(metadata_file, "w") as f_out:
                json.dump(metadata_, f_out, sort_keys=True, indent=4)

            datasets_file = info[year]["outdir"] + "%s_datasets.json" % proc

            datasets_trimmed = copy.deepcopy(datasets[year][proc])
            for key in datasets_trimmed.keys():
                if ("eta_" + coupling.lower()) in key or coupling.upper() in key or proc != "fcnc":
                    continue
                else:
                    del datasets_trimmed[key]

            with open(datasets_file, "w") as f_out:
                json.dump(datasets_trimmed, f_out, sort_keys=True, indent=4)

            function = "python submit_jobs.py --proc %s --metadata %s --datasets %s" % (proc, metadata_file, datasets_file)

            couplings[coupling][year]["command_" + proc] = function
            command_list.append(function)

# Bookkeeping
with open("ws_jobs_summary_%s.json" % args.tag, "w") as f_out:
    json.dump(couplings, f_out, sort_keys=True, indent=4)
with open("ws_datasets_%s.json" % args.tag, "w") as f_out:
    json.dump(datasets, f_out, sort_keys=True, indent=4)

# Submit all
if args.dry_run:
    for command in command_list:
        print "\n\nCOMMAND"
        print command
else:
    #parallel_utils.submit_jobs(command_list, 1, True, True)
    parallel_utils.submit_jobs(command_list, len(command_list), True, True)

def search_for_command(dictionary, command_list = [], command = "command"):
    for key, info in dictionary.iteritems():
        if not isinstance(info, dict):
            continue
        elif command in info.keys():
            print key, info.keys()
            print "hadding %d workspaces to create master workspace %s" % (len(info["inputs"]), info["master"])
            if len(info["inputs"]) > 0 and not command == "":
                command_list.append(info[command])
                #os.system(info["command"])
        else:
            search_for_command(info, command_list, command)
    return command_list

def trim_dictionary(dictionary, to_remove):
    for key, info in dictionary.iteritems():
        if not isinstance(info, dict):
            continue
        elif to_remove in info.keys():
            del info[to_remove]
        else:
            trim_dictionary(info, to_remove)

max_ws = 300
def hadd_workspaces(master, targets):
    if os.path.exists(master):
        print "File %s already exists" % master
        return ""

    else:
        print "File %s does not already exist" % master

    if len(targets.split(" ")) <= max_ws:
        if len(targets.split(" ")) < 25:
            return "/usr/bin/ionice -c2 -n7 hadd_workspaces %s %s" % (master, targets)
        else:
            return "/usr/bin/ionice -c2 -n7 python hadd_parallel.py %s %s" % (master, targets)

    target_list = targets.split(" ")
    command = ""
    intermediate_files = ""
    for i in range((len(target_list)/max_ws) + 1):
        intermediate_file = "intermediate_ws_%s_%d.root" % (master.split("/")[-1].replace(".root",""),i)
        partial_files = ""
        for j in range(i*max_ws, min((i+1)*max_ws, len(target_list))):
            partial_files += "%s " % target_list[j]
        intermediate_command = "/usr/bin/ionice -c2 -n7 python hadd_parallel.py %s %s;" % (intermediate_file, partial_files)
        intermediate_files += "%s " % intermediate_file
        command += intermediate_command
        
    command += "/usr/bin/ionice -c2 -n7 hadd_workspaces %s %s;" % (master, intermediate_files)
    for file in intermediate_files.split(" "):
        if file.isspace() or not file:
            continue
        command += "rm %s;" % file

    return command
        

if args.hadd_workspaces:
    workspaces = {}
    hadd_summary = {}
    for coupling, info in couplings.iteritems():
        workspaces[coupling] = { "data" : {}, "sm_higgs" : {}, "fcnc" : {} }
        for cat, cat_info in workspaces[coupling].iteritems():
            for year in years:
                cat_info[year] = {}

    for coupling, info in workspaces.iteritems():
        for cat, cat_info in info.iteritems():
            if (cat not in procs and cat != "sm_higgs") or (cat == "sm_higgs" and "zh" not in procs and "sig" not in procs):
                continue
            if cat == "data":
                cat_info["2016"] = { "globber" : "DoubleEG" }
                cat_info["2017"] = { "globber" : "DoubleEG" }
                cat_info["2018"] = { "globber" : "EGamma" }
                for year in years:
                    cat_info[year]["inputs"] = glob.glob(couplings[coupling][year]["stage_dir"] + "/*" + cat_info[year]["globber"] + "*/*.root")
                    cat_info[year]["glob_command"] = couplings[coupling][year]["stage_dir"] + "/*" + cat_info[year]["globber"] + "*/*.root" 
                    cat_info[year]["n_inputs"] = len(cat_info[year]["inputs"])
                    cat_info[year]["targets"] = ""
                    for input in cat_info[year]["inputs"]:
                        cat_info[year]["targets"] += "%s " % input
                    cat_info[year]["master"] = couplings[coupling][year]["outdir"] + "/ws_merged_data_%s_%s.root" % (coupling, year)
                    cat_info[year]["command"] = hadd_workspaces(cat_info[year]["master"], cat_info[year]["targets"])
                cat_info["inputs"] = []
                for year in years:
                    cat_info["inputs"] += cat_info[year]["inputs"]
                cat_info["n_inputs"] = len(cat_info["inputs"])
            if cat == "fcnc":
                for year in years:
                    cat_info[year] = { "tt" : { "globber" : ["TT_FCNC", "FCNC_private_TT"] }, "st" : { "globber" : ["ST_FCNC", "FCNC_private_ST"] } }
                    for subcat, subcat_info in cat_info[year].iteritems():
                        subcat_info["inputs"] = glob.glob(couplings[coupling][year]["stage_dir"] + "/*" + subcat_info["globber"][0] + "*/*.root")
                        subcat_info["inputs"] += glob.glob(couplings[coupling][year]["stage_dir"] + "/*" + subcat_info["globber"][1] + "*/*.root")
                        subcat_info["glob_command"] = [couplings[coupling][year]["stage_dir"] + "/*" + globber + "*/*.root" for globber in subcat_info["globber"]]
                        subcat_info["n_inputs"] = len(subcat_info["inputs"] )
                        subcat_info["targets"] = ""
                        for input in subcat_info["inputs"]:
                            subcat_info["targets"] += "%s " % input
                        subcat_info["master"] = couplings[coupling][year]["outdir"] + "/ws_merged_fcnc_%s_%s_%s.root" % (coupling, subcat, year)
                        subcat_info["command"] = hadd_workspaces(subcat_info["master"], subcat_info["targets"])

            if cat == "sm_higgs":
                for year in years:
                    cat_info[year] = { 
                        "tth" : { "globber" : "ttHJetToGG" },
                        "ggh" : { "globber" : "GluGluHToGG" },
                        "thq" : { "globber" : "THQ" },
                        "thw" : { "globber" : "THW" },
                        "wh" : { "globber" : "sig_%s_VHToGG" % year },
                        "zh" : { "globber" : "zh_%s_VHToGG" % year },
                        "bbh" : { "globber" : "bbH" },
                        "vbf" : { "globber" : "VBF" }
                    }
                    for subcat, subcat_info in cat_info[year].iteritems():
                        for mass_point in ["120", "125", "130"]:
                            subcat_info[mass_point] = {}
                            subcat_info[mass_point]["inputs"] = glob.glob(couplings[coupling][year]["stage_dir"] + "/*" + subcat_info["globber"] + "*" + mass_point + "*/*.root")
                            subcat_info[mass_point]["glob_command"] = couplings[coupling][year]["stage_dir"] + "/*" + subcat_info["globber"] + "*" + mass_point + "*/*.root"
                            subcat_info[mass_point]["n_inputs"] = len(subcat_info[mass_point]["inputs"])
                            subcat_info[mass_point]["targets"] = ""
                            for input in subcat_info[mass_point]["inputs"]:
                                subcat_info[mass_point]["targets"] += "%s " % input
                            subcat_info[mass_point]["master"] = couplings[coupling][year]["outdir"] + "/ws_merged_sm_higgs_%s_%s_%s_%s.root" % (coupling, subcat, mass_point, year)
                            subcat_info[mass_point]["command"]  = hadd_workspaces(subcat_info[mass_point]["master"], subcat_info[mass_point]["targets"]) 

    # add all data files to make master data file
    if "data" in procs:
        for coupling, info in workspaces.iteritems():
            info["data"]["master"] = (os.popen("pwd").read()).rstrip() + "/" + couplings[coupling][year]["outdir"] + "/ws_merged_data_%s_all.root" % (coupling)
            info["data"]["targets"] = ""
            for year in years:
                info["data"]["targets"] += info["data"][year]["master"] + " "
            info["data"]["master_command"] = hadd_workspaces(info["data"]["master"], info["data"]["targets"])

    with open("ws_hadd_summary_%s.json" % args.tag, "w") as f_out:
        json.dump(workspaces, f_out, sort_keys=True, indent=4)

    workspaces_summary = copy.deepcopy(workspaces)
    trim_dictionary(workspaces_summary, "targets")
    trim_dictionary(workspaces_summary, "inputs")
    trim_dictionary(workspaces_summary, "command")
    trim_dictionary(workspaces_summary, "globber")

    with open("ws_hadd_summary_trimmed_%s.json" % args.tag, "w") as f_out:
        json.dump(workspaces_summary, f_out, sort_keys=True, indent=4)

    command_list = search_for_command(workspaces)
    command_list = [command for command in command_list if not command == ""]
    command_list_separated = []
    for command in command_list:
        command_list_separated += command.split(";")
    parallel_utils.submit_jobs(command_list_separated, 1)

    command_list = search_for_command(workspaces, [], "master_command")
    command_list = [command for command in command_list if not command == ""]
    parallel_utils.submit_jobs(command_list, 1)

    # Combine st and tt fcnc
    if "fcnc" in procs:
        for coupling, info in couplings.iteritems():
            for year in years:
                master = couplings[coupling][year]["outdir"] + "/ws_merged_fcnc_%s_tt_st_%s.root" % (coupling, year)
                if not os.path.exists(master):
                    command = "hadd_workspaces %s %s %s" % (master, couplings[coupling][year]["outdir"] + "/ws_merged_fcnc_%s_tt_%s.root" % (coupling, year), couplings[coupling][year]["outdir"] + "/ws_merged_fcnc_%s_st_%s.root" % (coupling, year))
                    print command
                    os.system(command)

