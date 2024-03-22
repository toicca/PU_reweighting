import ROOT
import os

ROOT.gROOT.SetBatch(True)

ROOT.EnableImplicitMT(8)

mc_file_path = "mcfiles.txt"
is_local = False
    
# Load the MC file paths and setup RDF
input_files = []
with open(mc_file_path) as f:
    input_files = f.readlines()
    
if not is_local:
    input_files = ["root://cms-xrd-global.cern.ch/" + file for file in input_files]

chain = ROOT.TChain("Events")
for file in input_files:
    chain.Add(file.strip())

rdf = ROOT.RDataFrame(chain)

ROOT.gInterpreter.Declare('''
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include "TH1D.h"
#include "TFile.h"

TH1D PU_weights;

// Load PU
void load_pileup() {
    TFile *f = TFile::Open("rootfiles/weights/HLT_DiPFJetAve320_weights.root");
    TH1D *h = (TH1D*)f->Get("weights");
    PU_weights = *h;
}

// Load the pileup weights and evaluate the weight for a given number of pileup interactions
double get_pileup_weight(int PU_x) {
    return PU_weights.Interpolate(PU_x);
}
''')

ROOT.load_pileup()

rdf = rdf.Define("pileup_weight", "get_pileup_weight(Pileup_nTrueInt)")
rdf = rdf.Filter("HLT_DiPFJetAve320").Define("weight", "genWeight * pileup_weight")

# Plot jet pt before and after reweighting
h1 = rdf.Histo1D(("jet_pt", "jet_pt", 100, 0, 200), "Jet_pt", "weight")
h2 = rdf.Histo1D(("jet_pt_unweighted", "jet_pt_unweighted", 100, 0, 200), "Jet_pt", "genWeight")

# Draw the histograms
c = ROOT.TCanvas("c", "c", 800, 600)
h1.Draw()
h2.Draw("same plc pmc pfc")
# Logy
c.SetLogy()

c.BuildLegend()
c.SaveAs("plots/jet_pt.png")




