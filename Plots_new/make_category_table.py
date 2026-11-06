import pandas as pd
import numpy as np
import argparse
import os
import json
import ROOT

# Translate procs
def load_translations(json_file):
    with open(json_file, 'r') as f:
        translations = json.load(f)
    return translations

def translate(x, translation_dict):
    return translation_dict[x] if x in translation_dict else x

cats_ordered = ['RECO_GG2H_0J_PTH_0_10_res0', 'RECO_GG2H_0J_PTH_0_10_res1', 'RECO_GG2H_0J_PTH_0_10_res2', 'RECO_GG2H_0J_PTH_GT10_res0', 'RECO_GG2H_0J_PTH_GT10_res1', 'RECO_GG2H_0J_PTH_GT10_res2', 'RECO_GG2H_1J_PTH_0_60_res0', 'RECO_GG2H_1J_PTH_0_60_res1', 'RECO_GG2H_1J_PTH_0_60_res2',  'RECO_GG2H_1J_PTH_60_120_res0', 'RECO_GG2H_1J_PTH_60_120_res1', 'RECO_GG2H_1J_PTH_60_120_res2', 'RECO_GG2H_1J_PTH_120_200_res0', 'RECO_GG2H_1J_PTH_120_200_res1', 'RECO_GG2H_1J_PTH_120_200_res2','RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res2', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res0', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res1', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res2', 'RECO_GG2H_PTH_200_300_res0', 'RECO_GG2H_PTH_200_300_res1', 'RECO_GG2H_PTH_200_300_res2', 'RECO_GG2H_PTH_300_450_res0', 'RECO_GG2H_PTH_300_450_res1', 'RECO_GG2H_PTH_450_650', 'RECO_GG2H_PTH_GT650', 'RECO_QQ2HQQ_REST_res0', 'RECO_QQ2HQQ_REST_res1', 'RECO_QQ2HQQ_REST_res2', 'RECO_QQ2HQQ_GE2J_MJJ_60_120', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res1',  'RECO_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200', 'RECO_WH2HLNU_PTV_0_75', 'RECO_WH2HLNU_PTV_75_150', 'RECO_WH2HLNU_PTV_GT150', 'RECO_ZH2HLL_PTV_0_150_ZH_ll', 'RECO_ZH2HLL_PTV_GT150_ZH_ll', 'RECO_ZH2HLL_PTV_0_150_ZH_nunu', 'RECO_ZH2HLL_PTV_GT150_ZH_nunu', 'RECO_TTH_PTH_0_60_ttH_had_res0', 'RECO_TTH_PTH_0_60_ttH_had_res1', 'RECO_TTH_PTH_60_120_ttH_had_res0', 'RECO_TTH_PTH_60_120_ttH_had_res1', 'RECO_TTH_PTH_120_200_ttH_had', 'RECO_TTH_PTH_200_300_ttH_had', 'RECO_TTH_PTH_GT300_ttH_had', 'RECO_TTH_PTH_0_60_ttH_semilep', 'RECO_TTH_PTH_60_120_ttH_semilep', 'RECO_TTH_PTH_120_200_ttH_semilep', 'RECO_TTH_PTH_200_300_ttH_semilep', 'RECO_TTH_PTH_GT300_ttH_semilep', 'RECO_TTH_PTH_0_60_ttH_lep',   'RECO_TTH_PTH_60_120_ttH_lep',   'RECO_TTH_PTH_120_200_ttH_lep',   'RECO_TTH_PTH_200_300_ttH_lep',    'RECO_TTH_PTH_GT300_ttH_lep', 'RECO_TH_tH_had_res0', 'RECO_TH_tH_had_res1', 'RECO_TH_tH_lep']

parser = argparse.ArgumentParser()
parser.add_argument("--input-csv", type=str, required=True, help="Path to the input csv storing yields")
parser.add_argument("--process-map", type=str, required=True, help="Path to json file storing process map")
parser.add_argument("--targeted-stxs-regions", type=str, required=True, help="Path to json file storing targeted STXS regions")
parser.add_argument('--translate-procs-json', dest='translate_procs_json', default=None, help="Path to json file storing process translation map")
parser.add_argument('--translate-cats-json', dest='translate_cats_json', default=None, help="Path to json file storing category translation map")
parser.add_argument("--path-to-effsigma", type=str, required=True, help="Path to the effsigma json files")
parser.add_argument("--path-to-multipdf", type=str, required=True, help="Path to multipdf ROOT files")
parser.add_argument('--ext', dest='ext', default="", help="Extension for the plot file name")
args = parser.parse_args()

translate_procs = {} if args.translate_procs_json is None else load_translations(args.translate_procs_json)
translate_cats = {} if args.translate_cats_json is None else load_translations(args.translate_cats_json)

# Load the yields from the CSV file
df = pd.read_csv(args.input_csv)

# Load the process mapping from the JSON file
with open(args.process_map, 'r') as f:
    process_map = json.load(f)


# Apply process mapping to add new column 'proc_mapped' to the dataframe
df['proc_mapped'] = df['proc'].map(process_map)

# Load targeted STXS region from the JSON file
with open(args.targeted_stxs_regions, 'r') as f:
    targeted_stxs_regions = json.load(f)

# Define a new column (stage0) based on the "{stage0}_" part of the 'proc_mapped' column
df['stage0'] = df['proc_mapped'].apply(lambda x: x.split('_')[0] if isinstance(x, str) else x)
stage0_regions = ['GG2H', 'BBH', 'QQ2HQQ', 'WH2HLNU', 'ZH2HLL', 'TTH', 'TH']
translate_stage0 = {stage0: translate(stage0, translate_procs) for stage0 in stage0_regions}

# Create new table with one row per category
# First column: category
# Second column: sum of n_exp for each category
# Third column: fraction of sum of n_exp from targeted STXS region(s)
# Next columns are the fraction of sum of n_exp from each STXS region (stage0) for that category
# Next column: effsigma for that category (from json file)
# Next column: background per GeV for that category (from multipdf ROOT file)
# Next column: F68 for that category where F68 = S/S+B in the range MH +- effsigma
summary_df = pd.DataFrame(columns=['Analysis category', 'Total', 'Target STXS region(s)'] + [translate_stage0[stage0] for stage0 in stage0_regions] + ['$\\sigma_{eff}$ (GeV)'] + ['Bkg (GeV$^{-1}$)'] + ['$F_{68}$'])
for cat in cats_ordered:
    cat_df = df[df['cat'] == cat]
    total_n_exp = cat_df['n_exp'].sum()
    targeted_n_exp = cat_df[cat_df['proc_mapped']==targeted_stxs_regions[cat]]['n_exp'].sum()
    fraction_targeted = 100*(targeted_n_exp / total_n_exp) if total_n_exp > 0 else 0

    # Create a new row for the category
    new_row = {
        'Analysis category': translate(cat, translate_cats),
        'Total': total_n_exp,
        'Target STXS region(s)': fraction_targeted
    }

    # Add fractions for each STXS region (stage0)
    for stage0 in stage0_regions:
        stage0_n_exp = cat_df[cat_df['stage0'] == stage0]['n_exp'].sum()
        new_row[translate_stage0[stage0]] = 100 * (stage0_n_exp / total_n_exp) if total_n_exp > 0 else 0

    # Load the effsigma values from the JSON file
    effsigma_file = os.path.join(args.path_to_effsigma, f"effSigma_{cat}.json")
    if os.path.exists(effsigma_file):
        with open(effsigma_file, 'r') as f:
            effsigma_data = json.load(f)
        new_row['$\\sigma_{eff}$ (GeV)'] = effsigma_data['combined']
    else:
        new_row['$\\sigma_{eff}$ (GeV)'] = 999

    # Load the background values from the ROOT file
    multipdf_file = os.path.join(args.path_to_multipdf, f"CMS-HGG_multipdf_{cat}.root")
    if os.path.exists(multipdf_file):
        f = ROOT.TFile(multipdf_file)
        w = f.Get("multipdf")
        bpdf = w.pdf(f"CMS_hgg_{cat}_13p6TeV_bkgshape")
        # Take away signal norm 
        bnorm = w.var(f"CMS_hgg_{cat}_13p6TeV_bkgshape_norm").getVal() - total_n_exp
        # Integrate B pdf over range MH +- effsigma
        xvar = w.var("CMS_hgg_mass")
        range_name = f"eff_sigma_{cat}"
        xvar.setRange(range_name, 125.07 - new_row['$\\sigma_{eff}$ (GeV)'], 125.07 + new_row['$\\sigma_{eff}$ (GeV)'])
        b_integral = bpdf.createIntegral(ROOT.RooArgSet(xvar), ROOT.RooArgSet(xvar), range_name).getVal() * bnorm
        b_per_GeV = b_integral / (2 * new_row['$\\sigma_{eff}$ (GeV)']) if new_row['$\\sigma_{eff}$ (GeV)'] > 0 else 999
        new_row['Bkg (GeV$^{-1}$)'] = b_per_GeV
        # Calculate F68 = S / (S + B) in the range MH +- effsigma
        s_in_range = 0.683 * total_n_exp  # Assuming 68.3% of signal is within effsigma range
        new_row['$F_{68}$'] = s_in_range / (s_in_range + b_integral) if (s_in_range + b_integral) > 0 else 999
    else:
        new_row['Bkg (GeV$^{-1}$)'] = 999
        new_row['$F_{68}$'] = 999

    # Append the new row to the dataframe
    summary_df = pd.concat([summary_df, pd.DataFrame([new_row])], ignore_index=True)

# Output summary_df as latex table
# Total, Target STXS region(s), and each STXS region (stage0) columns should be formatted to 1 decimal place
# Sigma effecitive to two decimal places
# Background per GeV to 3 sigfig but don't allow scientific notation
# S/S+B to 2 decimal places
summary_df['Total'] = summary_df['Total'].map(lambda x: f"{x:.1f}")
summary_df['Target STXS region(s)'] = summary_df['Target STXS region(s)'].map(lambda x: f"{x:.1f}\\%")
for stage0 in stage0_regions:
    summary_df[translate_stage0[stage0]] = summary_df[translate_stage0[stage0]].map(lambda x: f"{x:.1f}\\%")
summary_df['$\\sigma_{eff}$ (GeV)'] = summary_df['$\\sigma_{eff}$ (GeV)'].map(lambda x: f"{x:.2f}")
summary_df['Bkg (GeV$^{-1}$)'] = summary_df['Bkg (GeV$^{-1}$)'].map(lambda x: f"{x:.0f}" if x > 10 else f"{x:.1f}")
summary_df['$F_{68}$'] = summary_df['$F_{68}$'].map(lambda x: f"{x:.2f}")

# Output as latex table
latex_table = summary_df.to_latex(index=False, escape=False, column_format='l' + 'c' * (len(summary_df.columns) - 1), label="tab:summary_table")
output_latex_file = os.path.join(f"summary_table{args.ext}.tex")
with open(output_latex_file, 'w') as f:
    f.write(latex_table)