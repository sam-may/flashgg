#ifndef _TOP_RECO_HELPER_H_
#define _TOP_RECO_HELPER_H_

#include <vector>
#include <TLorentzVector.h>
#include "flashgg/Taggers/interface/covMatrix.h"

using namespace std;

//--------------------------------------------------//
// quadratic equation related
//--------------------------------------------------//
inline vector<int> get_bjet_indices(vector<TLorentzVector> Jets, vector<double> btag_scores)
{
    vector<int> indices;
    //# consider the jet with the highest b-tag score only
    int index_bjet = std::max_element(btag_scores.begin(), btag_scores.end()) - btag_scores.begin();
    indices = {index_bjet};
    return indices;
}
inline double evaluate_neutrino_pz(TLorentzVector lepton, vector<double> met_info)
{
    float met_pt = met_info[0];
    float met_px = met_info[1];
    float met_py = met_info[2];
    float lepton_px = lepton.Px();
    float lepton_py = lepton.Py();
    float lepton_pz = lepton.Pz();
    float lepton_energy = lepton.E();
    float coefficient_factor = ( W_BOSON_MASS*W_BOSON_MASS + 2*lepton_px*met_px + 2*lepton_py*met_py ) / (2.*lepton_energy);
    float coefficient_A = 1. - (lepton_pz*lepton_pz)/(lepton_energy*lepton_energy);
    float coefficient_B = 2.*coefficient_factor*lepton_pz/lepton_energy;
    float coefficient_C = met_pt*met_pt - coefficient_factor*coefficient_factor;
    float coefficient_D = coefficient_B*coefficient_B - 4.*coefficient_A*coefficient_C;
    
    float met_pz_solution_1 = 0.0;
    float met_pz_solution_2 = 0.0;
    if(coefficient_D < 0){
        met_pz_solution_1 = coefficient_B / (2.*coefficient_A);
        met_pz_solution_2 = coefficient_B / (2.*coefficient_A);
    } else{
        met_pz_solution_1 = (coefficient_B + TMath::Sqrt(coefficient_D))/(2.*coefficient_A);
        met_pz_solution_2 = (coefficient_B - TMath::Sqrt(coefficient_D))/(2.*coefficient_A);
    }
    //ordering
    float larger_pz  = (abs(met_pz_solution_1) > abs(met_pz_solution_2) ) ? met_pz_solution_1 : met_pz_solution_2;
    float smaller_pz = (abs(met_pz_solution_1) < abs(met_pz_solution_2) ) ? met_pz_solution_1 : met_pz_solution_2;
    met_pz_solution_1 = larger_pz;
    met_pz_solution_2 = smaller_pz;
    return met_pz_solution_2;
}
inline TLorentzVector derive_reco_neutrino(TLorentzVector lepton, vector<double> met_info)
{
    double neutrino_pz = evaluate_neutrino_pz(lepton, met_info);
    double met_pt = met_info[0];
    double met_px = met_info[1];
    double met_py = met_info[2];
    double neutrino_energy = TMath::Sqrt(met_pt*met_pt + neutrino_pz*neutrino_pz);
    TLorentzVector reco_neutrino;
    reco_neutrino.SetPxPyPzE( met_px, met_py, neutrino_pz, neutrino_energy );
    return reco_neutrino;
}
inline TLorentzVector derive_reco_wboson(TLorentzVector lepton, TLorentzVector reco_neutrino)
{
    TLorentzVector reco_wboson = reco_neutrino + lepton;
    return reco_wboson;
}
inline TLorentzVector derive_reco_tbw(TLorentzVector reco_wboson, TLorentzVector bjet)
{
    TLorentzVector reco_tbw = reco_wboson + bjet;
    return reco_tbw;
}
inline int get_q_index_min_chi2(std::vector<TLorentzVector> Jets, int index_bjet, TLorentzVector diphoton)
{
    std::vector<int> indices;
    std::vector<double> top_fcnh_chi2;
    for(std::size_t i=0; i!=Jets.size(); ++i){
        if((int)i==index_bjet) continue; //skip the selected jets for bjet
        TLorentzVector top_fcnh_tmp = diphoton + Jets[i];
        double chi2 = (top_fcnh_tmp.M() - TOP_QUARK_MASS) * (top_fcnh_tmp.M() - TOP_QUARK_MASS);
        indices.push_back(i);
        top_fcnh_chi2.push_back(chi2);
    }
    int min_index =  std::min_element(top_fcnh_chi2.begin(), top_fcnh_chi2.end()) - top_fcnh_chi2.begin();
    //double min    = *std::min_element(top_fcnh_chi2.begin(), top_fcnh_chi2.end());
    int result = Jets.size() > 1 ? indices[min_index] : -1;
    return result;
}

//--------------------------------------------------//
// chi-2 related
//--------------------------------------------------//
//chi-2 with 3x3 covariance matrix
inline std::vector<int> get_bjjq_indices_chi2_3x3(std::vector<TLorentzVector> Jets, int index_bjet, TLorentzVector diphoton, double &chi2_min)
{
    // 1. pick up 3 jets
    // 2. q-jj three combinations 
    int index_tqh_qjet = -1;
    std::vector<int> index_wjets(2);
    TLorentzVector wjets[2], tqh_qjet;
    TLorentzVector w_boson, sm_top, fcnc_top; 
    TLorentzVector bjet = Jets[index_bjet];
    std::size_t num_jets = Jets.size();
    for(std::size_t i=0; i!=num_jets; ++i){
        if((int)i==index_bjet) continue;//bypass bjet
        for(std::size_t j=i+1; j!=num_jets; ++j){
            if((int)j==index_bjet) continue;//bypass bjet
            for(std::size_t k=j+1; k!=num_jets; ++k){
                if((int)k==index_bjet) continue;//bypass bjet
                //--- combinations ---//
                TLorentzVector jets_chosen[3];
                jets_chosen[0] = Jets[i];
                jets_chosen[1] = Jets[j];
                jets_chosen[2] = Jets[k];
                TLorentzVector tqh_q_chosen[3];
                tqh_q_chosen[0] = jets_chosen[0];
                tqh_q_chosen[1] = jets_chosen[1];
                tqh_q_chosen[2] = jets_chosen[2];
                TLorentzVector w_candidate[3];
                w_candidate[0] = jets_chosen[1] + jets_chosen[2];
                w_candidate[1] = jets_chosen[0] + jets_chosen[2];
                w_candidate[2] = jets_chosen[0] + jets_chosen[1];
                TLorentzVector top_candidate[3];
                TLorentzVector fcnc_top_candidate[3];
                //--- calculation ---//
                std::vector<double> chi2;
                double w_mass[3], t_mass[3], fcnc_top_mass[3];
                for(int x = 0; x<3; ++x){
                    w_mass[x] =  w_candidate[x].M();
                    top_candidate[x] = w_candidate[x] + bjet;
                    t_mass[x] =  top_candidate[x].M();
                    fcnc_top_candidate[x] = tqh_q_chosen[x] + diphoton;
                    fcnc_top_mass[x] = fcnc_top_candidate[x].M();
                    chi2.push_back( Chi2_calculator_improved(w_mass[x], t_mass[x], fcnc_top_mass[x]) );
                }
                //--- sorting ---//
                int smallest_chi2_index = std::min_element(chi2.begin(),chi2.end()) - chi2.begin();
                double smallest_chi2 = *std::min_element(chi2.begin(),chi2.end());
                if(smallest_chi2 < chi2_min){
                    if(smallest_chi2_index == 0){
                        tqh_qjet = tqh_q_chosen[0];
                        wjets[0] = jets_chosen[1];
                        wjets[1] = jets_chosen[2];
                        index_tqh_qjet = i;
                        index_wjets[0] = j;
                        index_wjets[1] = k;
                    } else if(smallest_chi2_index == 1){
                        tqh_qjet = tqh_q_chosen[1];
                        wjets[0] = jets_chosen[0];
                        wjets[1] = jets_chosen[2];
                        index_tqh_qjet = j;
                        index_wjets[0] = i;
                        index_wjets[1] = k;
                    } else{
                        tqh_qjet = tqh_q_chosen[2];
                        wjets[0] = jets_chosen[0];
                        wjets[1] = jets_chosen[1];
                        index_tqh_qjet = k;
                        index_wjets[0] = i;
                        index_wjets[1] = j;
                    }
                    chi2_min = smallest_chi2;
                }
            }
        }
    }//end of looping jets
    w_boson  = wjets[0] + wjets[1];
    sm_top   = w_boson + bjet;
    fcnc_top = tqh_qjet + diphoton;
    std::vector<int> indices = {index_bjet, index_wjets[0], index_wjets[1], index_tqh_qjet};
    return indices;
}
inline std::vector<int> get_bjjq_indices_min_chi2_3x3(std::vector<TLorentzVector> Jets, std::vector<int> indices_bjet, TLorentzVector diphoton)
{
    vector<double> vec_chi2;
    vector<vector<int>> vec_indices_jet;
    for(std::size_t i=0; i!=indices_bjet.size(); ++i){
        double chi2_min = 99999;
        std::vector<int> index_jet_chi2 = get_bjjq_indices_chi2_3x3(Jets, indices_bjet[i], diphoton, chi2_min); // indices of b j j q
        vec_chi2.push_back(chi2_min);
        vec_indices_jet.push_back(index_jet_chi2);
    }
    int min_index =  std::min_element(vec_chi2.begin(), vec_chi2.end()) - vec_chi2.begin();
    double min    = *std::min_element(vec_chi2.begin(), vec_chi2.end());
    return vec_indices_jet[min_index];
}

//chi-2 with 2x2 covariance matrix
inline int get_q_index_min_chi2(std::vector<TLorentzVector> Jets, std::vector<int> indices_bjj, TLorentzVector diphoton)
{
    std::vector<int> indices;
    std::vector<double> top_fcnh_chi2;
    for(std::size_t i=0; i!=Jets.size(); ++i){
        if((int)i==indices_bjj[0] || (int)i==indices_bjj[1] || (int)i==indices_bjj[2]) continue; //skip the selected jets for bjj
        TLorentzVector top_fcnh_tmp = diphoton + Jets[i];
        double chi2 = (top_fcnh_tmp.M() - TOP_QUARK_MASS) * (top_fcnh_tmp.M() - TOP_QUARK_MASS);
        indices.push_back(i);
        top_fcnh_chi2.push_back(chi2);
    }
    int min_index =  std::min_element(top_fcnh_chi2.begin(), top_fcnh_chi2.end()) - top_fcnh_chi2.begin();
    double min    = *std::min_element(top_fcnh_chi2.begin(), top_fcnh_chi2.end());
    return indices[min_index];
}
inline std::vector<int> get_indices_chi2(std::vector<TLorentzVector> Jets, int index_bjet, double &chi2_min, bool is_chi2_modified)
{
    std::vector<int> indices_selected_jet(3, -999);
    indices_selected_jet[0] = index_bjet;
    TLorentzVector bjet = Jets[index_bjet];
    std::size_t num_jets = Jets.size();
    for(std::size_t i=0; i<num_jets; ++i){
        if((int)i==index_bjet) continue;//bypass bjet
        for(std::size_t j=i+1; j<num_jets; ++j){
            if((int)j==index_bjet) continue;//bypass bjet
            TLorentzVector w_candidate = Jets[i] + Jets[j];
            double w_mass = w_candidate.M();
            TLorentzVector top_candidate = w_candidate + bjet;
            double t_mass = top_candidate.M();
            double chi2 = !is_chi2_modified ? Chi2_calculator_simple(w_mass, t_mass) : Chi2_calculator_modified(w_mass, t_mass);
            if(chi2 < chi2_min){
                indices_selected_jet[1] = i;
                indices_selected_jet[2] = j;
                chi2_min = chi2;
            }
        }
    }//end of looping jets
    return indices_selected_jet; //indices of b j j
}
inline vector<int> get_bjj_indices_min_chi2(std::vector<TLorentzVector> Jets, std::vector<int> indices_bjet, bool is_chi2_modified)
{
    vector<double> vec_chi2;
    vector<vector<int>> vec_indices_jet;
    for(std::size_t i=0; i!=indices_bjet.size(); ++i){
        double chi2_min = 99999;
        std::vector<int> index_jet_chi2 = get_indices_chi2(Jets, indices_bjet[i], chi2_min, is_chi2_modified); // indices of b j j
        vec_chi2.push_back(chi2_min);
        vec_indices_jet.push_back(index_jet_chi2);
    }
    int min_index =  std::min_element(vec_chi2.begin(), vec_chi2.end()) - vec_chi2.begin();
    double min    = *std::min_element(vec_chi2.begin(), vec_chi2.end());
    return vec_indices_jet[min_index];
}
inline vector<int> get_bjjq_indices_min_chi2(std::vector<TLorentzVector> Jets, std::vector<int> indices_bjet, TLorentzVector diphoton, bool is_chi2_modified)
{
    std::vector<int> indices = get_bjj_indices_min_chi2(Jets, indices_bjet, is_chi2_modified);
    int index_q = get_q_index_min_chi2(Jets, indices, diphoton);
    indices.push_back(index_q);
    return indices;
}
inline double calculate_CvsL(double c_disciminant, double udsg_discriminant)
{
    double CvsL = c_disciminant / (c_disciminant + udsg_discriminant);
    return CvsL;
}

inline double calculate_CvsB(double c_disciminant, double b_discriminant, double bb_discriminant)
{
    double CvsB = c_disciminant / (c_disciminant + b_discriminant + bb_discriminant);
    return CvsB;
}

#endif
