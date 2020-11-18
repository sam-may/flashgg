import sys, os

n_events = -1 
file_names = "DoubleEG"
meta_conditions = "MetaData/data/MetaConditions/Era2018_RR-17Sep2018_v1.json"
processId = "tth_125"

if len(sys.argv) >= 4:
  file_names = sys.argv[2].replace("/hadoop", "file:/hadoop").split(",")
  for i in range(len(file_names)):
      if file_names[i].startswith("/store"):
          file_names[i] = "root://cms-xrd-global.cern.ch/" + file_names[i]
  meta_conditions = sys.argv[3]
  print "Found at least 5 args, setting filenames to %s and meta conditions %s" % (file_names, meta_conditions)

if len(sys.argv) >= 5:
  n_events = int(sys.argv[4])
  print "Setting max number of events to %d" % (n_events)


doSystematics = True

import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.ParameterSet.VarParsing as VarParsing
from flashgg.Systematics.SystematicDumperDefaultVariables import minimalVariables,minimalHistograms,minimalNonSignalVariables,systematicVariables
from flashgg.Systematics.SystematicDumperDefaultVariables import minimalVariablesHTXS,systematicVariablesHTXS
import os
from flashgg.MetaData.MetaConditionsReader import *

# SYSTEMATICS SECTION
process = cms.Process("FLASHggTag")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32( 1000 )

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(file_names))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(n_events))

systlabels = [""]
phosystlabels = []
metsystlabels = []
jetsystlabels = []
elesystlabels = []
musystlabels = []

from flashgg.MetaData.MetaConditionsReader import *
metaConditions = MetaConditionsReader(meta_conditions)
print "Metaconds: ", metaConditions["L1Prefiring"]

ISDATA = False
if "DoubleEG" in file_names[0] or "EGamma" in file_names[0]:
  ISDATA = True

ISSIGNAL = False
signal_strings = ["ttHJetToGG", "ttHToGG", "THQ", "THW", "VBF", "GluGluHToGG", "VHToGG", "bbH"]
if any([x in file_names[0] for x in signal_strings]):
  ISSIGNAL = True

signal_strings_dict = {
    "ttHJetToGG" : "tth",
    "ttHToGG" : "powheg_tth",
    "THQ" : "th",
    "THW" : "th",
    "VBF" : "vbf",
    "GluGluHToGG" : "ggh",
    "VHToGG" : "vh",
    "bbH" : "bbh"
}

mass_dict = {
    "M120" : "120",
    "M123" : "123",
    "M124" : "124",
    "M125" : "125",
    "M126" : "126",
    "M127" : "127",
    "M128" : "128"
}

if ISSIGNAL:
    for signal_string in signal_strings_dict.keys():
        if signal_string in file_names[0]:
            processId = signal_strings_dict[signal_string]
    for mass in mass_dict.keys():
        if mass in file_names[0]:
            processId += "_" + mass_dict[mass]
elif ISDATA:
    processId = "Data"
else:
    processId = "bkg"
print "ProcessId: %s" % processId

### Global Tag
from Configuration.AlCa.GlobalTag import GlobalTag
if ISDATA:
    process.GlobalTag.globaltag = str(metaConditions['globalTags']['data'])
else:
    process.GlobalTag.globaltag = str(metaConditions['globalTags']['MC'])

from flashgg.Systematics.SystematicsCustomize import *

from flashgg.MetaData.JobConfig import customize
customize.metaConditions = metaConditions
customize.processId = processId
customize.doSystematics = doSystematics
customize.doGranularJEC = False


jetSystematicsInputTags = createStandardSystematicsProducers(process , customize)
modifyTagSequenceForSystematics(process,jetSystematicsInputTags)

# needed for 0th vertex from microAOD
process.load("flashgg/MicroAOD/flashggDiPhotons_cfi")
process.flashggDiPhotons.whichVertex = cms.uint32(0)
process.flashggDiPhotons.useZerothVertexFromMicro = cms.bool(True)

applyL1Prefiring = customizeForL1Prefiring(process, customize.metaConditions, customize.processId)

# Remove unneeded tags
process.flashggTagSequence.remove(process.flashggTHQLeptonicTag)
process.flashggTagSequence.remove(process.flashggTTHDiLeptonTag)
process.flashggTagSequence.remove(process.flashggVBFTag)
process.flashggTagSequence.remove(process.flashggVHMetTag)
process.flashggTagSequence.remove(process.flashggWHLeptonicTag)
process.flashggTagSequence.remove(process.flashggZHLeptonicTag)
process.flashggTagSequence.remove(process.flashggVHLeptonicLooseTag)
process.flashggTagSequence.remove(process.flashggVHHadronicTag)
process.flashggTagSequence.remove(process.flashggUntagged)
process.flashggTagSequence.remove(process.flashggVBFMVA)
process.flashggTagSequence.remove(process.flashggVBFDiPhoDiJetMVA)

process.flashggTagSequence.remove(process.flashggTTHHadronicTag)
process.flashggTagSequence.remove(process.flashggTTHLeptonicTag)


process.flashggTagSorter.TagPriorityRanges = cms.VPSet(   
        cms.PSet(TagName = cms.InputTag('flashggTTHLeptonicTag')),
        cms.PSet(TagName = cms.InputTag('flashggTTHHadronicTag')) )

newvpset = cms.VPSet()
for pset in process.flashggDiPhotonSystematics.SystMethods:
    if not pset.Label.value().count("FracRVNvtxWeight") :
	print  pset.Label.value()
	newvpset += [pset]

#from flashgg.Systematics.flashggDiPhotonSystematics_cfi import PixelSeedWeight
#newvpset += [ PixelSeedWeight ]

process.flashggDiPhotonSystematics.SystMethods = newvpset

# Or use the official tool instead
useEGMTools(process)

systlabels = [""]
phosystlabels = []
metsystlabels = []
jetsystlabels = []
elesystlabels = []
musystlabels = []



if not ISDATA:
    if ISSIGNAL:
        variablesToUse = minimalVariables
    else:
        variablesToUse = minimalNonSignalVariables
    if doSystematics:
        for direction in ["Up","Down"]:
            phosystlabels.append("MvaShift%s01sigma" % direction)
            #phosystlabels.append("SigmaEOverEShift%s01sigma" % direction)
            #phosystlabels.append("MaterialCentralBarrel%s01sigma" % direction)
            #phosystlabels.append("MaterialOuterBarrel%s01sigma" % direction)
            #phosystlabels.append("MaterialForward%s01sigma" % direction)
            #phosystlabels.append("FNUFEB%s01sigma" % direction)
            #phosystlabels.append("FNUFEE%s01sigma" % direction)
            #phosystlabels.append("MCScaleGain6EB%s01sigma" % direction)
            #phosystlabels.append("MCScaleGain1EB%s01sigma" % direction)
            jetsystlabels.append("JEC%s01sigma" % direction)
            jetsystlabels.append("JER%s01sigma" % direction)
            #jetsystlabels.append("PUJIDShift%s01sigma" % direction)
            #metsystlabels.append("metJecUncertainty%s01sigma" % direction)
            #metsystlabels.append("metJerUncertainty%s01sigma" % direction)
            #metsystlabels.append("metPhoUncertainty%s01sigma" % direction)
            #metsystlabels.append("metUncUncertainty%s01sigma" % direction)
            #variablesToUse.append("UnmatchedPUWeight%s01sigma[1,-999999.,999999.] := weight(\"UnmatchedPUWeight%s01sigma\")" % (direction,direction))
            #variablesToUse.append("MvaLinearSyst%s01sigma[1,-999999.,999999.] := weight(\"MvaLinearSyst%s01sigma\")" % (direction,direction))
            variablesToUse.append("PixelSeedWeight%s01sigma[1,-999999.,999999.] := getObjectWeight(\"PixelSeedWeight%s01sigma\")" % (direction,direction))
            variablesToUse.append("LooseMvaSF%s01sigma[1,-999999.,999999.] := weight(\"LooseMvaSF%s01sigma\")" % (direction,direction))
            variablesToUse.append("PreselSF%s01sigma[1,-999999.,999999.] := weight(\"PreselSF%s01sigma\")" % (direction,direction))
            variablesToUse.append("electronVetoSF%s01sigma[1,-999999.,999999.] := weight(\"electronVetoSF%s01sigma\")" % (direction,direction))
            variablesToUse.append("TriggerWeight%s01sigma[1,-999999.,999999.] := weight(\"TriggerWeight%s01sigma\")" % (direction,direction))
            #variablesToUse.append("FracRVWeight%s01sigma[1,-999999.,999999.] := weight(\"FracRVWeight%s01sigma\")" % (direction,direction))
            #variablesToUse.append("FracRVNvtxWeight%s01sigma[1,-999999.,999999.] := weight(\"FracRVNvtxWeight%s01sigma\")" % (direction,direction))
            variablesToUse.append("ElectronWeight%s01sigma[1,-999999.,999999.] := getObjectWeight(\"ElectronWeight%s01sigma\")" % (direction,direction))
            variablesToUse.append("JetBTagCutWeight%s01sigma[1,-999999.,999999.] := getObjectWeight(\"JetBTagCutWeight%s01sigma\")" % (direction,direction))
            variablesToUse.append("JetBTagReshapeWeight%s01sigma[1,-999999.,999999.] := getObjectWeight(\"JetBTagReshapeWeight%s01sigma\")" % (direction,direction))
            #variablesToUse.append("JetCTagReshapeWeight%s01sigma[1,-999999.,999999.] := getObjectWeight(\"JetCTagReshapeWeight%s01sigma\")" % (direction,direction))
            if applyL1Prefiring:
                variablesToUse.append("prefireProbability := weight(\"prefireProbability\")")
            variablesToUse.append("weight_JetBTagWeight:=getObjectWeight(\"JetBTagReshapeWeightCentral\")")
            #variablesToUse.append("weight_JetCTagWeight:=getObjectWeight(\"JetCTagReshapeWeightCentral\")")
            for r9 in ["HighR9","LowR9"]:
                for region in ["EB","EE"]:
                    phosystlabels.append("ShowerShape%s%s%s01sigma"%(r9,region,direction))
    #                    phosystlabels.append("MCSmear%s%s%s01sigma" % (r9,region,direction))
                    phosystlabels.append("MCScale%s%s%s01sigma" % (r9,region,direction))
                    for var in ["Rho","Phi"]:
                        phosystlabels.append("MCSmear%s%s%s%s01sigma" % (r9,region,var,direction))
        systlabels += phosystlabels
        systlabels += jetsystlabels
        systlabels += metsystlabels


if ISSIGNAL:
    print "Signal MC" # "so adding systematics and dZ"
    customizeSystematicsForSignal(process)
elif ISDATA:
    print "Data" # "so turn off all shifts and systematics, with some exceptions"
    variablesToUse = minimalNonSignalVariables
    customizeSystematicsForData(process)
else:
    print "Background MC" # "so store mgg and central only"
    customizeSystematicsForSignal(process)
    #customizeSystematicsForBackground(process)

printSystematicInfo(process)

cloneTagSequenceForEachSystematic(process,systlabels,phosystlabels,metsystlabels,jetsystlabels,jetSystematicsInputTags)

# Require standard diphoton trigger
# Triggers are already required in microAOD production, don't need to require again
#from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
#hlt_paths = []
#for dset in customize.metaConditions["TriggerPaths"]:
#    if dset[2:-2] in file_names[0]: 
#        print customize.metaConditions["TriggerPaths"][dset]
#        hlt_paths.extend(customize.metaConditions["TriggerPaths"][dset])

#hlt_paths = [path.encode("ascii") for path in hlt_paths]
#process.hltHighLevel= hltHighLevel.clone(HLTPaths = cms.vstring(hlt_paths))

process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

#process.dataRequirements = cms.Sequence()
#if customize.processId == "Data":
#        process.dataRequirements += process.hltHighLevel


process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

process.genFilter = cms.Sequence()
# Split WH and ZH
process.genFilter = cms.Sequence()
if ((customize.processId.count("wh") or customize.processId.count("zh")) and not (customize.processId.count("powheg"))) and not customize.processId.count("wzh") :
    print "enabling vh filter!!!!!"
    process.load("flashgg/Systematics/VHFilter_cfi")
    process.genFilter += process.VHFilter
    process.VHFilter.chooseW = bool(customize.processId.count("wh"))
    process.VHFilter.chooseZ = bool(customize.processId.count("zh"))

if (customize.processId == "th_125" or customize.processId == "bbh_125"):
    process.load("flashgg/Systematics/CentralHiggsFilter_cfi")
    process.genFilter += process.CentralHiggsFilter

#pythia8 has an unanticipated EM showering feature, check have two photons from hard scatter
process.penultimateFilter= cms.Sequence()
if customize.processId == "th_125": # for this sample the filter removes also H -> ZG
    process.load("flashgg/Systematics/HardProcessFinalStateFilter_cfi")
#    process.HardProcessFinalStateFilter.debug = True
    process.penultimateFilter += process.HardProcessFinalStateFilter


# Met Filters
process.load('flashgg/Systematics/flashggMetFilters_cfi')
if ISDATA:
    metFilterSelector = "data" 
else:
    metFilterSelector = "mc"
process.flashggMetFilters.requiredFilterNames = cms.untracked.vstring([filter.encode("ascii") for filter in metaConditions["flashggMetFilters"][metFilterSelector]])
print "Required MET filters: ", process.flashggMetFilters.requiredFilterNames


process.load("flashgg/Taggers/flashggTagSequence_cfi")
process.load("flashgg/Taggers/flashggTagTester_cfi")
process.load("flashgg.Taggers.diphotonTagDumper_cfi") ##  import diphotonTagDumper 


process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("merged_ntuple.root"))

dipho_variables=["dipho_sumpt      := diPhoton.sumPt",
                 "dipho_cosphi     := abs(cos(diPhoton.leadingPhoton.phi - diPhoton.subLeadingPhoton.phi))",
                 "mass             := diPhoton.mass",
                 "leadPt           := diPhoton.leadingPhoton.pt",
                 "leadEt           := diPhoton.leadingPhoton.et",
                 "leadEnergy       := diPhoton.leadingPhoton.energy",
                 "leadEta          := diPhoton.leadingPhoton.eta",
                 "leadPhi          := diPhoton.leadingPhoton.phi",
                 "lead_sieie       := diPhoton.leadingPhoton.sigmaIetaIeta",
                 "lead_hoe         := diPhoton.leadingPhoton.hadronicOverEm",
                 "lead_sigmaEoE    := diPhoton.leadingPhoton.sigEOverE",
                 "lead_ptoM        := diPhoton.leadingPhoton.pt/diPhoton.mass",
                 "leadR9           := diPhoton.leadingPhoton.full5x5_r9",
                 "leadGenMatch     := diPhoton.leadingPhoton.genMatchType",
                 "leadPtGen        := ? diPhoton.leadingPhoton.hasMatchedGenPhoton ? diPhoton.leadingPhoton.matchedGenPhoton.pt : 0",
                 "leadGendeltaR    := ? diPhoton.leadingPhoton.hasMatchedGenPhoton ? sqrt( pow((diPhoton.leadingPhoton.phi -  diPhoton.leadingPhoton.matchedGenPhoton.phi), 2) + pow((diPhoton.leadingPhoton.phi -  diPhoton.leadingPhoton.matchedGenPhoton.phi), 2)) : -999",
                 "subleadPt        := diPhoton.subLeadingPhoton.pt",
                 "subleadEt        := diPhoton.subLeadingPhoton.et",
                 "subleadEnergy    := diPhoton.subLeadingPhoton.energy",
                 "subleadEta       := diPhoton.subLeadingPhoton.eta",
                 "subleadPhi       := diPhoton.subLeadingPhoton.phi",
                 "sublead_sieie    := diPhoton.subLeadingPhoton.sigmaIetaIeta",
                 "sublead_hoe      := diPhoton.subLeadingPhoton.hadronicOverEm",
                 "sublead_sigmaEoE := diPhoton.subLeadingPhoton.sigEOverE",
                 "sublead_ptoM     := diPhoton.subLeadingPhoton.pt/diPhoton.mass",
                 "subleadR9        := diPhoton.subLeadingPhoton.full5x5_r9",
                 "subleadGenMatch  := diPhoton.subLeadingPhoton.genMatchType",
                 "subleadPtGen     := ? diPhoton.subLeadingPhoton.hasMatchedGenPhoton ? diPhoton.subLeadingPhoton.matchedGenPhoton.pt : 0",
                 "subleadGendeltaR := ? diPhoton.subLeadingPhoton.hasMatchedGenPhoton ? sqrt( pow((diPhoton.subLeadingPhoton.phi -  diPhoton.subLeadingPhoton.matchedGenPhoton.phi), 2) + pow((diPhoton.subLeadingPhoton.phi -  diPhoton.subLeadingPhoton.matchedGenPhoton.phi), 2)) : -999",
                 "leadIDMVA        := diPhoton.leadingView.phoIdMvaWrtChosenVtx",
                 "subleadIDMVA     := diPhoton.subLeadingView.phoIdMvaWrtChosenVtx",
                 "dipho_rapidity   := diPhoton.rapidity",
                 "vertex_idx       := diPhoton.vertexIndex",
                 "nGoodEls         := nGoodEls",
                 "nGoodElsFromTau  := nGoodElsFromTau",
                 "nGoodMus         := nGoodMus",
                 "nGoodMusFromTau  := nGoodMusFromTau",
                 "nGoodTaus        := nGoodTaus",
                 "diphoMVARes      := diphoMVARes",
                 "leadPassEVeto    := diPhoton.leadingPhoton.passElectronVeto",
                 "subleadPassEVeto := diPhoton.subLeadingPhoton.passElectronVeto",
                 "leadPixelSeed    := diPhoton.leadingPhoton.hasPixelSeed",
                 "subleadPixelSeed := diPhoton.subLeadingPhoton.hasPixelSeed",
                 "nb_loose         := nBLoose",
                 "nb_medium        := nBMedium",
                 "nb_tight         := nBTight",
                 "rand             := rand",
                 "lead_photon_type := leadPhotonType",
                 "sublead_photon_type := subleadPhotonType",
                 "lead_closest_gen_Pt := leadPhotonClosestPt",
                 "sublead_closest_gen_Pt := subleadPhotonClosestPt",
                 "lead_closest_gen_dR := leadPhotonClosestDeltaR",
                 "sublead_closest_gen_dR := subleadPhotonClosestDeltaR",
                 "lead_PhoGenPt := leadPhoGenPt",
                 "lead_PhoGenEta := leadPhoGenEta",
                 "lead_PhoGenPhi := leadPhoGenPhi",
                 "lead_Prompt := leadPrompt",
                 "lead_Mad := leadMad",
                 "lead_Pythia := leadPythia",
                 "lead_SimpleMomID := leadSimpleMomID",
                 "lead_SimpleMomStatus := leadSimpleMomStatus",
                 "lead_MomID := leadMomID",
                 "lead_MomMomID := leadMomMomID",
                 "lead_PassFrix := leadPassFrix",
                 "lead_SmallestDr := leadSmallestDr",
                 "sublead_PhoGenPt := subleadPhoGenPt",
                 "sublead_PhoGenEta := subleadPhoGenEta",
                 "sublead_PhoGenPhi := subleadPhoGenPhi",
                 "sublead_Prompt := subleadPrompt",
                 "sublead_Mad := subleadMad",
                 "sublead_Pythia := subleadPythia",
                 "sublead_SimpleMomID := subleadSimpleMomID",
                 "sublead_SimpleMomStatus := subleadSimpleMomStatus",
                 "sublead_MomID := subleadMomID",
                 "sublead_MomMomID := subleadMomMomID",
                 "sublead_PassFrix := subleadPassFrix",
                 "sublead_SmallestDr := subleadSmallestDr",
                 "MetPt  := MetPt",
                 "MetPhi := MetPhi",
                 "topTag_score := topTagScore",
                 "topTag_topMass := topTagTopMass",
                 "topTag_WMass := topTagWMass",
                 "dnn_score_ttgg  := dnn_score_ttH_vs_ttgg",
                 "dnn_score_fcnc_tt := dnn_score_fcnc_tt",
                 "dnn_score_fcnc_st := dnn_score_fcnc_st",
                 "fcnc_bdt_nrb_hut_score := fcnc_bdt_nrb_hut_score",
                 "fcnc_bdt_nrb_hct_score := fcnc_bdt_nrb_hct_score",
                 "fcnc_bdt_smh_hut_score := fcnc_bdt_smh_hut_score",
                 "fcnc_bdt_smh_hct_score := fcnc_bdt_smh_hct_score",
]

leptonic_variables = [  "n_ele    := electrons.size",
                        "ele1_pt  := ?(electrons.size>0)? electrons.at(0).pt : -1",
                        "ele2_pt  := ?(electrons.size>1)? electrons.at(1).pt : -1",
                        "ele1_eta  := ?(electrons.size>0)? electrons.at(0).eta : -999",
                        "ele2_eta  := ?(electrons.size>1)? electrons.at(1).eta : -999",
                        "ele1_phi  := ?(electrons.size>0)? electrons.at(0).phi : -999",
                        "ele2_phi  := ?(electrons.size>1)? electrons.at(1).phi : -999",
                        "ele1_energy  := ?(electrons.size>0)? electrons.at(0).energy : -999",
                        "ele2_energy  := ?(electrons.size>1)? electrons.at(1).energy : -999",
                        "ele1_charge  := ?(electrons.size>0)? electrons.at(0).charge : -999",
                        "ele2_charge  := ?(electrons.size>1)? electrons.at(1).charge : -999",
                        "n_muons  := muons.size",
                        "muon1_pt := ?(muons.size>0)? muons.at(0).pt : -1",
                        "muon2_pt := ?(muons.size>1)? muons.at(1).pt : -1",
                        "muon1_eta := ?(muons.size>0)? muons.at(0).eta : -999",
                        "muon2_eta := ?(muons.size>1)? muons.at(1).eta : -999",
                        "muon1_phi := ?(muons.size>0)? muons.at(0).phi : -999",
                        "muon2_phi := ?(muons.size>1)? muons.at(1).phi : -999",
                        "muon1_energy := ?(muons.size>0)? muons.at(0).energy : -999",
                        "muon2_energy := ?(muons.size>1)? muons.at(1).energy : -999",
                        "muon1_charge := ?(muons.size>0)? muons.at(0).charge : -999",
                        "muon2_charge := ?(muons.size>1)? muons.at(1).charge : -999",
                        "muonLeadIso := muonLeadIso",
                        "muonSubleadIso := muonSubleadIso",
                        "nMuonLoose :=  nMuonLoose",
                        "nMuonMedium :=  nMuonMedium",
                        "nMuonTight :=  nMuonTight",
                        "nElecLoose :=  nElecLoose",
                        "nElecMedium :=  nElecMedium",
                        "nElecTight :=  nElecTight",
                        "n_bjets  := bJets.size",
                        "n_jets   := jets.size",
                        "Mjj      := ?(jets.size>1)?"
                        +"sqrt((jets.at(0).energy+jets.at(1).energy)^2-(jets.at(0).px+jets.at(1).px)^2-(jets.at(0).py+jets.at(1).py)^2-(jets.at(0).pz+jets.at(1).pz)^2)"
                        +": -1",
                        "mT     := MT",
                        "tthMVA := mvaRes",
                        "tthMVA_RunII := mva_RunII_Res",
                        "jet_pt1                :=  ? jets.size()>0 ? jets[0].pt() : -100 ",
                        "jet_eta1               :=  ? jets.size()>0 ? jets[0].eta() : -100 ",
                        "jet_phi1               :=  ? jets.size()>0 ? jets[0].phi() : -100 ",
                        "jet_bdiscriminant1     :=  ? jets.size()>0 ? jets[0].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100",
                        "jet_pt2                :=  ? jets.size()>1 ? jets[1].pt() : -100 ",
                        "jet_eta2               :=  ? jets.size()>1 ? jets[1].eta() : -100 ",
                        "jet_phi2               :=  ? jets.size()>1 ? jets[1].phi() : -100 ",
                        "jet_bdiscriminant2     :=  ? jets.size()>1 ? jets[1].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100",
                        "jet_pt3                :=  ? jets.size()>2 ? jets[2].pt() : -100 ",
                        "jet_eta3               :=  ? jets.size()>2 ? jets[2].eta() : -100 ",
                        "jet_phi3               :=  ? jets.size()>2 ? jets[2].phi() : -100 ",
                        "jet_bdiscriminant3     :=  ? jets.size()>2 ? jets[2].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt4                :=  ? jets.size()>3 ? jets[3].pt() : -100 ",
                        "jet_eta4               :=  ? jets.size()>3 ? jets[3].eta() : -100 ",
                        "jet_phi4               :=  ? jets.size()>3 ? jets[3].phi() : -100 ",
                        "jet_bdiscriminant4     :=  ? jets.size()>3 ? jets[3].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt5                :=  ? jets.size()>4 ? jets[4].pt() : -100 ",
                        "jet_eta5               :=  ? jets.size()>4 ? jets[4].eta() : -100 ",
                        "jet_phi5               :=  ? jets.size()>4 ? jets[4].phi() : -100 ",
                        "jet_bdiscriminant5     :=  ? jets.size()>4 ? jets[4].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt6                :=  ? jets.size()>5 ? jets[5].pt() : -100 ",
                        "jet_eta6               :=  ? jets.size()>5 ? jets[5].eta() : -100 ",
                        "jet_phi6               :=  ? jets.size()>5 ? jets[5].phi() : -100 ",
                        "jet_bdiscriminant6     :=  ? jets.size()>5 ? jets[5].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt7                :=  ? jets.size()>6 ? jets[6].pt() : -100 ",
                        "jet_eta7               :=  ? jets.size()>6 ? jets[6].eta() : -100 ",
                        "jet_phi7               :=  ? jets.size()>6 ? jets[6].phi() : -100 ",
                        "jet_bdiscriminant7     :=  ? jets.size()>6 ? jets[6].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt8                :=  ? jets.size()>7 ? jets[7].pt() : -100 ",
                        "jet_eta8               :=  ? jets.size()>7 ? jets[7].eta() : -100 ",
                        "jet_phi8               :=  ? jets.size()>7 ? jets[7].phi() : -100 ",
                        "jet_bdiscriminant8     :=  ? jets.size()>7 ? jets[7].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt9                :=  ? jets.size()>8 ? jets[8].pt() : -100 ",
                        "jet_eta9               :=  ? jets.size()>8 ? jets[8].eta() : -100 ",
                        "jet_phi9               :=  ? jets.size()>8 ? jets[8].phi() : -100 ",
                        "jet_bdiscriminant9     :=  ? jets.size()>8 ? jets[8].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt10                :=  ? jets.size()>9 ? jets[9].pt() : -100 ",
                        "jet_eta10               :=  ? jets.size()>9 ? jets[9].eta() : -100 ",
                        "jet_phi10               :=  ? jets.size()>9 ? jets[9].phi() : -100 ",
                        "jet_bdiscriminant10     :=  ? jets.size()>9 ? jets[9].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt11                :=  ? jets.size()>10 ? jets[10].pt() : -100 ",
                        "jet_eta11               :=  ? jets.size()>10 ? jets[10].eta() : -100 ",
                        "jet_phi11               :=  ? jets.size()>10 ? jets[10].phi() : -100 ",
                        "jet_bdiscriminant11     :=  ? jets.size()>10 ? jets[10].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt12                :=  ? jets.size()>11 ? jets[11].pt() : -100 ",
                        "jet_eta12               :=  ? jets.size()>11 ? jets[11].eta() : -100 ",
                        "jet_phi12               :=  ? jets.size()>11 ? jets[11].phi() : -100 ",
                        "jet_bdiscriminant12     :=  ? jets.size()>11 ? jets[11].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt13                :=  ? jets.size()>12 ? jets[12].pt() : -100 ",
                        "jet_eta13               :=  ? jets.size()>12 ? jets[12].eta() : -100 ",
                        "jet_phi13               :=  ? jets.size()>12 ? jets[12].phi() : -100 ",
                        "jet_bdiscriminant13     :=  ? jets.size()>12 ? jets[12].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt14                :=  ? jets.size()>13 ? jets[13].pt() : -100 ",
                        "jet_eta14               :=  ? jets.size()>13 ? jets[13].eta() : -100 ",
                        "jet_phi14               :=  ? jets.size()>13 ? jets[13].phi() : -100 ",
                        "jet_bdiscriminant14     :=  ? jets.size()>13 ? jets[13].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_pt15                :=  ? jets.size()>14 ? jets[14].pt() : -100 ",
                        "jet_eta15               :=  ? jets.size()>14 ? jets[14].eta() : -100 ",
                        "jet_phi15               :=  ? jets.size()>14 ? jets[14].phi() : -100 ",
                        "jet_bdiscriminant15     :=  ? jets.size()>14 ? jets[14].bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -100 ",
                        "jet_bbdiscriminant1  := ?(jets.size>0)? jets.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant2  := ?(jets.size>1)? jets.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant3  := ?(jets.size>2)? jets.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant4  := ?(jets.size>3)? jets.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant5  := ?(jets.size>4)? jets.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant6  := ?(jets.size>5)? jets.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant7  := ?(jets.size>6)? jets.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant8  := ?(jets.size>7)? jets.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant9  := ?(jets.size>8)? jets.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant10  := ?(jets.size>9)? jets.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant11  := ?(jets.size>10)? jets.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant12  := ?(jets.size>11)? jets.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant13  := ?(jets.size>12)? jets.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant14  := ?(jets.size>13)? jets.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_bbdiscriminant15  := ?(jets.size>14)? jets.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet_cdiscriminant1  := ?(jets.size>0)? jets.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant2  := ?(jets.size>1)? jets.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant3  := ?(jets.size>2)? jets.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant4  := ?(jets.size>3)? jets.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant5  := ?(jets.size>4)? jets.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant6  := ?(jets.size>5)? jets.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant7  := ?(jets.size>6)? jets.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant8  := ?(jets.size>7)? jets.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant9  := ?(jets.size>8)? jets.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant10  := ?(jets.size>9)? jets.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant11  := ?(jets.size>10)? jets.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant12  := ?(jets.size>11)? jets.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant13  := ?(jets.size>12)? jets.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant14  := ?(jets.size>13)? jets.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_cdiscriminant15  := ?(jets.size>14)? jets.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet_udsgdiscriminant1  := ?(jets.size>0)? jets.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant2  := ?(jets.size>1)? jets.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant3  := ?(jets.size>2)? jets.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant4  := ?(jets.size>3)? jets.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant5  := ?(jets.size>4)? jets.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant6  := ?(jets.size>5)? jets.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant7  := ?(jets.size>6)? jets.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant8  := ?(jets.size>7)? jets.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant9  := ?(jets.size>8)? jets.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant10  := ?(jets.size>9)? jets.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant11  := ?(jets.size>10)? jets.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant12  := ?(jets.size>11)? jets.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant13  := ?(jets.size>12)? jets.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant14  := ?(jets.size>13)? jets.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_udsgdiscriminant15  := ?(jets.size>14)? jets.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet_energy1  := ?(jets.size>0)? jets.at(0).energy : -1",
                        "jet_energy2  := ?(jets.size>1)? jets.at(1).energy : -1",
                        "jet_energy3  := ?(jets.size>2)? jets.at(2).energy : -1",
                        "jet_energy4  := ?(jets.size>3)? jets.at(3).energy : -1",
                        "jet_energy5  := ?(jets.size>4)? jets.at(4).energy : -1",
                        "jet_energy6  := ?(jets.size>5)? jets.at(5).energy : -1",
                        "jet_energy7  := ?(jets.size>6)? jets.at(6).energy : -1",
                        "jet_energy8  := ?(jets.size>7)? jets.at(7).energy : -1",
                        "jet_energy9  := ?(jets.size>8)? jets.at(8).energy : -1",
                        "jet_energy10  := ?(jets.size>9)? jets.at(9).energy : -1",
                        "jet_energy11  := ?(jets.size>10)? jets.at(10).energy : -1",
                        "jet_energy12  := ?(jets.size>11)? jets.at(11).energy : -1",
                        "jet_energy13  := ?(jets.size>12)? jets.at(12).energy : -1",
                        "jet_energy14  := ?(jets.size>13)? jets.at(13).energy : -1",
                        "jet_energy15  := ?(jets.size>14)? jets.at(14).energy : -1",
                        "jet_hadronFlavour1  := ?(jets.size>0)? jets.at(0).hadronFlavour : -1",
                        "jet_hadronFlavour2  := ?(jets.size>1)? jets.at(1).hadronFlavour : -1",
                        "jet_hadronFlavour3  := ?(jets.size>2)? jets.at(2).hadronFlavour : -1",
                        "jet_hadronFlavour4  := ?(jets.size>3)? jets.at(3).hadronFlavour : -1",
                        "jet_hadronFlavour5  := ?(jets.size>4)? jets.at(4).hadronFlavour : -1",
                        "jet_hadronFlavour6  := ?(jets.size>5)? jets.at(5).hadronFlavour : -1",
                        "jet_hadronFlavour7  := ?(jets.size>6)? jets.at(6).hadronFlavour : -1",
                        "jet_hadronFlavour8  := ?(jets.size>7)? jets.at(7).hadronFlavour : -1",
                        "jet_hadronFlavour9  := ?(jets.size>8)? jets.at(8).hadronFlavour : -1",
                        "jet_hadronFlavour10  := ?(jets.size>9)? jets.at(9).hadronFlavour : -1",
                        "jet_hadronFlavour11  := ?(jets.size>10)? jets.at(10).hadronFlavour : -1",
                        "jet_hadronFlavour12  := ?(jets.size>11)? jets.at(11).hadronFlavour : -1",
                        "jet_hadronFlavour13  := ?(jets.size>12)? jets.at(12).hadronFlavour : -1",
                        "jet_hadronFlavour14  := ?(jets.size>13)? jets.at(13).hadronFlavour : -1",
                        "jet_hadronFlavour15  := ?(jets.size>14)? jets.at(14).hadronFlavour : -1", 
]

hadronic_variables = [  "n_bjets  := nBMedium",
                        "n_jets   := jetVector.size",
                        "bjet1_pt := ?nBMedium>1? bJetVector.at(0).pt : -1",
                        "bjet2_pt := ?nBMedium>1? bJetVector.at(1).pt : -1",
                        "jet1_pt  := ?(jetVector.size>0)? jetVector.at(0).pt : -1",
                        "jet2_pt  := ?(jetVector.size>1)? jetVector.at(1).pt : -1",
                        "jet3_pt  := ?(jetVector.size>2)? jetVector.at(2).pt : -1",
                        "jet4_pt  := ?(jetVector.size>3)? jetVector.at(3).pt : -1",
                        "jet5_pt  := ?(jetVector.size>4)? jetVector.at(4).pt : -1",
                        "jet6_pt  := ?(jetVector.size>5)? jetVector.at(5).pt : -1",
                        "jet7_pt  := ?(jetVector.size>6)? jetVector.at(6).pt : -1",
                        "jet8_pt  := ?(jetVector.size>7)? jetVector.at(7).pt : -1",
                        "jet9_pt  := ?(jetVector.size>8)? jetVector.at(8).pt : -1",
                        "jet10_pt  := ?(jetVector.size>9)? jetVector.at(9).pt : -1",
                        "jet11_pt  := ?(jetVector.size>10)? jetVector.at(10).pt : -1",
                        "jet12_pt  := ?(jetVector.size>11)? jetVector.at(11).pt : -1",
                        "jet13_pt  := ?(jetVector.size>12)? jetVector.at(12).pt : -1",
                        "jet14_pt  := ?(jetVector.size>13)? jetVector.at(13).pt : -1",
                        "jet15_pt  := ?(jetVector.size>14)? jetVector.at(14).pt : -1",
                        "jet1_eta  := ?(jetVector.size>0)? jetVector.at(0).eta : -1",
                        "jet2_eta  := ?(jetVector.size>1)? jetVector.at(1).eta : -1",
                        "jet3_eta  := ?(jetVector.size>2)? jetVector.at(2).eta : -1",
                        "jet4_eta  := ?(jetVector.size>3)? jetVector.at(3).eta : -1",
                        "jet5_eta  := ?(jetVector.size>4)? jetVector.at(4).eta : -1",
                        "jet6_eta  := ?(jetVector.size>5)? jetVector.at(5).eta : -1",
                        "jet7_eta  := ?(jetVector.size>6)? jetVector.at(6).eta : -1",
                        "jet8_eta  := ?(jetVector.size>7)? jetVector.at(7).eta : -1",
                        "jet9_eta  := ?(jetVector.size>8)? jetVector.at(8).eta : -1",
                        "jet10_eta  := ?(jetVector.size>9)? jetVector.at(9).eta : -1",
                        "jet11_eta  := ?(jetVector.size>10)? jetVector.at(10).eta : -1",
                        "jet12_eta  := ?(jetVector.size>11)? jetVector.at(11).eta : -1",
                        "jet13_eta  := ?(jetVector.size>12)? jetVector.at(12).eta : -1",
                        "jet14_eta  := ?(jetVector.size>13)? jetVector.at(13).eta : -1",
                        "jet15_eta  := ?(jetVector.size>14)? jetVector.at(14).eta : -1",
                        "jet1_phi  := ?(jetVector.size>0)? jetVector.at(0).phi : -1",
                        "jet2_phi  := ?(jetVector.size>1)? jetVector.at(1).phi : -1",
                        "jet3_phi  := ?(jetVector.size>2)? jetVector.at(2).phi : -1",
                        "jet4_phi  := ?(jetVector.size>3)? jetVector.at(3).phi : -1",
                        "jet5_phi  := ?(jetVector.size>4)? jetVector.at(4).phi : -1",
                        "jet6_phi  := ?(jetVector.size>5)? jetVector.at(5).phi : -1",
                        "jet7_phi  := ?(jetVector.size>6)? jetVector.at(6).phi : -1",
                        "jet8_phi  := ?(jetVector.size>7)? jetVector.at(7).phi : -1",
                        "jet9_phi  := ?(jetVector.size>8)? jetVector.at(8).phi : -1",
                        "jet10_phi  := ?(jetVector.size>9)? jetVector.at(9).phi : -1",
                        "jet11_phi  := ?(jetVector.size>10)? jetVector.at(10).phi : -1",
                        "jet12_phi  := ?(jetVector.size>11)? jetVector.at(11).phi : -1",
                        "jet13_phi  := ?(jetVector.size>12)? jetVector.at(12).phi : -1",
                        "jet14_phi  := ?(jetVector.size>13)? jetVector.at(13).phi : -1",
                        "jet15_phi  := ?(jetVector.size>14)? jetVector.at(14).phi : -1",
                        "jet1_bdiscriminant  := ?(jetVector.size>0)? jetVector.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet2_bdiscriminant  := ?(jetVector.size>1)? jetVector.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet3_bdiscriminant  := ?(jetVector.size>2)? jetVector.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet4_bdiscriminant  := ?(jetVector.size>3)? jetVector.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet5_bdiscriminant  := ?(jetVector.size>4)? jetVector.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet6_bdiscriminant  := ?(jetVector.size>5)? jetVector.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet7_bdiscriminant  := ?(jetVector.size>6)? jetVector.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet8_bdiscriminant  := ?(jetVector.size>7)? jetVector.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet9_bdiscriminant  := ?(jetVector.size>8)? jetVector.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet10_bdiscriminant  := ?(jetVector.size>9)? jetVector.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet11_bdiscriminant  := ?(jetVector.size>10)? jetVector.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet12_bdiscriminant  := ?(jetVector.size>11)? jetVector.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet13_bdiscriminant  := ?(jetVector.size>12)? jetVector.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet14_bdiscriminant  := ?(jetVector.size>13)? jetVector.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet15_bdiscriminant  := ?(jetVector.size>14)? jetVector.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probb') : -1",
                        "jet1_bbdiscriminant  := ?(jetVector.size>0)? jetVector.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet2_bbdiscriminant  := ?(jetVector.size>1)? jetVector.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet3_bbdiscriminant  := ?(jetVector.size>2)? jetVector.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet4_bbdiscriminant  := ?(jetVector.size>3)? jetVector.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet5_bbdiscriminant  := ?(jetVector.size>4)? jetVector.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet6_bbdiscriminant  := ?(jetVector.size>5)? jetVector.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet7_bbdiscriminant  := ?(jetVector.size>6)? jetVector.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet8_bbdiscriminant  := ?(jetVector.size>7)? jetVector.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet9_bbdiscriminant  := ?(jetVector.size>8)? jetVector.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet10_bbdiscriminant  := ?(jetVector.size>9)? jetVector.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet11_bbdiscriminant  := ?(jetVector.size>10)? jetVector.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",                        "jet12_bbdiscriminant  := ?(jetVector.size>11)? jetVector.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet13_bbdiscriminant  := ?(jetVector.size>12)? jetVector.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",                        "jet14_bbdiscriminant  := ?(jetVector.size>13)? jetVector.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet15_bbdiscriminant  := ?(jetVector.size>14)? jetVector.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probbb') : -1",
                        "jet1_cdiscriminant  := ?(jetVector.size>0)? jetVector.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet2_cdiscriminant  := ?(jetVector.size>1)? jetVector.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet3_cdiscriminant  := ?(jetVector.size>2)? jetVector.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet4_cdiscriminant  := ?(jetVector.size>3)? jetVector.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet5_cdiscriminant  := ?(jetVector.size>4)? jetVector.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet6_cdiscriminant  := ?(jetVector.size>5)? jetVector.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet7_cdiscriminant  := ?(jetVector.size>6)? jetVector.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet8_cdiscriminant  := ?(jetVector.size>7)? jetVector.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet9_cdiscriminant  := ?(jetVector.size>8)? jetVector.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet10_cdiscriminant  := ?(jetVector.size>9)? jetVector.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet11_cdiscriminant  := ?(jetVector.size>10)? jetVector.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",                        "jet12_cdiscriminant  := ?(jetVector.size>11)? jetVector.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet13_cdiscriminant  := ?(jetVector.size>12)? jetVector.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",                        "jet14_cdiscriminant  := ?(jetVector.size>13)? jetVector.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet15_cdiscriminant  := ?(jetVector.size>14)? jetVector.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probc') : -1",
                        "jet1_udsgdiscriminant  := ?(jetVector.size>0)? jetVector.at(0).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet2_udsgdiscriminant  := ?(jetVector.size>1)? jetVector.at(1).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet3_udsgdiscriminant  := ?(jetVector.size>2)? jetVector.at(2).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet4_udsgdiscriminant  := ?(jetVector.size>3)? jetVector.at(3).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet5_udsgdiscriminant  := ?(jetVector.size>4)? jetVector.at(4).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet6_udsgdiscriminant  := ?(jetVector.size>5)? jetVector.at(5).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet7_udsgdiscriminant  := ?(jetVector.size>6)? jetVector.at(6).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet8_udsgdiscriminant  := ?(jetVector.size>7)? jetVector.at(7).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet9_udsgdiscriminant  := ?(jetVector.size>8)? jetVector.at(8).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet10_udsgdiscriminant  := ?(jetVector.size>9)? jetVector.at(9).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet11_udsgdiscriminant  := ?(jetVector.size>10)? jetVector.at(10).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet12_udsgdiscriminant  := ?(jetVector.size>11)? jetVector.at(11).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet13_udsgdiscriminant  := ?(jetVector.size>12)? jetVector.at(12).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet14_udsgdiscriminant  := ?(jetVector.size>13)? jetVector.at(13).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet15_udsgdiscriminant  := ?(jetVector.size>14)? jetVector.at(14).bDiscriminator('mini_pfDeepFlavourJetTags:probuds') : -1",
                        "jet1_energy  := ?(jetVector.size>0)? jetVector.at(0).energy : -1",
                        "jet2_energy  := ?(jetVector.size>1)? jetVector.at(1).energy : -1",
                        "jet3_energy  := ?(jetVector.size>2)? jetVector.at(2).energy : -1",
                        "jet4_energy  := ?(jetVector.size>3)? jetVector.at(3).energy : -1",
                        "jet5_energy  := ?(jetVector.size>4)? jetVector.at(4).energy : -1",
                        "jet6_energy  := ?(jetVector.size>5)? jetVector.at(5).energy : -1",
                        "jet7_energy  := ?(jetVector.size>6)? jetVector.at(6).energy : -1",
                        "jet8_energy  := ?(jetVector.size>7)? jetVector.at(7).energy : -1",
                        "jet9_energy  := ?(jetVector.size>8)? jetVector.at(8).energy : -1",
                        "jet10_energy  := ?(jetVector.size>9)? jetVector.at(9).energy : -1",
                        "jet11_energy  := ?(jetVector.size>10)? jetVector.at(10).energy : -1",
                        "jet12_energy  := ?(jetVector.size>11)? jetVector.at(11).energy : -1",
                        "jet13_energy  := ?(jetVector.size>12)? jetVector.at(12).energy : -1",
                        "jet14_energy  := ?(jetVector.size>13)? jetVector.at(13).energy : -1",
                        "jet15_energy  := ?(jetVector.size>14)? jetVector.at(14).energy : -1",
                        "jet1_hadronFlavour  := ?(jetVector.size>0)? jetVector.at(0).hadronFlavour : -1",
                        "jet2_hadronFlavour  := ?(jetVector.size>1)? jetVector.at(1).hadronFlavour : -1",
                        "jet3_hadronFlavour  := ?(jetVector.size>2)? jetVector.at(2).hadronFlavour : -1",
                        "jet4_hadronFlavour  := ?(jetVector.size>3)? jetVector.at(3).hadronFlavour : -1",
                        "jet5_hadronFlavour  := ?(jetVector.size>4)? jetVector.at(4).hadronFlavour : -1",
                        "jet6_hadronFlavour  := ?(jetVector.size>5)? jetVector.at(5).hadronFlavour : -1",
                        "jet7_hadronFlavour  := ?(jetVector.size>6)? jetVector.at(6).hadronFlavour : -1",
                        "jet8_hadronFlavour  := ?(jetVector.size>7)? jetVector.at(7).hadronFlavour : -1",
                        "jet9_hadronFlavour  := ?(jetVector.size>8)? jetVector.at(8).hadronFlavour : -1",
                        "jet10_hadronFlavour  := ?(jetVector.size>9)? jetVector.at(9).hadronFlavour : -1",
                        "jet11_hadronFlavour  := ?(jetVector.size>10)? jetVector.at(10).hadronFlavour : -1",
                        "jet12_hadronFlavour  := ?(jetVector.size>11)? jetVector.at(11).hadronFlavour : -1",
                        "jet13_hadronFlavour  := ?(jetVector.size>12)? jetVector.at(12).hadronFlavour : -1",
                        "jet14_hadronFlavour  := ?(jetVector.size>13)? jetVector.at(13).hadronFlavour : -1",
                        "jet15_hadronFlavour  := ?(jetVector.size>14)? jetVector.at(14).hadronFlavour : -1", 
                        "bjet1_csv:= maxBTagVal",
                        "bjet2_csv:= secondMaxBTagVal",
                        "tthMVA := tthMvaRes",
                        "tthMVA_RunII := tthMva_RunII_Res",
                        "dnn_score_dipho := dnn_score_ttH_vs_dipho",
]

## TAGS DUMPERS ##
from flashgg.Taggers.tagsDumpers_cfi import *

process.tagsDumper.className = "DiPhotonTagDumper"
process.tagsDumper.src = "flashggSystTagMerger"
process.tagsDumper.dumpTrees = True
process.tagsDumper.nameTemplate = cms.untracked.string("$PROCESS_$SQRTS_$CLASSNAME_$SUBCAT_$LABEL")

tagList = [
    ["TTHHadronicTag", 0],
    ["TTHLeptonicTag", 0]
]

definedSysts=set()
process.tagsDumper.classifierCfg.remap=cms.untracked.VPSet()

import flashgg.Taggers.dumperConfigTools as cfgTools

for tag in tagList:
    tagName = tag[0]
    tagCats = tag[1]
    # remap return value of class-based classifier
    process.tagsDumper.classifierCfg.remap.append( cms.untracked.PSet( src=cms.untracked.string("flashgg%s"%tagName), dst=cms.untracked.string(tagName) ) )
    print "Systematics with independent collections", systlabels
    for systlabel in systlabels:
        if not systlabel in definedSysts:
            # the cut corresponding to the systematics can be defined just once
            cutstring = "hasSyst(\"%s\") "%(systlabel)
            definedSysts.add(systlabel)
        else:
            cutstring = None

        if systlabel == "":
            currentVariables = variablesToUse
            print "Systematics affecting weights", currentVariables
        else:
            currentVariables = systematicVariables

        currentVariables += dipho_variables
        if "Hadronic" in tagName:
            currentVariables += hadronic_variables
        elif "Leptonic" in tagName:
            currentVariables += leptonic_variables
            currentVariables = [var for var in currentVariables if var not in hadronic_variables] # I don't understand why I need to do this, but the hadronic variables get added for some reason...

        currentVariables = list(set(currentVariables))
        isBinnedOnly = (systlabel !=  "")
        cfgTools.addCategory(process.tagsDumper, systlabel, classname=tagName, cutbased=cutstring, subcats=tagCats, variables=currentVariables, histograms=[], binnedOnly=isBinnedOnly, dumpPdfWeights=False)
        currentVariables = []


process.p = cms.Path(    #process.dataRequirements* # don't require trigger because it's already required in microAOD production
                         #process.flashggMetFilters*
                         process.genFilter* # revisit later, this looks like it's only needed for other signal modes than ttH
                         process.flashggDiPhotons* # needed for 0th vertex from microAOD
                         process.flashggDifferentialPhoIdInputsCorrection* 
                         process.flashggDiPhotonSystematics* 
                         process.flashggMetSystematics*
                         process.flashggMuonSystematics*process.flashggElectronSystematics*
                         (process.flashggUnpackedJets*process.jetSystematicsSequence)*
                         (process.flashggTagSequence*process.systematicsTagSequences)*
			             process.flashggSystTagMerger*
			             #process.flashggTagSequence*
                         #process.flashggTagTester*
                         process.penultimateFilter*
                         process.tagsDumper)
                         #(process.tthLeptonicTagDumper
                         # +process.tthHadronicTagDumper))

modifySystematicsWorkflowForttH(process, systlabels, phosystlabels, metsystlabels, jetsystlabels)

print process.p
