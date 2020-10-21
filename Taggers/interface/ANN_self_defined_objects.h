#ifndef _ANNSEFLOBJECTS_H_
#define _ANNSEFLOBJECTS_H_
#include <memory>
#include <vector>
#include <string>
#include <utility>
#include "DataFormats/Math/interface/LorentzVector.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "TMVA/Reader.h"
#include <iostream>
#include <algorithm>
#include <TMath.h>

namespace flashgg {

typedef math::PtEtaPhiMLorentzVectorD ANN_rTT_ptvec;
//typedef math::PtEtaPhiELorentzVectorD ANN_rTT_energyvec;

class ANN_rTT_Photon : public ANN_rTT_ptvec{
 public:
  ANN_rTT_Photon() : ANN_rTT_ptvec(0,0,0,0){};
  ANN_rTT_Photon(float pt,float eta, float phi, float mass, float IDMVA)
      : ANN_rTT_ptvec(pt,eta,phi,mass), _IDMVA(IDMVA){};
  float _IDMVA = 0;
  float IDMVA() const {return _IDMVA;}
};

class ANN_rTT_Jet : public ANN_rTT_ptvec{
 public:
  ANN_rTT_Jet() : ANN_rTT_ptvec(0,0,0,0){};
  ANN_rTT_Jet(float pt,float eta, float phi, float mass, float deepcsv)
      : ANN_rTT_ptvec(pt,eta,phi,mass), _deepcsv(deepcsv){};
  float _deepcsv = 0;
  float deepcsv() const {return _deepcsv;}
};

class ANN_rTT_Lepton : public ANN_rTT_ptvec{
 public:
  ANN_rTT_Lepton() : ANN_rTT_ptvec(0,0,0,0){};
  ANN_rTT_Lepton(float pt,float eta, float phi, float mass, float id)
      : ANN_rTT_ptvec(pt,eta,phi,mass), _id(id){};
  float _id = 0;
  float id() const {return _id;}
};

}

#endif // _ANNSEFLOBJECTS_H_
