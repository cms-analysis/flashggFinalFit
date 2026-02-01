import glob

import argparse
from collections import defaultdict

# 1. Load all root files
parser = argparse.ArgumentParser()


parser.add_argument('--path')

args=parser.parse_args()


file_list = glob.glob(f"{args.path}/*.root")  # adjust path as needed

# 2. Map process → set of categories
proc_to_cats = defaultdict(set)

for filepath in file_list:
    filename = filepath.split("/")[-1]
    for er in ['preEE','postEE','preBPix','postBPix']:
        if er in filepath:
            era=er
    try:
        # Extract process name between `preEE_` and `_preEE_RECO`
        process = filename.split(f"{era}_")[1].split(f"_{era}_RECO")[0]
        
        # Extract category name after `RECO_` and before `.root`
        category = filename.split("RECO_")[1].replace(".root", "")
        
        proc_to_cats[process].add(category)

    except IndexError:
        print(f"Filename doesn't match expected format: {filename}")

# 3. Check which processes are missing categories
for proc, cats in proc_to_cats.items():
    if len(cats) != 20:
        print(f"❌ Process {proc} has only {len(cats)} categories")
    else:
        print(f"✅ Process {proc} has 20 categories")