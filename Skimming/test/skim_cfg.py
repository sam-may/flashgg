import FWCore.ParameterSet.Config as cms

from flashgg.MicroAOD.flashggJets_cfi import flashggBTag
from flashgg.Taggers.flashggTags_cff import flashggTTHHadronicTag, flashggTTHLeptonicTag, bDiscriminator80XReReco

process = cms.Process("skim")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")

isMC = False

process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag
if isMC:
    process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data')

process.source = cms.Source("PoolSource",
			    fileNames = cms.untracked.vstring("file:myMicroAODOutputFile.root")		
                            # fileNames = cms.untracked.vstring("PUTFILENAMEHERE")
                            # fileNames = cms.untracked.vstring("file:../myMicroAODOutputFile_99.root")
                            # fileNames = cms.untracked.vstring("/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1741.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1742.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1743.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1744.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1745.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1746.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1747.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1748.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1749.root","/store/group/phys_higgs/cmshgg/sethzenz/flashgg/ReMiniAOD-03Feb2017-2_5_4/2_5_1/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/170310_111930/0001/myMicroAODOutputFile_1750.root")
)

print process.source.fileNames

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1 ) )
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.skimFilter = cms.EDFilter("SkimFilter",
                                  verbose = cms.bool(False),
                                  inputDiPhotons = cms.InputTag("flashggDiPhotons"),
                                  inputDiPhotonMVA = cms.InputTag("flashggDiPhotonMVA"),
                                  inputJets = cms.InputTag("flashggFinalJets"),
                                  inputElectrons = cms.InputTag("flashggSelectedElectrons"),
                                  inputMuons = cms.InputTag("flashggSelectedMuons"),
                                  inputVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                  rhoTag = cms.InputTag('fixedGridRhoFastjetAll'),
                                  btagDiscName = cms.string(flashggBTag),

                                  acceptIfNLeptons = cms.int32(2),
                				  dRPhoLepCut = cms.double(0.4),
                                  leptonPtThreshold = cms.double(5.0),
                                  muonEtaThreshold = cms.double(2.4), 
                				  muonIsoCut = flashggTTHLeptonicTag.MuonIsoCut,

                                  electronEtaThresholds = flashggTTHLeptonicTag.EleEtaCuts,
                				  ElePhotonZMassCut = flashggTTHLeptonicTag.ElePhotonZMassCut,
                				  DeltaRTrkEle = flashggTTHLeptonicTag.DeltaRTrkEle,

                                  diphotonMVAcut = cms.double(-999.0),
                                  diphotonLeadPtOverMassCut = cms.double(0.0),
                                  diphotonSubLeadPtOverMassCut = cms.double(0.0),

                                  jetPtThresh = cms.double(20.0),
                                  jetEtaThresh = cms.double(2.4),
                                  btagDiscThresh = cms.double(bDiscriminator80XReReco[0]), # loose
                                  nJetCut = cms.int32(2),
                                  nBJetCut = cms.int32(0),
                                  dRLeadPhoJetCut = flashggTTHHadronicTag.dRJetPhoLeadCut,
                                  dRSubLeadPhoJetCut = flashggTTHHadronicTag.dRJetPhoSubleadCut
)

#process.load("flashgg.Taggers.flashggDiPhotonMVA_cfi")
#process.load("flashgg.Taggers.flashggPreselectedDiPhotons_cfi")
#process.load("flashgg.Taggers.flashggUpdatedIdMVADiPhotons_cfi")

process.load("flashgg/MicroAOD/flashggDiPhotons_cfi")
process.flashggDiPhotons.whichVertex = cms.uint32(0)
process.flashggDiPhotons.useZerothVertexFromMicro = cms.bool(True)

process.p = cms.Path(
        process.flashggDiPhotons *
        process.skimFilter
)

#process.p = cms.Path(#process.flashggDiPhotons *
#                     process.flashggUpdatedIdMVADiPhotons * 
#                     process.flashggPreselectedDiPhotons * 
#                     process.flashggDiPhotonMVA *
#                     process.skimFilter
#)

process.out = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string("test_skim.root"),
                               # fileName = cms.untracked.string("file:/hadoop/cms/store/user/bemarsh/flashgg/MicroAOD_skim/2016_skim_v3_jetPt20/DoubleEG/ReMiniAOD-03Feb2017-2_5_4-2_5_1-v0-Run2016H-03Feb2017_ver2-v1/microAOD_175.root"),
                               outputCommands = cms.untracked.vstring("keep *","drop *_flashggDiPhotonMVA_*_*","drop *_flashggUpdatedIdMVADiPhotons_*_*","drop *_flashggPreselectedDiPhotons_*_*",),
                               SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring("p") )
)

process.outpath = cms.EndPath(process.out)
