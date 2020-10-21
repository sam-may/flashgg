#ifndef _ANN_HADRONIC_TOP_RECO_HELPER_
#define _ANN_HADRONIC_TOP_RECO_HELPER_

#include "flashgg/Taggers/interface/ANN_self_defined_objects.h"

namespace flashgg {

//class ANN_Hadronic_top_pair {{{
class ANN_Hadronic_top_pair {
public:
  ANN_Hadronic_top_pair(){};
  ANN_Hadronic_top_pair(std::shared_ptr<ANN_rTT_Photon> _leading_photon, std::shared_ptr<ANN_rTT_Photon> _subleading_photon, std::shared_ptr<ANN_rTT_Jet> _b, std::shared_ptr<ANN_rTT_Jet> _j2, std::shared_ptr<ANN_rTT_Jet> _j3, std::shared_ptr<ANN_rTT_Jet> _j4 ){

    leading_photon = _leading_photon;
    subleading_photon = _subleading_photon;
    b = _b;
    j2 = _j2; // q-jet
    if (_j3->pt() > _j4->pt()) { j3 = _j3; j4 = _j4; }
    else { j3 = _j4; j4 = _j3; }

    *diphoton = *(dynamic_cast<ANN_rTT_ptvec*>(leading_photon.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(subleading_photon.get()));
    *wboson = *(dynamic_cast<ANN_rTT_ptvec*>(j3.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(j4.get()));
    *top_tbw = (b!=NULL) ? *wboson + *(dynamic_cast<ANN_rTT_ptvec*>(b.get())) : *wboson;
    *top_tqh = (_j2!=NULL) ? *diphoton + *(dynamic_cast<ANN_rTT_ptvec*>(j2.get())) : *diphoton; // warnning: diphoton info

  }
  std::shared_ptr<ANN_rTT_ptvec> diphoton = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> wboson = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> top_tbw = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> top_tqh = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_Photon> leading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Photon> subleading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Jet> b = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j2 = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j3 = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j4 = nullptr;
  float score = -99;
  int j1idx = -99;
  int j2idx = -99;
  int j3idx = -99;
  int j4idx = -99;
};
//}}}
//class ANN_Hadronic_single_top {{{
class ANN_Hadronic_single_top {
public:
  ANN_Hadronic_single_top(){};
  ANN_Hadronic_single_top(std::shared_ptr<ANN_rTT_Photon> _leading_photon, std::shared_ptr<ANN_rTT_Photon> _subleading_photon, std::shared_ptr<ANN_rTT_Jet> _b, std::shared_ptr<ANN_rTT_Jet> _j2, std::shared_ptr<ANN_rTT_Jet> _j3 ){

    leading_photon = _leading_photon;
    subleading_photon = _subleading_photon;
    b = _b;
    if (_j2->pt() > _j3->pt()) { j2 = _j2; j3 = _j3; }
    else { j2 = _j3; j3 = _j2; }

    *diphoton = *(dynamic_cast<ANN_rTT_ptvec*>(leading_photon.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(subleading_photon.get()));
    *wboson = *(dynamic_cast<ANN_rTT_ptvec*>(j2.get())) + *(dynamic_cast<ANN_rTT_ptvec*>(j3.get()));
    *top_tbw = (b!=NULL) ? *wboson + *(dynamic_cast<ANN_rTT_ptvec*>(b.get())) : *wboson;

  }
  std::shared_ptr<ANN_rTT_ptvec> diphoton = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> wboson = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_ptvec> top_tbw = std::make_shared<ANN_rTT_ptvec>(0,0,0,0);
  std::shared_ptr<ANN_rTT_Photon> leading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Photon> subleading_photon = nullptr;
  std::shared_ptr<ANN_rTT_Jet> b = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j2 = nullptr;
  std::shared_ptr<ANN_rTT_Jet> j3 = nullptr;
  float score = -99;
  int j1idx = -99;
  int j2idx = -99;
  int j3idx = -99;
};
//}}}
//class ANN_HadronicTopTagger {{{
class ANN_HadronicTopTagger {
public:
  ANN_HadronicTopTagger(std::string weight_file_name_01, std::string weight_file_name_02){
    Init_tt(weight_file_name_01);
    Init_st(weight_file_name_02);
  };

  ~ANN_HadronicTopTagger(){
    clear();
  };

  void addJet(float pt,float eta, float phi, float mass, float deepcsv){
    jets.push_back(std::make_shared<ANN_rTT_Jet>(pt,eta,phi,mass,deepcsv));
  };
  
  void addPhoton(float pt,float eta, float phi, float mass, float IDMVA){
    photons.push_back(std::make_shared<ANN_rTT_Photon>(pt,eta,phi,mass, IDMVA));
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

  float EvalScore_tt(const std::shared_ptr<ANN_Hadronic_top_pair>);
  float EvalScore_st(const std::shared_ptr<ANN_Hadronic_single_top>);

  std::shared_ptr<TMVA::Reader> reader_tt = nullptr;
  std::shared_ptr<TMVA::Reader> reader_st = nullptr;

  float bJet_Pt = -99;
  float bJet_Eta = -99;
  float bJet_btag = -99;
  float M1Jet_Pt = -99;
  float M1Jet_Eta = -99;
  float M1Jet_btag = -99;
  float WJet1_Pt = -99;
  float WJet1_Eta = -99;
  float WJet1_btag = -99;
  float WJet2_Pt = -99;
  float WJet2_Eta = -99;
  float WJet2_btag = -99;
  float M1 = -99;
  float M2 = -99;
  float MW = -99;
  float dR_qH = -99;
  float dR_bW = -99;
  float dR_tt = -99;
  float dR_qq = -99;
  float dR_tH = -99;

  bool debug = false;

};
//}}}

//void ANN_HadronicTopTagger::Init_tt(std::string weight_file_name){{{
inline
void ANN_HadronicTopTagger::Init_tt(std::string weight_file_name){

  reader_tt = std::make_shared<TMVA::Reader>( "!Color:!Silent" );

  reader_tt->AddVariable("bJet_Pt", &bJet_Pt);
  reader_tt->AddVariable("bJet_Eta", &bJet_Eta);
  reader_tt->AddVariable("bJet_btag", &bJet_btag);
  reader_tt->AddVariable("M1Jet_Pt", &M1Jet_Pt);
  reader_tt->AddVariable("M1Jet_Eta", &M1Jet_Eta);
  reader_tt->AddVariable("M1Jet_btag", &M1Jet_btag);
  reader_tt->AddVariable("WJet1_Pt", &WJet1_Pt);
  reader_tt->AddVariable("WJet1_Eta", &WJet1_Eta);
  reader_tt->AddVariable("WJet1_btag", &WJet1_btag);
  reader_tt->AddVariable("WJet2_Pt", &WJet2_Pt);
  reader_tt->AddVariable("WJet2_Eta", &WJet2_Eta);
  reader_tt->AddVariable("WJet2_btag", &WJet2_btag);
  reader_tt->AddVariable("M1", &M1);
  reader_tt->AddVariable("M2", &M2);
  reader_tt->AddVariable("MW", &MW);
  reader_tt->AddVariable("dR_qH", &dR_qH);
  reader_tt->AddVariable("dR_bW", &dR_bW);
  reader_tt->AddVariable("dR_tt", &dR_tt);
  reader_tt->AddVariable("dR_qq", &dR_qq);

  reader_tt->BookMVA("TT_had_MVA", weight_file_name);
};
//}}}
//void ANN_HadronicTopTagger::Init_st(std::string weight_file_name){{{
inline
void ANN_HadronicTopTagger::Init_st(std::string weight_file_name){

  reader_st = std::make_shared<TMVA::Reader>( "!Color:!Silent" );

  reader_st->AddVariable("bJet_Pt", &bJet_Pt);
  reader_st->AddVariable("bJet_Eta", &bJet_Eta);
  reader_st->AddVariable("bJet_btag", &bJet_btag);
  reader_st->AddVariable("WJet1_Pt", &WJet1_Pt);
  reader_st->AddVariable("WJet1_Eta", &WJet1_Eta);
  reader_st->AddVariable("WJet1_btag", &WJet1_btag);
  reader_st->AddVariable("WJet2_Pt", &WJet2_Pt);
  reader_st->AddVariable("WJet2_Eta", &WJet2_Eta);
  reader_st->AddVariable("WJet2_btag", &WJet2_btag);
  reader_st->AddVariable("M1", &M1);
  reader_st->AddVariable("MW", &MW);
  reader_st->AddVariable("dR_bW", &dR_bW);
  reader_st->AddVariable("dR_tH", &dR_tH);
  reader_st->AddVariable("dR_qq", &dR_qq);
  
  reader_st->BookMVA("ST_had_MVA", weight_file_name);
};
//}}}
//void ANN_HadronicTopTagger::clear(){{{
inline
void ANN_HadronicTopTagger::clear(){

  jets.clear();
  photons.clear();

  bJet_Pt = -99;
  bJet_Eta = -99;
  bJet_btag = -99;
  M1Jet_Pt = -99;
  M1Jet_Eta = -99;
  M1Jet_btag = -99;
  WJet1_Pt = -99;
  WJet1_Eta = -99;
  WJet1_btag = -99;
  WJet2_Pt = -99;
  WJet2_Eta = -99;
  WJet2_btag = -99;
  M1 = -99;
  M2 = -99;
  MW = -99;
  dR_qH = -99;
  dR_bW = -99;
  dR_tt = -99;
  dR_tH = -99;
  dR_qq = -99;

}
//}}}
//std::vector<float> ANN_HadronicTopTagger::EvalMVA_tt(){{{
inline
std::vector<float> ANN_HadronicTopTagger::EvalMVA_tt(){

  int njets = jets.size();

  std::vector<std::shared_ptr<ANN_Hadronic_top_pair>> allcands;
  for (int i=0; i<njets; ++i) { // b-jet
    for (int j=0; j<njets; ++j) { // q-jet
      if(j == i) continue;
      for (int k=0; k<njets-1; ++k) { // w-jet1
        if(k == i || k == j) continue;
        for (int l=k+1; l<njets-1; ++l) { // w-jet2
          if(l == i || l == j) continue;
	      auto topcand = std::make_shared<ANN_Hadronic_top_pair>(photons[0], photons[1], jets.at(i), jets.at(j), jets.at(k), jets.at(l));
          topcand->score = EvalScore_tt(topcand);
          topcand->j1idx = i;
          topcand->j2idx = j;
          topcand->j3idx = k;
          topcand->j4idx = l;
          allcands.push_back(topcand);
        }
      }
    }
  }

  if (debug) std::cout << "Hadronic EvalScore_tt: njets = " << njets ;

  std::vector<float> output(16,-99);
  if (allcands.size()>0) {
    // note: make sure this return max values
    auto top = *std::min_element(allcands.begin(),allcands.end(),[](const std::shared_ptr<ANN_Hadronic_top_pair> &a, const std::shared_ptr<ANN_Hadronic_top_pair> &b){return a->score > b->score;});
    output.at(0) = top->score; // mvaValue
  }
  if (debug) std::cout << "MVA score: " << output.at(0) << std::endl;
  return output;

};
//}}}
//std::vector<float> ANN_HadronicTopTagger::EvalMVA_st(){{{
inline
std::vector<float> ANN_HadronicTopTagger::EvalMVA_st(){

  int njets = jets.size();

  std::vector<std::shared_ptr<ANN_Hadronic_single_top>> allcands;
  for (int i=0; i<njets; ++i) { // b-jet
    for (int k=0; k<njets-1; ++k) { // w-jet1
      if(k == i) continue;
      for (int l=k+1; l<njets; ++l) { // w-jet2
        if(l == i) continue;
	    auto topcand = std::make_shared<ANN_Hadronic_single_top>(photons[0], photons[1], jets.at(i), jets.at(k), jets.at(l));
        topcand->score = EvalScore_st(topcand);
        topcand->j1idx = i;
        topcand->j2idx = k;
        topcand->j3idx = l;
        allcands.push_back(topcand);
      }
    }
  }

  if (debug) std::cout << "Hadronic EvalScore_st: njets = " << njets ;

  std::vector<float> output(16,-99);
  if (allcands.size()>0) {
    // note: make sure this return max values
    auto top = *std::min_element(allcands.begin(),allcands.end(),[](const std::shared_ptr<ANN_Hadronic_single_top> &a, const std::shared_ptr<ANN_Hadronic_single_top> &b){return a->score > b->score;});
    output.at(0) = top->score; // mvaValue
  }
  if (debug) std::cout << "MVA score: " << output.at(0) << std::endl;
  return output;

};
//}}}

//float ANN_HadronicTopTagger::EvalScore_tt(const std::shared_ptr<ANN_Hadronic_top_pair> object){{{
inline
float ANN_HadronicTopTagger::EvalScore_tt(const std::shared_ptr<ANN_Hadronic_top_pair> object){

  bJet_Pt    = object->b->pt();
  bJet_Eta   = object->b->eta();
  bJet_btag  = object->b->deepcsv();
  WJet1_Pt   = object->j3->pt();
  WJet1_Eta  = object->j3->eta();
  WJet1_btag = object->j3->deepcsv();
  WJet2_Pt   = object->j4->pt();
  WJet2_Eta  = object->j4->eta();
  WJet2_btag = object->j4->deepcsv();
  M1Jet_Pt   = object->j2->pt();
  M1Jet_Eta  = object->j2->eta();
  M1Jet_btag = object->j2->deepcsv();
  M1         = object->top_tqh->mass();
  M2         = object->top_tbw->mass();
  MW         = object->wboson->mass();
  dR_qH      = deltaR(object->j2->eta(),object->j2->phi(),object->diphoton->eta(),object->diphoton->phi());
  dR_bW      = deltaR(object->b->eta(),object->b->phi(),object->wboson->eta(),object->wboson->phi());
  dR_tt      = deltaR(object->top_tbw->eta(),object->top_tbw->phi(),object->top_tqh->eta(),object->top_tqh->phi());
  dR_qq      = deltaR(object->j3->eta(),object->j3->phi(),object->j4->eta(),object->j4->phi());

  float score = reader_tt->EvaluateMVA("TT_had_MVA");

  if (debug) {
    std::cout << "bJet_Pt = " << bJet_Pt << " " ;
    std::cout << "bJet_Eta = " << bJet_Eta << " " ;
    std::cout << "bJet_btag = " << bJet_btag << " " ;
    std::cout << "WJet1_Pt = " << WJet1_Pt << " " ;
    std::cout << "WJet1_Eta = " << WJet1_Eta << " " ;
    std::cout << "WJet1_btag = " << WJet1_btag << " " ;
    std::cout << "WJet2_Pt = " << WJet2_Pt << " " ;
    std::cout << "WJet2_Eta = " << WJet2_Eta << " " ;
    std::cout << "WJet2_btag = " << WJet2_btag << " " ;
    std::cout << "M1Jet_Pt = " << M1Jet_Pt << " " ;
    std::cout << "M1Jet_Eta = " << M1Jet_Eta << " " ;
    std::cout << "M1Jet_btag = " << M1Jet_btag << " " ;
    std::cout << "M1 = " << M1 << " " ;
    std::cout << "M2 = " << M2 << " " ;
    std::cout << "MW = " << MW << " " ;
    std::cout << "dR_qH = " << dR_qH << " " ;
    std::cout << "dR_bW = " << dR_bW << " " ;
    std::cout << "dR_tt = " << dR_tt << " " ;
    std::cout << "dR_qq = " << dR_qq << " " ;

    std::cout << object->top_tbw->mass() << " " << std::endl;
    std::cout << "score = " << score << std::endl;
  }

  return score;
};
//}}}
//float ANN_HadronicTopTagger::EvalScore_st(const std::shared_ptr<ANN_Hadronic_single_top> object){{{
inline
float ANN_HadronicTopTagger::EvalScore_st(const std::shared_ptr<ANN_Hadronic_single_top> object){

  bJet_Pt    = object->b->pt();
  bJet_Eta   = object->b->eta();
  bJet_btag  = object->b->deepcsv();
  WJet1_Pt   = object->j2->pt();
  WJet1_Eta  = object->j2->eta();
  WJet1_btag = object->j2->deepcsv();
  WJet2_Pt   = object->j3->pt();
  WJet2_Eta  = object->j3->eta();
  WJet2_btag = object->j3->deepcsv();
  M1         = object->top_tbw->mass(); // in single top had, M1 represent M_tbw
  MW         = object->wboson->mass();
  dR_bW      = deltaR(object->b->eta(),object->b->phi(),object->wboson->eta(),object->wboson->phi());
  dR_tH      = deltaR(object->top_tbw->eta(),object->top_tbw->phi(),object->diphoton->eta(),object->diphoton->phi());
  dR_qq      = deltaR(object->j2->eta(),object->j2->phi(),object->j3->eta(),object->j3->phi());

  float score = reader_st->EvaluateMVA("ST_had_MVA");

  if (debug) {
    std::cout << "bJet_Pt = " << bJet_Pt << " " ;
    std::cout << "bJet_Eta = " << bJet_Eta << " " ;
    std::cout << "bJet_btag = " << bJet_btag << " " ;
    std::cout << "WJet1_Pt = " << WJet1_Pt << " " ;
    std::cout << "WJet1_Eta = " << WJet1_Eta << " " ;
    std::cout << "WJet1_btag = " << WJet1_btag << " " ;
    std::cout << "WJet2_Pt = " << WJet2_Pt << " " ;
    std::cout << "WJet2_Eta = " << WJet2_Eta << " " ;
    std::cout << "WJet2_btag = " << WJet2_btag << " " ;
    std::cout << "M1 = " << M1 << " " ;
    std::cout << "MW = " << MW << " " ;
    std::cout << "dR_bW = " << dR_bW << " " ;
    std::cout << "dR_tH = " << dR_tH << " " ;
    std::cout << "dR_qq = " << dR_qq << " " ;
    
    std::cout << object->top_tbw->mass() << " " << std::endl;
    std::cout << "score = " << score << std::endl;
  }

  return score;
};
//}}}
}

#endif // _ANN_HADRONIC_TOP_RECO_HELPER_
