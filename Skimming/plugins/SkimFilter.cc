// -*- C++ -*-
//
// Package:    flashgg/SkimFilter
// Class:      SkimFilter
// 
/**\class SkimFilter SkimFilter.cc flashgg/Skimming/plugins/SkimFilter.cc
*/
//
// Original Author:  bmarsh@umail.ucsb.edu 6-10-2015
//         Created:  Thu, 01 Mar 2018 18:14:31 GMT
//
//


// system include files
#include <memory>
#include <iostream> 

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/EDMException.h"

#include "DataFormats/Common/interface/Handle.h"
#include "flashgg/DataFormats/interface/Jet.h"
#include "flashgg/DataFormats/interface/Electron.h"
#include "flashgg/DataFormats/interface/Muon.h"
#include "flashgg/DataFormats/interface/DiPhotonCandidate.h"
#include "flashgg/DataFormats/interface/DiPhotonMVAResult.h"

#include "flashgg/Taggers/interface/LeptonSelection2018.h"

#include "DataFormats/Math/interface/deltaR.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"



//
// class declaration
//

class SkimFilter : public edm::stream::EDFilter<> {
  public:
    explicit SkimFilter(const edm::ParameterSet&);
    ~SkimFilter();

  private:
    virtual bool filter(edm::Event&, const edm::EventSetup&) override;
    bool CheckJetCollection(uint jetCollectionIdx, const std::vector< std::vector< flashgg::Jet> >* jets, const flashgg::DiPhotonCandidate& diphotons, const int nJetThresh_ = 2);

      // ----------member data ---------------------------
    edm::EDGetTokenT<std::vector< std::vector< flashgg::Jet> > > jetToken_;
    edm::EDGetTokenT< std::vector< flashgg::DiPhotonCandidate> > diphoToken_;
    edm::EDGetTokenT<View<flashgg::DiPhotonCandidate> > diPhotonToken_;
    edm::EDGetTokenT< std::vector< flashgg::DiPhotonMVAResult> > diphoMVAToken_;
    edm::EDGetTokenT< edm::View< flashgg::Electron> > electronToken_;
    edm::EDGetTokenT< edm::View< flashgg::Muon> > muonToken_;
    edm::EDGetTokenT< edm::View< reco::Vertex> > vertexToken_;
    edm::EDGetTokenT<double> rhoToken_;

    bool verbose_;

    string btagDiscName_;

    int acceptIfNLeptons_;
    double dRPhoLepCut_;
    double leptonPtThreshold_;
    double muonEtaThreshold_;
    double muonIsoCut_;
    vector<double>  electronEtaThresholds_;
    double ElePhotonZMassCut_;
    double DeltaRTrkEle_;


    double jetPtThresh_;
    double jetEtaThresh_;
    double btagDiscThresh_;

    double diphotonMVAcut_;
    double diphotonLeadPtOverMassCut_;
    double diphotonSubLeadPtOverMassCut_;

    int nJetCut_;
    int nBJetCut_;

    double dRLeadPhoJetCut_;
    double dRSubLeadPhoJetCut_;
};

//
// constructors and destructor
//
SkimFilter::SkimFilter(const edm::ParameterSet& iConfig) :
    jetToken_( consumes< std::vector< std::vector< flashgg::Jet> > >(iConfig.getParameter<edm::InputTag>("inputJets"))),
    diphoToken_( consumes< std::vector< flashgg::DiPhotonCandidate> >(iConfig.getParameter<edm::InputTag>("inputDiPhotons"))),
    diPhotonToken_( consumes<View<flashgg::DiPhotonCandidate> >( iConfig.getParameter<InputTag> ( "inputDiPhotons" ) ) ),
    diphoMVAToken_( consumes< std::vector< flashgg::DiPhotonMVAResult> >(iConfig.getParameter<edm::InputTag>("inputDiPhotonMVA"))),
    electronToken_( consumes< edm::View< flashgg::Electron> >(iConfig.getParameter<edm::InputTag>("inputElectrons"))),
    muonToken_( consumes< edm::View< flashgg::Muon> >(iConfig.getParameter<edm::InputTag>("inputMuons"))),
    vertexToken_( consumes< edm::View< reco::Vertex> >(iConfig.getParameter<edm::InputTag>("inputVertices"))),
    rhoToken_( consumes<double>(iConfig.getParameter<edm::InputTag>("rhoTag")))
{
    verbose_ = iConfig.getParameter<bool>("verbose");

    btagDiscName_ = iConfig.getParameter<string>("btagDiscName");

    acceptIfNLeptons_ = iConfig.getParameter<int>("acceptIfNLeptons");
    dRPhoLepCut_ = iConfig.getParameter<double>("dRPhoLepCut");
    leptonPtThreshold_ = iConfig.getParameter<double>("leptonPtThreshold");
    muonEtaThreshold_ = iConfig.getParameter<double>("muonEtaThreshold");
    muonIsoCut_ = iConfig.getParameter<double>("muonIsoCut");
    electronEtaThresholds_ = iConfig.getParameter<vector<double > >( "electronEtaThresholds");
    ElePhotonZMassCut_ = iConfig.getParameter<double>("ElePhotonZMassCut");
    DeltaRTrkEle_ = iConfig.getParameter<double>("DeltaRTrkEle");


    jetPtThresh_ = iConfig.getParameter<double>("jetPtThresh");
    jetEtaThresh_ = iConfig.getParameter<double>("jetEtaThresh");
    btagDiscThresh_ = iConfig.getParameter<double>("btagDiscThresh");

    diphotonMVAcut_ = iConfig.getParameter<double>("diphotonMVAcut");
    diphotonLeadPtOverMassCut_ = iConfig.getParameter<double>("diphotonLeadPtOverMassCut");
    diphotonSubLeadPtOverMassCut_ = iConfig.getParameter<double>("diphotonSubLeadPtOverMassCut");

    nJetCut_ = iConfig.getParameter<int>("nJetCut");
    nBJetCut_ = iConfig.getParameter<int>("nBJetCut");

    dRLeadPhoJetCut_ = iConfig.getParameter<double>("dRLeadPhoJetCut");    
    dRSubLeadPhoJetCut_ = iConfig.getParameter<double>("dRSubLeadPhoJetCut");    
}


SkimFilter::~SkimFilter()
{
}

//
// member functions
//

// ------------ method called on each new Event  ------------
bool
SkimFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

    edm::Handle< std::vector< std::vector< flashgg::Jet> > > jets_h;
    iEvent.getByToken(jetToken_, jets_h);
    const std::vector< std::vector< flashgg::Jet> >* jets = jets_h.product();
    
    edm::Handle< std::vector< flashgg::DiPhotonCandidate> > diphos_h;
    iEvent.getByToken(diphoToken_, diphos_h);
    const std::vector< flashgg::DiPhotonCandidate >* diphotons = diphos_h.product();

    Handle<View<flashgg::DiPhotonCandidate> > diPhotons;
    iEvent.getByToken(diPhotonToken_, diPhotons);

    //edm::Handle< std::vector< flashgg::DiPhotonMVAResult> > diphomva_h;
    //iEvent.getByToken(diphoMVAToken_, diphomva_h);
    //const std::vector< flashgg::DiPhotonMVAResult >* diphotonMVAs = diphomva_h.product();

    edm::Handle< edm::View<flashgg::Electron> > electrons_h;
    iEvent.getByToken(electronToken_, electrons_h);

    edm::Handle< edm::View<flashgg::Muon> > muons_h;
    iEvent.getByToken(muonToken_, muons_h);

    edm::Handle< edm::View< reco::Vertex> > vertices_h;
    iEvent.getByToken(vertexToken_, vertices_h);

    edm::Handle<double>  rho_h;
    iEvent.getByToken(rhoToken_,rho_h);
    double rho    = *rho_h;

    // select loose leptons
    //goodMuons = selectMuons(muons_h->ptrs(), 
 

    std::vector<edm::Ptr<flashgg::Muon> > goodMuons;
    /*
    if( !useStdLeptonID_) {
        goodMuons = selectAllMuonsSum16( muons_h->ptrs(), vertices_h->ptrs(), muonEtaThreshold_ , 
                                         leptonPtThreshold_, muMiniIsoSumRelThreshold_ );
    } else {
        goodMuons = selectAllMuons( muons_h->ptrs(), vertices_h->ptrs(), muonEtaThreshold_ , 
                                    leptonPtThreshold_, muPFIsoSumRelThreshold_ );
    }
    */
    std::vector<edm::Ptr<flashgg::Electron> > goodElectrons ;
    //goodElectrons = selectStdAllElectrons(electrons_h->ptrs(), vertices_h->ptrs(), leptonPtThreshold_, electronEtaThresholds_,
    //                                      useElectronMVARecipe_, useElectronLooseID_,
    //                                      rho, iEvent.isRealData() );


    // loop over all diphoton pairs and check if good. If none good, return false
    uint nDiPhotons = diphotons->size();
    for(uint idp=0; idp < nDiPhotons; idp++){

        // Select leps
    	edm::Ptr<flashgg::DiPhotonCandidate> dipho = diPhotons->ptrAt(idp);

        goodMuons = selectMuons( muons_h->ptrs(), dipho, vertices_h->ptrs(), leptonPtThreshold_, muonEtaThreshold_, muonIsoCut_, dRPhoLepCut_, 0, 2); // 1 means loose ID
        goodElectrons = selectElectrons( electrons_h->ptrs(), dipho, leptonPtThreshold_, electronEtaThresholds_, dRPhoLepCut_, ElePhotonZMassCut_, DeltaRTrkEle_, 0, 2); // 1 means loose ID 

        float leadPt = diphotons->at(idp).leadingPhoton()->pt();
        float subleadPt = diphotons->at(idp).subLeadingPhoton()->pt();
        float mass = diphotons->at(idp).mass();
        //float mva = diphotonMVAs->at(idp).mvaValue();

        //if(verbose_) std::cout << "    DiPhoton " << idp << ": " << mass << ", " << leadPt << ", " << subleadPt << ", " << mva << std::endl;
        
        if( leadPt/mass < diphotonLeadPtOverMassCut_ || subleadPt/mass < diphotonSubLeadPtOverMassCut_)
            continue;

        //if( mva < diphotonMVAcut_ )
        //    continue;

    	int nGoodLep = goodMuons.size() + goodElectrons.size();

        if(nGoodLep >= acceptIfNLeptons_)
            return true; // accept if >= 2 good leps

        uint jetCollectionIdx = diphotons->at(idp).jetCollectionIndex();

    	if (nGoodLep >= 1) {
	        if (CheckJetCollection(jetCollectionIdx, jets, diphotons->at(idp), 1) || (jetCollectionIdx==0 || !CheckJetCollection(0, jets, diphotons->at(idp), 1)))
	        return true; // accepts if >= 1 good leps and >=1 good jets
        }


        // check jet collections
        if(!CheckJetCollection(jetCollectionIdx, jets, diphotons->at(idp), nJetCut_) && (jetCollectionIdx==0 || !CheckJetCollection(0, jets, diphotons->at(idp), nJetCut_)))
            continue; // continue if not >= 2 good jets
        
        // if we've made it here, then it is a good photon pair.
        return true;
    }

   return false;
}

bool SkimFilter::CheckJetCollection(uint jetCollectionIdx, const std::vector< std::vector< flashgg::Jet> >* jets, const flashgg::DiPhotonCandidate& diphoton, const int nJetThresh_){

    if (jetCollectionIdx > jets->size() - 1){
        if(verbose_) std::cout << "SHOULDN'T GET HERE" << std::endl;
        return false;
    }

    uint njet = jets->at(jetCollectionIdx).size();
    int nGoodJet = 0;
    int nGoodBJet = 0;
    if(verbose_) std::cout << "    jet collection " << jetCollectionIdx << ", " << njet << " jets\n";
    for(uint j=0; j<njet; j++){
        const flashgg::Jet& jet = jets->at(jetCollectionIdx).at(j);
        if(verbose_) std::cout << "      " << jet.pt() << std::endl;

        if(jet.pt() > jetPtThresh_ && fabs(jet.eta()) < jetEtaThresh_ && 
           deltaR(jet.eta(), jet.phi(), diphoton.leadingPhoton()->eta(), diphoton.leadingPhoton()->phi()) > dRLeadPhoJetCut_ && 
           deltaR(jet.eta(), jet.phi(), diphoton.subLeadingPhoton()->eta(), diphoton.subLeadingPhoton()->phi()) > dRSubLeadPhoJetCut_) {
            nGoodJet += 1;
            float bDisc = jets->at(jetCollectionIdx).at(j).bDiscriminator(btagDiscName_);
            if(bDisc > btagDiscThresh_)
                nGoodBJet += 1;
        }
            
    }

    if(verbose_) std::cout << "     nJet: " << nGoodJet << std::endl;
    if(verbose_) std::cout << "    nBJet: " << nGoodBJet << std::endl;

    if(nGoodJet < nJetThresh_)
        return false;
        
    if(nGoodBJet < nBJetCut_)
        return false;

    return true;
 
}

//define this as a plug-in
DEFINE_FWK_MODULE(SkimFilter);
