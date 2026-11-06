import pandas as pd
import glob
import argparse
import os

import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

from XSBR import xsbr
from commonObjects import *

parser = argparse.ArgumentParser()
parser.add_argument("--input-dir", type=str, required=True, help="Path to the input directory containing parquet files")
parser.add_argument("--years", type=str, required=True, help="Comma separated list of years to process")
parser.add_argument("--background-cats", type=str, default='RECO_DY,RECO_GG+DDQCDGJets,RECO_Top,RECO_VV+VG', required=False, help="Comma separated list of background categories to drop from the dataframe")
parser.add_argument("--output-csv", type=str, default="signal_yields.csv", required=False, help="Output CSV file name (default: signal_yields.csv)")
args = parser.parse_args()

# Folder structure: input_dir/year/*.parquet
# Loop over parquet files and store sumw from each (proc, cat, year) in a dataframe
data = pd.DataFrame(columns=["proc", "cat", "year", "sumw", "n_exp"])
for year in args.years.split(","):

    parquet_files = glob.glob(os.path.join(args.input_dir, year, "*.parquet"))
    for i, parquet_file in enumerate(parquet_files):

        # Filename: events__{proc}.parquet
        proc = os.path.basename(parquet_file).split("__")[1].split(".")[0]
        print(f"Processing file {i+1}/{len(parquet_files)}: (proc: {proc}, year: {year})")

        df = pd.read_parquet(parquet_file, columns=["category", "weight"])
        for category in df["category"].unique():

            if args.background_cats and category in args.background_cats.split(","):
                continue

            sumw = df[df["category"] == category]["weight"].sum()
            n_exp = xsbr[proc]["factor"] * xsbr['decay']['factor'] * lumiMap[year] * lumiScaleFactor * sumw 
            data = pd.concat([data, pd.DataFrame({"proc": [proc], "cat": [category], "year": [year], "sumw": [sumw], "n_exp": [n_exp]})], ignore_index=True)

# Save the dataframe to a CSV file
output_csv = os.path.join(args.output_csv)
data.to_csv(output_csv, index=False)
