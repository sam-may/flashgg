/***************************************/
/* sweepRoot                           */
/* Sweep bad root files under the rug! */
/*                                     */
/* Author: Jacob Ribnik                */
/*         jribnik@cern.ch             */
/***************************************/

#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TObject.h"
#include "TH1F.h"

void usage() {
   std::cout << "Usage: sweepRoot [-b] [-g] [-x] [-r] [-d] [-o TObject::GetName()] file1 [file2]..." << std::endl;
   std::cout << std::endl;
   std::cout << "    -b        print list of bad files" << std::endl;
   std::cout << "    -g        print list of good files" << std::endl;
   std::cout << "    -x        move bad files" << std::endl;
   std::cout << "    -r        prefix rfio" << std::endl;
   std::cout << "    -d        prefix dcache" << std::endl;
   std::cout << "    -o        check for TObject of given name" << std::endl;
   std::cout << "    -t        check for TTree of given name" << std::endl;
   std::cout << std::endl;
   exit(1);
}

void move(std::string& target) {
   std::string cmd = "mv ";
   cmd += target;
   target += ".bad";
   cmd += " ";
   cmd += target;
   system(cmd.c_str());
}

int main(int argc, char** argv) {
   std::vector<std::string> printbad;
   std::vector<std::string> printgood;
   int nbad = 0;

   /**************************/
   /* command line arguments */
   /**************************/
   bool doPrintBad  = false;
   bool doPrintGood = false;
   bool doMove      = false;
   bool useRfio     = false;
   bool useDcache   = false;
   std::string name = "";
   std::string tree_name = "";

   int shift = 1;
   if (argc > 1) {
      std::string tmp;
      for (int it = 1; it < argc; it++) {
         tmp = std::string(argv[it]);
         // print list of bad files
         if (tmp == "-b") {
            doPrintBad = true;
            ++shift;
            continue;
         }
         // print list of good files
         if (tmp == "-g") {
            doPrintGood = true;
            ++shift;
            continue;
         }
         // move bad files
         if (tmp == "-x") {
            doMove = true;
            ++shift;
            continue;
         }
         // check for TObject of given name
         if (tmp == "-o") {
            if (it == argc-1) usage();
            name = std::string(argv[it+1]);
            shift += 2;
         }
         // check for TTree of given name
         if (tmp == "-t") {
            if (it == argc-1) usage();
            tree_name = std::string(argv[it+1]);
            shift += 2;
         }
      }
      if (argc <= shift) usage();
      if (useRfio && useDcache) {
         std::cout << "rfio and dcache?  Make up your mind!" << std::endl;
         usage();
      }
   }  else usage();
   //std::cout << "Checking for TObject named: " << name << std::endl;
   std::cout << "sweepRooting " << argc-shift << " files" << std::endl;

   for (int it = shift; it < argc; it++) {
      std::cout << "\rsweepRooted  " << it-shift + 1 << " files";
      std::cout.flush();
      //std::cout << "File " << argv[it] << " is... ";
      std::string target(argv[it]);

      /**************/
      /* check file */
      /**************/
      TFile* f = 0;
      char fname[200];
      strcpy(fname, argv[it]);

      f = TFile::Open(fname, "READ");

      if (! f || f->IsZombie()) {
         if (doPrintBad) printbad.push_back(target);
         ++nbad;
         continue;
      }

      /****************/
      /* check object */
      /****************/
      if (name != "") {
         TObject* obj = f->Get(name.c_str());
         if (! obj || obj->IsZombie()) {
            //std::cout << "bad!" << std::endl;
            if (doMove) move(target);
            if (doPrintBad) printbad.push_back(target);
            ++nbad;
            continue;
         }
      }

      /****************/
      /* check tree */
      /****************/
      if (tree_name != "") {
          TTree* tree = (TTree*)f->Get(tree_name.c_str());
          int nEntries = tree->GetEntriesFast();
          bool isBad = false;
          for (int idx = 0; idx < nEntries; idx++) {
              if (tree->GetEntry(idx,1) < 0) {
                  ++nbad;
                  if (doPrintBad) printbad.push_back(target);
                  isBad = true;
                  break;
              }
          }
          if(isBad)
              continue;
      }
      
      //std::cout << "good!" << std::endl;
      if (doPrintGood) printgood.push_back(target);
      f->Close();
   }

   std::cout << std::endl;
   std::cout << std::endl;
   std::cout << "SUMMARY: " << nbad << " bad, " << argc-shift-nbad << " good" << std::endl;
   if (! printbad.empty()) {
       for (unsigned int i = 0; i < printbad.size(); i++)
           std::cout << "BAD FILE: " << printbad.at(i) << std::endl;
   }
   if (! printgood.empty()) {
       for (unsigned int i = 0; i < printgood.size(); i++)
           std::cout << "GOOD FILE: " << printgood.at(i) << std::endl;
   }

   return nbad;
}
