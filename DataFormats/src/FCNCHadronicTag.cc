#include "flashgg/DataFormats/interface/FCNCHadronicTag.h"
#include "flashgg/DataFormats/interface/Jet.h"

using namespace flashgg;

FCNCHadronicTag::FCNCHadronicTag() : DiPhotonTagBase::DiPhotonTagBase() {}

FCNCHadronicTag::~FCNCHadronicTag() {}

FCNCHadronicTag::FCNCHadronicTag( edm::Ptr<flashgg::DiPhotonCandidate> diPho, edm::Ptr<DiPhotonMVAResult> mvaRes,
                                std::vector<edm::Ptr<flashgg::Jet> > theJetVec , std::vector<edm::Ptr<flashgg::Jet> > theBJetVec ) :
    FCNCHadronicTag::FCNCHadronicTag( diPho, *mvaRes, theJetVec, theBJetVec ) {}

FCNCHadronicTag::FCNCHadronicTag( edm::Ptr<DiPhotonCandidate> dipho, DiPhotonMVAResult mvares,
                                std::vector<edm::Ptr<flashgg::Jet> > theJetVec , std::vector<edm::Ptr<flashgg::Jet> > theBJetVec ) :
    DiPhotonTagBase::DiPhotonTagBase( dipho, mvares )
{
    theJetVec_ = std::vector<edm::Ptr<flashgg::Jet> >( theJetVec );
    theBJetVec_ = std::vector<edm::Ptr<flashgg::Jet> >( theBJetVec );
}

// Local Variables:
// mode:c++
// indent-tabs-mode:nil
// tab-width:4
// c-basic-offset:4
// End:
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

