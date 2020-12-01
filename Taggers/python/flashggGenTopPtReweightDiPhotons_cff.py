import FWCore.ParameterSet.Config as cms

flashggGenTopPtReweightDiPhotons = cms.EDProducer("FlashggGenTopPtReweightDiPhotonProducer",
        DiPhotonTag = cms.InputTag("flashggDifferentialPhoIdInputsCorrection"),
        GenParticleTag = cms.InputTag("flashggPrunedGenParticles"),
        sfFileName = cms.FileInPath("flashgg/Taggers/data/top_pt_sfs.root"),
        sfHistName = cms.untracked.string("pt_ratio"),
        applyToCentral = cms.bool(False),
        debug = cms.bool(True)
)
