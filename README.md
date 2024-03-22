# PU_reweighting
Scripts for creating PU reweighting for CMS MC.

# Setup
* Include all the triggers you'd like to reweight in `trigger_list.txt`
* In `run.py` check that the golden JSON and PU JSON match the data era that you want to generate the PU for. Also check the min bias xsec and CMSSW version (newer should work even for older runs).
* Include the MC files which you would like to reweight in mcfiles.txt. This can be a local or an xrootd path (xrootd requires grid certificates). If local files, change is_local=True in `create_weights.py`.

# Running
* Connect to lxplus, preferably lxplus8
* `python3 run.py`
* Source an LCG for creating weights: `source /cvmfs/sft.cern.ch/lcg/views/LCG_104a/x86_64-centos8-gcc11-opt/setup.sh`
* Create weights with `python3 create_weights.py`. Alternatively create your own MC PU profile and proceed as in `create_weights.py`
* There's a rough example in `reweighting_example.py` which requires to run the process for trigger HLT_DiPFJetAve320

# TODO
* At the moment it's not clear how to reweight cases with multiple triggers, for example if HLT_PFJet80 and HLT_DiPFJetAve40 have both triggered.