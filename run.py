import os
import sys

mbiasxsec = 69200  # mb
CMSSW_VERSION = 'CMSSW_13_2_10'

# The path /eos/user/c/cmsdqm/www/CAF/certification/ also contains other similar JSONs for different eras
jsonfile = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'
# Alternative 2022 JSON: /eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json

pileupJSON = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23/PileUp/BCD/pileup_JSON.txt'
# Alternative 2022 pileup JSON: /eos/user/c/cmsdqm/www/CAF/certification/Collisions22/PileUp/BCDEFG/pileup_JSON.txt

trigger_list = []
with open('trigger_list.txt') as f:
    trigger_list = f.readlines()
    trigger_list = [x.strip() for x in trigger_list]

for i in range(len(trigger_list)):
    trigger_list[i] = trigger_list[i].strip()

# Check that the directories exist
if not os.path.exists('csvs'):
    os.makedirs('csvs')
if not os.path.exists('rootfiles'):
    os.makedirs('rootfiles')
if not os.path.exists('rootfiles/pileup'):
    os.makedirs('rootfiles/pileup')
        
if not os.path.exists(CMSSW_VERSION):
    os.system(f'cmsrel {CMSSW_VERSION}')

for trigger in trigger_list:
    command = f'''
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env    
echo "Processing {trigger}"
brilcalc lumi --byls --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json --minBiasXsec {mbiasxsec} -u /fb --hltpath "{trigger}_v*" -i {jsonfile} -o csvs/{trigger}.csv
'''
    os.system(command)
    
    # Reset the environment from brilws to CMSSW
    # Notice --runperiod Run2 is used for 2016-2023
    # A ~bug in CMSSW, see source code
    # https://github.com/cms-sw/cmssw/blob/a33c53afbb1049c261c178be6b6d05e32a30f6d2/RecoLuminosity/LumiDB/python/csvLumibyLSParser.py#L51
    command = f'''
    echo "Calculating pileup for {trigger}"
cd {CMSSW_VERSION}/src
cmsenv
cd -
pileupReCalc_HLTpaths.py -i csvs/{trigger}.csv --inputLumiJSON {pileupJSON} -o csvs/{trigger}_pileup.txt --runperiod Run2
pileupCalc.py -i {jsonfile} --inputLumiJSON csvs/{trigger}_pileup.txt --calcMode true --minBiasXsec {mbiasxsec} --maxPileupBin 120 --numPileupBins 120 rootfiles/pileup/{trigger}_pileup.root
'''
    os.system(command)
    print(f'Finished processing {trigger}')
