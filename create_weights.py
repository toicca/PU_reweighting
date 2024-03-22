import ROOT
import os

ROOT.gROOT.SetBatch(True)

ROOT.EnableImplicitMT(8)

mc_file_path = "mcfiles.txt"
is_local = False

# Load the trigger list
trigger_list = []
with open('trigger_list.txt') as f:
    trigger_list = f.readlines()
    trigger_list = [x.strip() for x in trigger_list]
    
# Check that the directories exist
if not os.path.exists('rootfiles'):
    os.makedirs('rootfiles')
if not os.path.exists('rootfiles/weights'):
    os.makedirs('rootfiles/weights')
if not os.path.exists('plots'):
    os.makedirs('plots')

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

# Requires ROOT version >= 6.30
# ROOT.RDF.Experimental.AddProgressBar(rdf)

# Loop through triggers
for trigger in trigger_list:
    trig_rdf = rdf.Filter(trigger)
    histo = trig_rdf.Histo1D(("Pileup_nTrueInt", "pileup_mc", 120, 0, 120), "Pileup_nTrueInt", "genWeight")
    histo = histo.GetValue()

    # Get the DT histogram
    dt_file = ROOT.TFile.Open("rootfiles/pileup/" + trigger + "_pileup.root", "READ")
    dt_histo = dt_file.Get("pileup")
    dt_histo.SetDirectory(0)
    dt_histo.SetName("pileup_dt")
    dt_histo.SetTitle("pileup_dt")
    dt_histo.SetLineColor(ROOT.kRed)
    dt_histo.SetMarkerColor(ROOT.kRed)

    
    # Check that the histograms are not empty
    if histo.GetMaximum() == 0 or dt_histo.GetMaximum() == 0:
        print(f"Skipping {trigger} due to empty histograms")
        continue
    
    # Set dt_histo error to 0 and normalize the histograms
    for i in range(1, dt_histo.GetNbinsX() + 1):
        dt_histo.SetBinError(i, 0)
    
    histo.Scale(1 / histo.GetMaximum())
    dt_histo.Scale(1 / dt_histo.GetMaximum())
    
    # Compare the two histograms
    c = ROOT.TCanvas("canv", "canv", 800, 600)
    histo.Draw("hist")
    dt_histo.Draw("SAME")
    c.BuildLegend()
    c.SaveAs("plots/" + trigger + "_pileup_comparison.png")
    
    # Calculate the weights
    weights = histo.Clone()
    
    weights.Divide(dt_histo)
    weights.SetName("weights")
    weights.SetTitle("weights")
    weights.SetDirectory(0)
    dt_file.Close()

    # Save the weights
    weight_file = ROOT.TFile.Open("rootfiles/weights/" + trigger + "_weights.root", "RECREATE")
    weights.Write()
    dt_histo.SetName("dt_pileup")
    dt_histo.SetTitle("dt_pileup")
    dt_histo.Write()
    histo.SetName("mc_pileup")
    histo.SetTitle("mc_pileup")
    histo.Write()
    weight_file.Close()
    