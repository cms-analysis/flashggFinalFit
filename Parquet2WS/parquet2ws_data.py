import argparse
import os
import json
import re
import glob

import pyarrow.parquet as pq
import pandas as pd

from commonTools import *
from commonObjects import *
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-dir", required=True, type=str, help='Path to input directory')
parser.add_argument("-e", "--era", required=True, type=str, help='Era to process. If merge, merge across eras')
parser.add_argument("-c", "--config", required=True, type=str, help='Config file')
parser.add_argument("--save-merged-parquet", default=False, action="store_true", help='Save merged parquet file')
args = parser.parse_args()

# Load config
with open(args.config, "r") as jf:
    config = json.load(jf)

# Extract files and loop over
if args.era == 'merged':
    list_of_files = glob.glob(f"{args.input_dir}/*/events__Data.parquet")
else:
    list_of_files = [f"{args.input_dir}/{args.era}/events__Data.parquet"]

df_list = []

for i, input_file in enumerate(list_of_files):

    # Load parquet file
    f = pq.ParquetFile(input_file).read()
    df = f.to_pandas()
    df_list.append(df)

# Concatenate dataframes
merged_df = pd.concat(df_list, ignore_index=True)

# Print number of events in category
print(" --> Number of data events in categories...")
print(merged_df['category'].value_counts())

# Extract categories
cats = list(merged_df['category'].unique())
if 'cats_to_drop' in config:
    cats = [cat for cat in cats if cat not in config['cats_to_drop']]

# Define output_file
if args.era == 'merged':
    output_path = f'{args.input_dir}/merged'
    os.makedirs(output_path, exist_ok=True)
    output_file = f'{output_path}/allData.root'
else:
    output_file = f'{args.input_dir}/{args.era}/allData_{args.era}.root'

f_out = ROOT.TFile(output_file, "RECREATE")
f_out_dir = f_out.mkdir(inputWSName__.split("/")[0])
f_out_dir.cd()

# Build workspace
ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])

# Add variables to workspace
vars_to_add = [var for var in config['main_vars'] if var not in ['dZ', 'weight']]

list_of_vars = add_vars_to_workspace(ws, config['main_vars'])

# Loop over categories
for cat in cats:

    # Mask events in cat
    mask = (merged_df['category'] == cat)

    # Make RooArgSet
    aset = make_argset(ws, vars_to_add)

    # Build RooDataSet
    d_name = f"Data__{sqrts__}__{cat}"
    d = ROOT.RooDataSet.from_pandas(merged_df[mask], aset, name=d_name, title=d_name)

    # Add to workspace
    getattr(ws, 'import')(d)

# Write ws to file
ws.Write()

# Close file and delete workspace from heap
f_out.Close()

# Save merged parquet
if args.save_merged_parquet:
    if args.era == 'merged':
        output_parquet_file = f'{output_path}/events__Data.parquet'
        merged_df.to_parquet(output_parquet_file, index=False)
