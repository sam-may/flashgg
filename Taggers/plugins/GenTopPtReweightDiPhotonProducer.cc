#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/EDMException.h"

#include "flashgg/DataFormats/interface/DiPhotonCandidate.h"

#include "TMVA/Reader.h"
#include "TMath.h"
#include "TH1.h"
#include <string>
#include <algorithm>

using namespace std;
using namespace edm;

namespace flashgg {

    class GenTopPtReweightDiPhotonProducer : public EDProducer
    {
        public:
            GenTopPtReweightDiPhotonProducer( const ParameterSet & );
        private:
            void produce( Event &, const EventSetup &) override;

            std::vector<double> getGenTops_pT (Handle<View<reco::GenParticle>>);

            double getLOtoNLO_SF( TH1D*, double, double );
            double getLOtoNLO_SF_unc( TH1D*, double, double );
            double NLOtoNNLO_Formula(double );
            double getNLOtoNNLO_SF( double, double );

            bool applyToCentral_;

            FileInPath sfFileName_;
            std::string sfHistName_;
            TH1D* sfHist_;

            EDGetTokenT<View<DiPhotonCandidate> > diPhotonToken_;
            EDGetTokenT<View<reco::GenParticle>> genParticlesToken_;

            bool debug_;
    };

    GenTopPtReweightDiPhotonProducer::GenTopPtReweightDiPhotonProducer( const ParameterSet &iConfig ) :
        diPhotonToken_( consumes<View<flashgg::DiPhotonCandidate> >( iConfig.getParameter<InputTag> ( "DiPhotonTag" ) ) ),
        genParticlesToken_( consumes<View<reco::GenParticle> >( iConfig.getParameter<InputTag> ( "GenParticleTag" ) ) ),
        debug_( iConfig.getParameter<bool> ( "debug")) 
    {

        produces<std::vector<flashgg::DiPhotonCandidate> >();
        
        applyToCentral_ = iConfig.getParameter<bool>("applyToCentral");
        if (applyToCentral_) {
            sfFileName_ = iConfig.getParameter<edm::FileInPath>( "sfFileName" );
            TFile* sf_hist_file = TFile::Open(sfFileName_.fullPath().c_str());
            sfHistName_ = iConfig.getUntrackedParameter<std::string>( "sfHistName" );
            sfHist_ = (TH1D*)((TH1D*) sf_hist_file->Get(sfHistName_.c_str()))->Clone();
            sf_hist_file->Close();
            delete sf_hist_file;
        } 

    }

    std::vector<double> GenTopPtReweightDiPhotonProducer::getGenTops_pT(Handle<View<reco::GenParticle>> genParticles)
    {
        int n_matched_tops(0), n_matched_antitops(0);

        std::vector<double> gen_pt = { 0, 0 }; // { top pt, antitop pt }
        for (unsigned int i = 0; i < genParticles->size(); i++) {
            int pdgid = genParticles->ptrAt( i )->pdgId();
            if (!(abs(pdgid) == 6)) // skip if not a top/antitop
                continue;
    
            bool lastCopy = genParticles->ptrAt( i )->isLastCopy();
            if (!lastCopy) // skip if not isLastCopy
                continue;

            if (pdgid == 6) {
                gen_pt[0] = genParticles->ptrAt( i )->pt();
                n_matched_tops++;
            }
            else if (pdgid == -6) {
                gen_pt[1] = genParticles->ptrAt( i )->pt();
                n_matched_antitops++;
            }
        }
        if (n_matched_tops != 1 || n_matched_antitops != 1)
            throw cms::Exception("Did not match exactly 1 top and exactly 1 antitop in gen particles collection.");
        return gen_pt;
    }

    double GenTopPtReweightDiPhotonProducer::getLOtoNLO_SF(TH1D* sfHist, double gen_top_pt, double gen_antitop_pt)
    {
        double top_sf = sfHist->GetBinContent( sfHist->FindBin(gen_top_pt) );
        double antitop_sf = sfHist->GetBinContent( sfHist->FindBin(gen_antitop_pt) );
        return pow(top_sf * antitop_sf, 0.5); // take geometric mean of two SFs
    }

    double GenTopPtReweightDiPhotonProducer::getLOtoNLO_SF_unc(TH1D* sfHist, double gen_top_pt, double gen_antitop_pt)
    {
        double top_sf = sfHist->GetBinContent( sfHist->FindBin(gen_top_pt) );
        double antitop_sf = sfHist->GetBinContent( sfHist->FindBin(gen_antitop_pt) );

        double top_sf_unc = sfHist->GetBinError( sfHist->FindBin(gen_top_pt) );
        double antitop_sf_unc = sfHist->GetBinError( sfHist->FindBin(gen_antitop_pt) );

        // propagate individual statistical uncertainties through f(x,y) = sqrt(xy) -> sigma_f = sqrt( (x/4y)*sigma_x^2 + (y/4x)*sigma_y^2)
        return pow( ((antitop_sf / (4*top_sf)) * pow(top_sf_unc, 2)) + ((top_sf / (4*antitop_sf)) * pow(antitop_sf_unc, 2)), 0.5);
    }

    double GenTopPtReweightDiPhotonProducer::NLOtoNNLO_Formula(double pt)
    {
        return (0.103 * exp(-0.0118*pt)) - (0.000134*pt) + 0.973;
    }

    double GenTopPtReweightDiPhotonProducer::getNLOtoNNLO_SF(double gen_top_pt, double gen_antitop_pt)
    {
        double top_sf = NLOtoNNLO_Formula(gen_top_pt);
        double antitop_sf = NLOtoNNLO_Formula(gen_antitop_pt);
        return pow(top_sf * antitop_sf, 0.5); // take geometric mean of two SFs
    }

    void GenTopPtReweightDiPhotonProducer::produce( Event &evt, const EventSetup & )
    {
        Handle<View<flashgg::DiPhotonCandidate> > diPhotons;
        evt.getByToken( diPhotonToken_, diPhotons );

        Handle<View<reco::GenParticle> > genParticles;
        evt.getByToken( genParticlesToken_, genParticles );

        unique_ptr<std::vector<flashgg::DiPhotonCandidate> > updatedDiphotons( new std::vector<flashgg::DiPhotonCandidate>() );
        for( unsigned int candIndex = 0; candIndex < diPhotons->size() ; candIndex++ ) {
            edm::Ptr<flashgg::DiPhotonCandidate> dipho = diPhotons->ptrAt(candIndex);
            flashgg::DiPhotonCandidate *updatedDipho = dipho->clone();
            
            WeightedObject genTopPtReweightObject;

            if (applyToCentral_) {
                std::vector<double> gen_pt = getGenTops_pT(genParticles);
                double top_pt = gen_pt[0];
                double antitop_pt = gen_pt[1];

                double LOtoNLO_SF = getLOtoNLO_SF(sfHist_, top_pt, antitop_pt);
                double LOtoNLO_SF_unc = getLOtoNLO_SF_unc(sfHist_, top_pt, antitop_pt);

                double NLOtoNNLO_SF = getNLOtoNNLO_SF(top_pt, antitop_pt);

                double SF = LOtoNLO_SF * NLOtoNNLO_SF;                

                if (debug_) {
                    std::cout << "Top (antitop) pt identified as " << top_pt << " (" << antitop_pt << ")" << std::endl;
                    std::cout << "LO to NLO scale factor: " << LOtoNLO_SF << std::endl;
                    std::cout << "LO to NLO scale factor unc: " << LOtoNLO_SF_unc << std::endl;
                    std::cout << "NLO to NNLO scale factor: " << NLOtoNNLO_SF << std::endl;
                    std::cout << "Final scale factor and variations: central = " << SF << ", up = " << SF + LOtoNLO_SF_unc << ", down = " << SF - LOtoNLO_SF_unc << std::endl;
                }

                genTopPtReweightObject.setCentralWeight(SF);
                genTopPtReweightObject.setWeight("genTopPtReweightUp01sigma", SF + LOtoNLO_SF_unc);
                genTopPtReweightObject.setWeight("genTopPtReweightDown01sigma", SF - LOtoNLO_SF_unc);

                updatedDipho->includeWeights(genTopPtReweightObject);
            }

            else {
                genTopPtReweightObject.setWeight("genTopPtReweight", 1.);
                genTopPtReweightObject.setWeight("genTopPtReweightUp01sigma", 1.);
                genTopPtReweightObject.setWeight("genTopPtReweightDown01sigma", 1.);
                
                updatedDipho->includeWeights(genTopPtReweightObject); 
            }

            updatedDiphotons->push_back(*updatedDipho);
            delete updatedDipho;
        }
        evt.put( std::move(updatedDiphotons) );
    }
}

typedef flashgg::GenTopPtReweightDiPhotonProducer FlashggGenTopPtReweightDiPhotonProducer;
DEFINE_FKW_MODULE( FlashggGenTopPtReweightDiPhotonProducer );
// Local Variables:
// mode:c++
// indent-tabs-mode:nil
// tab-width:4
// c-basic-offset:4
// End:
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

