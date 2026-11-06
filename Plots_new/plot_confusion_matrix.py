import pandas as pd
import numpy as np
import argparse
import os
import json

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import mplhep as hep
hep.style.use("CMS")
from mpl_toolkits.axes_grid1 import make_axes_locatable

fontsize_map = {
    'values': 10,
    'cbar_label': 28,
    'cbar_tick_label': 22,
    'x_tick_label': 12,
    'y_tick_label': 12,
    'x_label': 28,
    'y_label': 28,
    'cms_title': 28
}

cmap = mcolors.LinearSegmentedColormap.from_list(
    "truncated_Greens",
    plt.cm.Greens(np.linspace(0.0, 0.5, 256))
)
plt.colormaps.register(cmap)
plt.set_cmap("truncated_Greens")

# Translate procs
def load_translations(json_file):
    with open(json_file, 'r') as f:
        translations = json.load(f)
    return translations

def translate(x, translation_dict):
    return translation_dict[x] if x in translation_dict else x

def plot_numbers_on_matrix(ax,mat,fontsize=16,drop_minor=False):
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            c = mat.values[i,j]
            if drop_minor:
                if abs(c) > 0.5:
                    ax.text(j,i,'{:.0f}'.format(c),fontdict={'size': fontsize},va='center',ha='center')
            else:
                if c != 0:
                    if abs(c) < 0.5:
                        ax.text(j,i,'{:.0f}'.format(abs(c)),fontdict={'size': fontsize},va='center',ha='center')
                    else:
                        ax.text(j,i,'{:.0f}'.format(c),fontdict={'size': fontsize},va='center',ha='center')

def plot_matrix(fig, ax, matrix, xlabel, ylabel, zlabel='Category composition (%)', do_text=False, drop_minor=False):
    plt.set_cmap(cmap)
    mat = ax.matshow(matrix, vmin=0, vmax=100, aspect='auto')
    if do_text:
        plot_numbers_on_matrix(ax, matrix, fontsize=fontsize_map['values'], drop_minor=drop_minor)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = fig.colorbar(mat, cax=cax)
    cbar.set_label(zlabel, fontsize=fontsize_map['cbar_label'])
    cbar.ax.tick_params(labelsize=fontsize_map['cbar_tick_label'])
    ax.set_xticks(np.arange(len(xlabel)))
    ax.set_yticks(np.arange(len(ylabel)))
    ax.set_xticklabels(xlabel, fontsize=fontsize_map['x_tick_label'], rotation=90)
    ax.set_yticklabels(ylabel, fontsize=fontsize_map['y_tick_label'])
    ax.tick_params(axis='both', which='both', size=0, pad=5)
    ax.xaxis.tick_bottom()


parser = argparse.ArgumentParser()
parser.add_argument("--input-csv", type=str, required=True, help="Path to the input csv storing yields")
parser.add_argument("--process-map", type=str, required=True, help="Path to json file storing process map")
parser.add_argument('--do-text', dest='do_text', default=False, action="store_true", help="Add text values to plot")
parser.add_argument('--drop-minor', dest='drop_minor', default=False, action="store_true", help="Drop neglgible terms in matrix")
parser.add_argument('--figsize', dest='figsize', default="10,10", help="Figure size")
parser.add_argument('--cms-label', dest='cms_label', default="Simulation Preliminary", help="CMS sub-label")
parser.add_argument('--plot-path', dest='plot_path', default="plots", help="Path to directory to save the plot")
parser.add_argument('--proc-vertical-line', dest='proc_vertical_line', default=None, help="List of procs to draw vertical line after")
parser.add_argument('--cat-horizontal-line', dest='cat_horizontal_line', default=None, help="List of categories to draw horizontal line after")
parser.add_argument('--translate-procs-json', dest='translate_procs_json', default=None, help="Path to json file storing process translation map")
parser.add_argument('--translate-cats-json', dest='translate_cats_json', default=None, help="Path to json file storing category translation map")
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

procs_ordered = ['FWDH', 'BBH', 'GG2H_0J_PTH_0_10', 'GG2H_0J_PTH_GT10', 'GG2H_1J_PTH_0_60',  'GG2H_1J_PTH_60_120', 'GG2H_1J_PTH_120_200', 'GG2H_GE2J_MJJ_0_350_PTH_0_60',  'GG2H_GE2J_MJJ_0_350_PTH_60_120', 'GG2H_GE2J_MJJ_0_350_PTH_120_200', 'GG2H_GE2J_MJJ_GT350_PTH_0_200', 'GG2H_PTH_200_300', 'GG2H_PTH_300_450', 'GG2H_PTH_450_650', 'GG2H_PTH_GT650', 'QQ2HQQ_REST', 'QQ2HQQ_GE2J_MJJ_60_120', 'QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200',  'QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200',  'QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200',  'WH2HLNU_PTV_0_75', 'WH2HLNU_PTV_75_150', 'WH2HLNU_PTV_GT150', 'ZH2HLL_PTV_0_150', 'ZH2HLL_PTV_GT150', 'TTH_PTH_0_60', 'TTH_PTH_60_120', 'TTH_PTH_120_200', 'TTH_PTH_200_300',  'TTH_PTH_GT300', 'TH']

cats_ordered = ['RECO_GG2H_0J_PTH_0_10_res0', 'RECO_GG2H_0J_PTH_0_10_res1', 'RECO_GG2H_0J_PTH_0_10_res2', 'RECO_GG2H_0J_PTH_GT10_res0', 'RECO_GG2H_0J_PTH_GT10_res1', 'RECO_GG2H_0J_PTH_GT10_res2', 'RECO_GG2H_1J_PTH_0_60_res0', 'RECO_GG2H_1J_PTH_0_60_res1', 'RECO_GG2H_1J_PTH_0_60_res2',  'RECO_GG2H_1J_PTH_60_120_res0', 'RECO_GG2H_1J_PTH_60_120_res1', 'RECO_GG2H_1J_PTH_60_120_res2', 'RECO_GG2H_1J_PTH_120_200_res0', 'RECO_GG2H_1J_PTH_120_200_res1', 'RECO_GG2H_1J_PTH_120_200_res2','RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res2', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res0', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res1', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res2', 'RECO_GG2H_PTH_200_300_res0', 'RECO_GG2H_PTH_200_300_res1', 'RECO_GG2H_PTH_200_300_res2', 'RECO_GG2H_PTH_300_450_res0', 'RECO_GG2H_PTH_300_450_res1', 'RECO_GG2H_PTH_450_650', 'RECO_GG2H_PTH_GT650', 'RECO_QQ2HQQ_REST_res0', 'RECO_QQ2HQQ_REST_res1', 'RECO_QQ2HQQ_REST_res2', 'RECO_QQ2HQQ_GE2J_MJJ_60_120', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res1',  'RECO_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200', 'RECO_WH2HLNU_PTV_0_75', 'RECO_WH2HLNU_PTV_75_150', 'RECO_WH2HLNU_PTV_GT150', 'RECO_ZH2HLL_PTV_0_150_ZH_ll', 'RECO_ZH2HLL_PTV_GT150_ZH_ll', 'RECO_ZH2HLL_PTV_0_150_ZH_nunu', 'RECO_ZH2HLL_PTV_GT150_ZH_nunu', 'RECO_TTH_PTH_0_60_ttH_had_res0', 'RECO_TTH_PTH_0_60_ttH_had_res1', 'RECO_TTH_PTH_60_120_ttH_had_res0', 'RECO_TTH_PTH_60_120_ttH_had_res1', 'RECO_TTH_PTH_120_200_ttH_had', 'RECO_TTH_PTH_200_300_ttH_had', 'RECO_TTH_PTH_GT300_ttH_had', 'RECO_TTH_PTH_0_60_ttH_semilep', 'RECO_TTH_PTH_60_120_ttH_semilep', 'RECO_TTH_PTH_120_200_ttH_semilep', 'RECO_TTH_PTH_200_300_ttH_semilep', 'RECO_TTH_PTH_GT300_ttH_semilep', 'RECO_TTH_PTH_0_60_ttH_lep',   'RECO_TTH_PTH_60_120_ttH_lep',   'RECO_TTH_PTH_120_200_ttH_lep',   'RECO_TTH_PTH_200_300_ttH_lep',    'RECO_TTH_PTH_GT300_ttH_lep', 'RECO_TH_tH_had_res0', 'RECO_TH_tH_had_res1', 'RECO_TH_tH_lep']
cats_ordered.reverse()

# Create counts matrix: row = category, column = proc_mapped, value = sum of n_exp
# Order the rows and columns according to the specified order
counts_matrix = df.pivot_table(index='cat', columns='proc_mapped', values='n_exp', aggfunc=np.sum, fill_value=0)
counts_matrix = counts_matrix.reindex(index=cats_ordered, columns=procs_ordered)

# Normalize the counts matrix to get percentages i.e. row sums to 100
conf_matrix = counts_matrix.div(counts_matrix.sum(axis=1), axis=0) * 100

# Extract axis labels
xlabels = [translate(proc, translate_procs) for proc in conf_matrix.columns]
ylabels= [translate(cat, translate_cats) for cat in conf_matrix.index]

fig_width, fig_height = float(args.figsize.split(",")[0]),float(args.figsize.split(",")[1])
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
plot_matrix(fig, ax, conf_matrix, xlabel=xlabels, ylabel=ylabels, do_text=args.do_text, drop_minor=args.drop_minor)
hep.cms.label(ax=ax, label=args.cms_label, data=True, fontsize=fontsize_map['cms_title'], com='13.6')

# Draw vertical lines after specified processes if provided
if args.proc_vertical_line:
    procs_to_draw_line_after = args.proc_vertical_line.split(",")
    for proc in procs_to_draw_line_after:
        if proc in conf_matrix.columns:
            col_index = list(conf_matrix.columns).index(proc)
            ax.axvline(x=col_index + 0.5, color='grey', linestyle='-', linewidth=1, alpha=0.5)

# Draw horizontal lines after specified categories if provided
if args.cat_horizontal_line:
    cats_to_draw_line_after = args.cat_horizontal_line.split(",")
    for cat in cats_to_draw_line_after:
        if cat in conf_matrix.index:
            row_index = list(conf_matrix.index).index(cat)
            ax.axhline(y=row_index -0.5, color='grey', linestyle='-', linewidth=1, alpha=0.5)

ax.set_xlabel("STXS region(s)", fontsize=fontsize_map['x_label'])
ax.set_ylabel("Analysis category (reco)", fontsize=fontsize_map['y_label'])

if not os.path.exists(args.plot_path):
    os.makedirs(args.plot_path, exist_ok=True)

ext_str = f"_{args.ext}" if args.ext else ""
fig.savefig(os.path.join(args.plot_path, f"confusion_matrix{ext_str}.png"), bbox_inches='tight')
fig.savefig(os.path.join(args.plot_path, f"confusion_matrix{ext_str}.pdf"), bbox_inches='tight')
