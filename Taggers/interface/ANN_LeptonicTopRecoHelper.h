#ifndef _ANN_HADRONIC_TOP_RECO_HELPER_
#define _ANN_HADRONIC_TOP_RECO_HELPER_

#include "flashgg/Taggers/interface/ANN_self_defined_objects.h"

namespace flashgg {

//class ANN_Leptonic_top_pair {{{
class ANN_Leptonic_top_pair {
public:
  ANN_Leptonic_top_pair(){};
  ANN_Leptonic_top_pair(std::shared_ptr<ANN_rTT_Photon> _leading_photon, std::shared_ptr<ANN_rTT_Photon> _subleading_photon, std::shared_ptr<ANN_rTT_Jet> _b, std::shared_ptr<ANN_rTT_Jet> _j2, std::shared_ptr<ANN_rTT_Lepton> _l ){

    leading_photon = _leading_photon;
    subleading_photon = _subleading_photon;
    b = _b;
    j2 = _j2; // q-jet
    l = _l; // lepton 

    *diphoton = *(dynamic_cast<ANN_rTT_ptvec*>(leading_photon.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(subleading_photon.get()));
    *top_tqh = (_j2!=NULL) ? *diphoton + *(dynamic_cast<ANN_rTT_ptvec*>(j2.get())) : *diphoton; // warnning: diphoton info

  }
  std::shared_ptr<ANN_rTT_ptvec> diphoton = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> top_tqh = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_Photon> leading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Photon> subleading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Jet> b = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j2 = nullptr;
  std::shared_ptr<ANN_rTT_Lepton> l = nullptr;
  float score = -99;
  int j1idx = -99;
  int j2idx = -99;
  int l1idx = -99;
};
//}}}
//class ANN_Leptonic_single_top {{{
class ANN_Leptonic_single_top {
public:
  ANN_Leptonic_single_top(){};
  ANN_Leptonic_single_top(std::shared_ptr<ANN_rTT_Photon> _leading_photon, std::shared_ptr<ANN_rTT_Photon> _subleading_photon, std::shared_ptr<ANN_rTT_Jet> _b, std::shared_ptr<ANN_rTT_Lepton> _l ){

    leading_photon = _leading_photon;
    subleading_photon = _subleading_photon;
    b = _b;
    l = _l;

    *diphoton = *(dynamic_cast<ANN_rTT_ptvec*>(leading_photon.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(subleading_photon.get()));

  }
  std::shared_ptr<ANN_rTT_ptvec> diphoton = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_Photon> leading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Photon> subleading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Jet> b = nullptr;
  std::shared_ptr<ANN_rTT_Lepton> l = nullptr;
  float score = -99;
  int j1idx = -99;
  int l1idx = -99;
};
//}}}
//class ANN_LeptonicTopTagger {{{
class ANN_LeptonicTopTagger {
public:
  ANN_LeptonicTopTagger(std::string weight_file_name_01, std::string weight_file_name_02){
    Init_tt(weight_file_name_01);
    Init_st(weight_file_name_02);
  };

  ~ANN_LeptonicTopTagger(){
    clear();
  };

  void addJet(float pt,float eta, float phi, float mass, float deepcsv){
    jets.push_back(std::make_shared<ANN_rTT_Jet>(pt,eta,phi,mass,deepcsv));
  };
  
  void addPhoton(float pt,float eta, float phi, float mass, float IDMVA){
    photons.push_back(std::make_shared<ANN_rTT_Photon>(pt,eta,phi,mass, IDMVA));
  };
  
  void addLepton(float pt, float eta, float phi, float mass, float id){
    leptons.push_back(std::make_shared<ANN_rTT_Lepton>(pt,eta,phi,mass,id));
  };
  
  void addElectron(float pt, float eta, float phi, float mass, float id){
    electrons.push_back(std::make_shared<ANN_rTT_Lepton>(pt,eta,phi,mass,id));
  };
  
  void addMuon(float pt, float eta, float phi, float mass, float id){
    muons.push_back(std::make_shared<ANN_rTT_Lepton>(pt,eta,phi,mass,id));
  };
  
  void addMet(float pt, float phi){
    Met_Pt = pt;
    Met_Phi = phi;
  };
  
  void clear();
  void Init_tt(std::string weight_file_name);
  void Init_st(std::string weight_file_name);
  
  std::vector<float> EvalMVA_tt();
  std::vector<float> EvalMVA_st();

  void setDebug(bool val){debug = val;};

private:

  std::vector<std::shared_ptr<ANN_rTT_Jet>> jets;
  std::vector<std::shared_ptr<ANN_rTT_Photon>> photons;
  std::vector<std::shared_ptr<ANN_rTT_Lepton>> leptons;
  std::vector<std::shared_ptr<ANN_rTT_Lepton>> electrons;
  std::vector<std::shared_ptr<ANN_rTT_Lepton>> muons;

  float EvalScore_tt(const std::shared_ptr<ANN_Leptonic_top_pair>);
  float EvalScore_st(const std::shared_ptr<ANN_Leptonic_single_top>);

  std::shared_ptr<TMVA::Reader> reader_tt = nullptr;
  std::shared_ptr<TMVA::Reader> reader_st = nullptr;

  float bJet_Pt = -99;
  float bJet_Eta = -99;
  float bJet_btag = -99;
  float M1Jet_Pt = -99;
  float M1Jet_Eta = -99;
  float M1Jet_btag = -99;
  float lep_ID = -99;
  float lep_Pt = -99;
  float lep_Eta = -99;
  float M1 = -99;
  float dR_qH = -99;
  float dR_lb = -99;
  float dR_lt = -99;
  float dR_lH = -99;
  float dPhi_bMET = -99;
  float Met_Phi = -99;
  float Met_Pt = -99;

  bool debug = false;

};
//}}}

//void ANN_LeptonicTopTagger::Init_tt(std::string weight_file_name){{{
inline
void ANN_LeptonicTopTagger::Init_tt(std::string weight_file_name){

  reader_tt = std::make_shared<TMVA::Reader>( "!Color:!Silent" );

  reader_tt->AddVariable("bJet_Pt", &bJet_Pt);
  reader_tt->AddVariable("bJet_Eta", &bJet_Eta);
  reader_tt->AddVariable("bJet_btag", &bJet_btag);
  reader_tt->AddVariable("M1Jet_Pt", &M1Jet_Pt);
  reader_tt->AddVariable("M1Jet_Eta", &M1Jet_Eta);
  reader_tt->AddVariable("M1Jet_btag", &M1Jet_btag);
  reader_tt->AddVariable("lep_ID", &lep_ID);
  reader_tt->AddVariable("lep_Pt", &lep_Pt);
  reader_tt->AddVariable("lep_Eta", &lep_Eta);
  reader_tt->AddVariable("M1", &M1);
  reader_tt->AddVariable("dR_qH", &dR_qH);
  reader_tt->AddVariable("dR_lb", &dR_lb);
  reader_tt->AddVariable("dR_lt", &dR_lt);
  reader_tt->AddVariable("dPhi_bMET", &dPhi_bMET);
  reader_tt->AddVariable("Met_Pt", &Met_Pt);

  reader_tt->BookMVA("TT_lep_MVA", weight_file_name);
};
//}}}
//void ANN_LeptonicTopTagger::Init_st(std::string weight_file_name){{{
inline
void ANN_LeptonicTopTagger::Init_st(std::string weight_file_name){

  reader_st = std::make_shared<TMVA::Reader>( "!Color:!Silent" );

  reader_st->AddVariable("bJet_Pt", &bJet_Pt);
  reader_st->AddVariable("bJet_Eta", &bJet_Eta);
  reader_st->AddVariable("bJet_btag", &bJet_btag);
  reader_st->AddVariable("lep_ID", &lep_ID);
  reader_st->AddVariable("lep_Pt", &lep_Pt);
  reader_st->AddVariable("lep_Eta", &lep_Eta);
  reader_st->AddVariable("dR_lb", &dR_lb);
  reader_st->AddVariable("dR_lH", &dR_lH);
  reader_st->AddVariable("dPhi_bMET", &dPhi_bMET);
  reader_st->AddVariable("Met_Pt", &Met_Pt);
  
  reader_st->BookMVA("ST_lep_MVA", weight_file_name);
};
//}}}
//void ANN_LeptonicTopTagger::clear(){{{
inline
void ANN_LeptonicTopTagger::clear(){

  jets.clear();
  photons.clear();
  leptons.clear();
  electrons.clear();
  muons.clear();

  bJet_Pt = -99;
  bJet_Eta = -99;
  bJet_btag = -99;
  M1Jet_Pt = -99;
  M1Jet_Eta = -99;
  M1Jet_btag = -99;
  lep_ID = -99;
  lep_Pt = -99;
  lep_Eta = -99;
  M1 = -99;
  dR_qH = -99;
  dR_lb = -99;
  dR_lt = -99;
  dR_lH = -99;
  dPhi_bMET = -99;
  Met_Phi = -99;
  Met_Pt = -99;

}
//}}}
//std::vector<float> ANN_LeptonicTopTagger::EvalMVA_tt(){{{
inline
std::vector<float> ANN_LeptonicTopTagger::EvalMVA_tt(){

  int njets = jets.size();
  int nleps = leptons.size();

  std::vector<std::shared_ptr<ANN_Leptonic_top_pair>> allcands;
  for (int i=0; i<njets; ++i) { // b-jet
    for (int j=0; j<njets; ++j) { // q-jet
      if(j == i) continue;
      for (int k=0; k<nleps; ++k) { // lepton
	      auto topcand = std::make_shared<ANN_Leptonic_top_pair>(photons[0], photons[1], jets.at(i), jets.at(j), leptons.at(k));
          topcand->score = EvalScore_tt(topcand);
          topcand->j1idx = i;
          topcand->j2idx = j;
          topcand->l1idx = k;
          allcands.push_back(topcand);
      }
    }
  }

  if (debug) std::cout << "Leptonic EvalScore_tt: njets = " << njets << " nleps = " << nleps ;

  std::vector<float> output(16,-99);
  if (allcands.size()>0) {
    // note: make sure this return max values
    auto top = *std::min_element(allcands.begin(),allcands.end(),[](const std::shared_ptr<ANN_Leptonic_top_pair> &a, const std::shared_ptr<ANN_Leptonic_top_pair> &b){return a->score > b->score;});
    output.at(0) = top->score; // mvaValue
  }
  if (debug) std::cout << "MVA score: " << output.at(0) << std::endl;
  return output;

};
//}}}
//std::vector<float> ANN_LeptonicTopTagger::EvalMVA_st(){{{
inline
std::vector<float> ANN_LeptonicTopTagger::EvalMVA_st(){

  int njets = jets.size();
  int nleps = leptons.size();

  std::vector<std::shared_ptr<ANN_Leptonic_single_top>> allcands;
  for (int i=0; i<njets; ++i) { // b-jet
    for (int k=0; k<nleps; ++k) { // lepton
	    auto topcand = std::make_shared<ANN_Leptonic_single_top>(photons[0], photons[1], jets.at(i), leptons.at(k));
        topcand->score = EvalScore_st(topcand);
        topcand->j1idx = i;
        topcand->l1idx = k;
        allcands.push_back(topcand);
    }
  }

  if (debug) std::cout << "Leptonic EvalScore_st: njets = " << njets << " nleps = " << nleps ;

  std::vector<float> output(16,-99);
  if (allcands.size()>0) {
    // note: make sure this return max values
    auto top = *std::min_element(allcands.begin(),allcands.end(),[](const std::shared_ptr<ANN_Leptonic_single_top> &a, const std::shared_ptr<ANN_Leptonic_single_top> &b){return a->score > b->score;});
    output.at(0) = top->score; // mvaValue
  }
  if (debug) std::cout << "MVA score: " << output.at(0) << std::endl;
  return output;

};
//}}}

//float ANN_LeptonicTopTagger::EvalScore_tt(const std::shared_ptr<ANN_Leptonic_top_pair> object){{{
inline
float ANN_LeptonicTopTagger::EvalScore_tt(const std::shared_ptr<ANN_Leptonic_top_pair> object){

  bJet_Pt    = object->b->pt();
  bJet_Eta   = object->b->eta();
  bJet_btag  = object->b->deepcsv();
  M1Jet_Pt   = object->j2->pt();
  M1Jet_Eta  = object->j2->eta();
  M1Jet_btag = object->j2->deepcsv();
  lep_ID     = object->l->id();
  lep_Pt     = object->l->pt();
  lep_Eta    = object->l->eta();
  M1         = object->top_tqh->mass();
  dR_qH      = deltaR(object->j2->eta(),object->j2->phi(),object->diphoton->eta(),object->diphoton->phi());
  dR_lb      = deltaR(object->l->eta(),object->l->phi(),object->b->eta(),object->b->phi());
  dR_lt      = deltaR(object->l->eta(),object->l->phi(),object->top_tqh->eta(),object->top_tqh->phi());
  dPhi_bMET = fabs( object->b->phi() - Met_Phi );
  if (dPhi_bMET > TMath::Pi()) dPhi_bMET = 2 * TMath::Pi() - dPhi_bMET;
  Met_Pt     = Met_Pt;


  float score = reader_tt->EvaluateMVA("TT_lep_MVA");

  if (debug) {
    std::cout << "bJet_Pt = " << bJet_Pt << " " ;
    std::cout << "bJet_Eta = " << bJet_Eta << " " ;
    std::cout << "bJet_btag = " << bJet_btag << " " ;
    std::cout << "M1Jet_Pt = " << M1Jet_Pt << " " ;
    std::cout << "M1Jet_Eta = " << M1Jet_Eta << " " ;
    std::cout << "M1Jet_btag = " << M1Jet_btag << " " ;
    std::cout << "lep_ID = " << lep_ID << " " ;
    std::cout << "lep_Pt = " << lep_Pt << " " ;
    std::cout << "lep_Eta = " << lep_Eta << " " ;
    std::cout << "M1 = " << M1 << " " ;
    std::cout << "dR_qH = " << dR_qH << " " ;
    std::cout << "dR_lb = " << dR_lb << " " ;
    std::cout << "dR_lt = " << dR_lt << " " ;
    std::cout << "dPhi_bMET = " << dPhi_bMET << " " ;
    std::cout << "Met_Pt = " << Met_Pt << " " ;

    std::cout << object->top_tqh->mass() << " " << std::endl;
    std::cout << "score = " << score << std::endl;
  }

  return score;
};
//}}}
//float ANN_LeptonicTopTagger::EvalScore_st(const std::shared_ptr<ANN_Leptonic_single_top> object){{{
inline
float ANN_LeptonicTopTagger::EvalScore_st(const std::shared_ptr<ANN_Leptonic_single_top> object){

  bJet_Pt    = object->b->pt();
  bJet_Eta   = object->b->eta();
  bJet_btag  = object->b->deepcsv();
  lep_ID     = object->l->id();
  lep_Pt     = object->l->pt();
  lep_Eta    = object->l->eta();
  dR_lb      = deltaR(object->l->eta(),object->l->phi(),object->b->eta(),object->b->phi());
  dR_lH      = deltaR(object->l->eta(),object->l->phi(),object->diphoton->eta(),object->diphoton->phi());
  dPhi_bMET = fabs( object->b->phi() - Met_Phi );
  if (dPhi_bMET > TMath::Pi()) dPhi_bMET = 2 * TMath::Pi() - dPhi_bMET;
  Met_Pt     = Met_Pt;

  float score = reader_st->EvaluateMVA("ST_lep_MVA");

  if (debug) {
    std::cout << "bJet_Pt = " << bJet_Pt << " " ;
    std::cout << "bJet_Eta = " << bJet_Eta << " " ;
    std::cout << "bJet_btag = " << bJet_btag << " " ;
    std::cout << "lep_ID = " << lep_ID << " " ;
    std::cout << "lep_Pt = " << lep_Pt << " " ;
    std::cout << "lep_Eta = " << lep_Eta << " " ;
    std::cout << "dR_lb = " << dR_lb << " " ;
    std::cout << "dR_lH = " << dR_lH << " " << std::endl;
    std::cout << "dPhi_bMET = " << dPhi_bMET << " " ;
    std::cout << "Met_Pt = " << Met_Pt << " " ;
    
    std::cout << "score = " << score << std::endl;
  }

  return score;
};
//}}}
}

#endif // _ANN_HADRONIC_TOP_RECO_HELPER_
