#include "flashgg/DataFormats/interface/FCNCLeptonicTag.h"
#include <algorithm>

using namespace flashgg;

FCNCLeptonicTag::FCNCLeptonicTag() : DiPhotonTagBase::DiPhotonTagBase()
{}

FCNCLeptonicTag::~FCNCLeptonicTag()
{}

// N.B. Other attributes are set using methods in header file
FCNCLeptonicTag::FCNCLeptonicTag( edm::Ptr<DiPhotonCandidate> diPho, edm::Ptr<DiPhotonMVAResult> mvares ) : FCNCLeptonicTag::FCNCLeptonicTag( diPho, *mvares ) {}
FCNCLeptonicTag::FCNCLeptonicTag( edm::Ptr<DiPhotonCandidate> dipho, DiPhotonMVAResult mvares ) : DiPhotonTagBase::DiPhotonTagBase( dipho, mvares ) {}

// Local Variables:
// mode:c++
// indent-tabs-mode:nil
// tab-width:4
// c-basic-offset:4
// End:
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

