import sys, os
import glob
import json
import re
import numpy

def choose_year(sample):
    if "RunIISummer16MiniAODv3" in sample or "Run2016" in sample:
        return "2016"
    elif "RunIIFall17MiniAODv2" in sample or "Run2017" in sample:
        return "2017"
    elif "RunIIAutumn18MiniAOD" in sample or "Run2018" in sample:
        return "2018"
    else:
        return "-1"

def choose_production(sample):
    production = sample.split("/")[2]
    #print production
    production_pieces = production.split("-")
    final_production = ""
    for piece in production_pieces[5:-1]:
        final_production += piece + "-"
    final_production = final_production[:-1]
    #print final_production
    return final_production

def skip_samples(sample):
    bad_samples = ["DoubleMuon", "M60", "M65", "M70", "M75", "M80", "M85", "M90", "M95", "M100", "M105", "M110", "M115", "WminusH", "WplusH", "ggZH_HToGG", "Up", "Down", "PSWeights", "GluGluToHH"]
    for bad_sample in bad_samples:
        if bad_sample in sample:
            #print "Skipping %s" % sample
            return True
    return False

def identify_old_productions(productions, sample, target_production=None):
    if len(productions) == 1:
        return []

    if "EGamma" in sample or "DoubleEG" in sample or "SingleElectron" in sample or "DoubleMuon" in sample:
        return []

    if target_production:
        old_productions = []
        for production in productions:
            if production == target_production:
                print "Found target production of %s for sample %s" % (target_production, sample)
                continue
            old_productions.append(production)
        return old_productions

    print "Identifying old productions for %s" % sample 

    nominal_productions = []
    extensions = []
    for production in productions:
        if "ext" in production:
            extensions += [production]
        else:
            nominal_productions += [production]
    if len(nominal_productions) == 1:
        print "Only 1 nominal production: %s" % nominal_productions[0]
        print "And the following extensions:"
        for extension in extensions:
            print extension
        print "So keeping all of them\n\n"
        return []
    else:
        versions = []
        for production in nominal_productions:
            versions += [int(production[-1])]
        versions = numpy.asarray(versions)
        arg_selected = versions.argmax()
        old_productions = nominal_productions[:]
        old_productions.pop(arg_selected)
        print "Choosing this sample: %s" % (nominal_productions[arg_selected])
        print "And removing these samples:"
        for production in old_productions:
            print production
        print "\n\n"
        return old_productions

def get_samples_from_catalogs(catalogs, productions=None):
    print "Getting samples"
    samples = {}
    for catalog in catalogs:
        datasets = glob.glob("../../MetaData/data/%s/*.json" % catalog)
        for dataset in datasets:
            with open(dataset, "r") as f_in:
                info = json.load(f_in)
                for sample in info.keys():
                    #print sample
                    if skip_samples(sample):
                        continue
                    sample_name = sample.split("/")[1]
                    if sample_name not in samples.keys():
                        #print sample_name
                        samples[sample_name] = {}
                    year = choose_year(sample)
                    production = choose_production(sample)
                    if year not in samples[sample_name].keys():
                        samples[sample_name][year] = {}
                    if production not in samples[sample_name][year].keys():
                        samples[sample_name][year][production] = { "files" : [], "nevents" : 0, "weights" : 0}
                    for file in info[sample]["files"]:
                        if "bad" in file.keys():
                            if file["bad"]:
                                continue
                        samples[sample_name][year][production]["files"].append(file["name"])
                        samples[sample_name][year][production]["nevents"] += file["nevents"]
                        #if "weights" not in file.keys():
                        #    print file
                        if "weights" in file.keys(): 
                            samples[sample_name][year][production]["weights"] += file["weights"]
    # Get XS's
    for file in ["/home/users/sjmay/ttH/BabyMaker/CMSSW_10_5_0/src/flashgg/MetaData/data/cross_sections.json", "/home/users/sjmay/ttH/Loopers/scale1fb/cross_sections_flashgg.json"]:
        with open(file, "r") as f_in:
            cross_sections = json.load(f_in)
            for sample in samples.keys():
                if sample in cross_sections.keys() and "xs" not in samples[sample].keys():
                    samples[sample]["xs"] = cross_sections[sample]["xs"]
                    if "br" in cross_sections[sample].keys():
                        samples[sample]["xs"] *= cross_sections[sample]["br"]
                    if "filter_eff" in cross_sections[sample].keys():
                        samples[sample]["xs"] *= cross_sections[sample]["filter_eff"]
                #else:
                    #print "%s unmatched to a cross section" % sample
                    #samples[sample]["xs"] = 0.0
    for sample in samples.keys():
        if "xs" not in samples[sample].keys():
            #print "%s unmatched to a cross section" % sample
            samples[sample]["xs"] = 0.0

    # Remove productions that are superseded
    for sample in samples.keys():
        for year in samples[sample].keys():
            if year == "xs" or year == "-1":
                continue
            if productions and sample in productions.keys():
                target_production = productions[sample]
                to_remove = identify_old_productions(samples[sample][year].keys(), sample, target_production)
            else:
                to_remove = identify_old_productions(samples[sample][year].keys(), sample)
            for production in to_remove:
                del samples[sample][year][production]


    # Compute scale1fb's
    for sample in samples.keys():
        for year in samples[sample].keys():
            if year == "xs":
                continue
            sum_of_weights = 0.
            for production in samples[sample][year].keys():
                sum_of_weights += samples[sample][year][production]["weights"]
            if sum_of_weights != 0:
                scale1fb = (samples[sample]["xs"] * 1000.) / float(sum_of_weights) 
            else:
                print "Calculated 0 sum of weights for sample %s, year %s, production %s, please check!" % (sample, year, production)
                scale1fb = -1
            samples[sample][year]["scale1fb"] = scale1fb

    # Hack to include FCNC
    with open("/home/users/sjmay/ttH/Loopers/scale1fb/scale1fb.json", "r") as f_in:
        fcnc_samples = json.load(f_in)
        for sample in fcnc_samples.keys():
            #if "FCNC" not in sample:
            #    continue
            entry = {}
            entry["xs"] = fcnc_samples[sample]["xs"]
            for year in ["2016", "2017", "2018"]:
                entry[year] = {}
                for production in fcnc_samples[sample]["productions"]:
                    #if "RunIIFall17MiniAODv2" not in production:
                    #    continue
                    entry[year][production] = { "files" : -1, "nevents" : fcnc_samples[sample]["productions"][production]["n_events_tot"], "weights" : fcnc_samples[sample]["productions"][production]["sum_of_weights"] }
                    entry[year]["scale1fb"] = fcnc_samples[sample]["scale1fb_%s" % year]
            samples[sample] = entry

    return samples

def summarize_samples(samples):
    samples_lite = samples.copy()
    for sample in samples_lite.keys():
        for year in samples_lite[sample].keys():
            if year == "xs":
                continue
            for production in samples_lite[sample][year].keys():
                if production == "scale1fb":
                    continue
                samples_lite[sample][year][production]["files"] = len(samples_lite[sample][year][production]["files"])
    with open("samples.json", "w") as f_out:
        json.dump(samples_lite, f_out, indent=4, sort_keys=True)
