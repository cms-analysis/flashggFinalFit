import argparse
import os
import json

cats_ordered = ['RECO_GG2H_0J_PTH_0_10_res0', 'RECO_GG2H_0J_PTH_0_10_res1', 'RECO_GG2H_0J_PTH_0_10_res2', 'RECO_GG2H_0J_PTH_GT10_res0', 'RECO_GG2H_0J_PTH_GT10_res1', 'RECO_GG2H_0J_PTH_GT10_res2', 'RECO_GG2H_1J_PTH_0_60_res0', 'RECO_GG2H_1J_PTH_0_60_res1', 'RECO_GG2H_1J_PTH_0_60_res2',  'RECO_GG2H_1J_PTH_60_120_res0', 'RECO_GG2H_1J_PTH_60_120_res1', 'RECO_GG2H_1J_PTH_60_120_res2', 'RECO_GG2H_1J_PTH_120_200_res0', 'RECO_GG2H_1J_PTH_120_200_res1', 'RECO_GG2H_1J_PTH_120_200_res2','RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120_res2', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res0', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res1', 'RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200_res2', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res0', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res1', 'RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200_res2', 'RECO_GG2H_PTH_200_300_res0', 'RECO_GG2H_PTH_200_300_res1', 'RECO_GG2H_PTH_200_300_res2', 'RECO_GG2H_PTH_300_450_res0', 'RECO_GG2H_PTH_300_450_res1', 'RECO_GG2H_PTH_450_650', 'RECO_GG2H_PTH_GT650', 'RECO_QQ2HQQ_REST_res0', 'RECO_QQ2HQQ_REST_res1', 'RECO_QQ2HQQ_REST_res2', 'RECO_QQ2HQQ_GE2J_MJJ_60_120', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_res2', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_res1', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res0', 'RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_res1',  'RECO_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200', 'RECO_WH2HLNU_PTV_0_75', 'RECO_WH2HLNU_PTV_75_150', 'RECO_WH2HLNU_PTV_GT150', 'RECO_ZH2HLL_PTV_0_150_ZH_ll', 'RECO_ZH2HLL_PTV_GT150_ZH_ll', 'RECO_ZH2HLL_PTV_0_150_ZH_nunu', 'RECO_ZH2HLL_PTV_GT150_ZH_nunu', 'RECO_TTH_PTH_0_60_ttH_had_res0', 'RECO_TTH_PTH_0_60_ttH_had_res1', 'RECO_TTH_PTH_60_120_ttH_had_res0', 'RECO_TTH_PTH_60_120_ttH_had_res1', 'RECO_TTH_PTH_120_200_ttH_had', 'RECO_TTH_PTH_200_300_ttH_had', 'RECO_TTH_PTH_GT300_ttH_had', 'RECO_TTH_PTH_0_60_ttH_semilep', 'RECO_TTH_PTH_60_120_ttH_semilep', 'RECO_TTH_PTH_120_200_ttH_semilep', 'RECO_TTH_PTH_200_300_ttH_semilep', 'RECO_TTH_PTH_GT300_ttH_semilep', 'RECO_TTH_PTH_0_60_ttH_lep',   'RECO_TTH_PTH_60_120_ttH_lep',   'RECO_TTH_PTH_120_200_ttH_lep',   'RECO_TTH_PTH_200_300_ttH_lep',    'RECO_TTH_PTH_GT300_ttH_lep', 'RECO_TH_tH_had_res0', 'RECO_TH_tH_had_res1', 'RECO_TH_tH_lep']

procs_ordered = ['GG2H_0J_PTH_0_10', 'GG2H_0J_PTH_GT10', 'GG2H_1J_PTH_0_60',  'GG2H_1J_PTH_60_120', 'GG2H_1J_PTH_120_200', 'GG2H_GE2J_MJJ_0_350_PTH_0_60',  'GG2H_GE2J_MJJ_0_350_PTH_60_120', 'GG2H_GE2J_MJJ_0_350_PTH_120_200', 'GG2H_GE2J_MJJ_GT350_PTH_0_200', 'GG2H_PTH_200_300', 'GG2H_PTH_300_450', 'GG2H_PTH_450_650', 'GG2H_PTH_GT650', 'QQ2HQQ_REST', 'QQ2HQQ_GE2J_MJJ_60_120', 'QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200',  'QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200',  'QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200',  'WH2HLNU_PTV_0_75', 'WH2HLNU_PTV_75_150', 'WH2HLNU_PTV_GT150', 'ZH2HLL_PTV_0_150', 'ZH2HLL_PTV_GT150', 'TTH_PTH_0_60', 'TTH_PTH_60_120', 'TTH_PTH_120_200', 'TTH_PTH_200_300',  'TTH_PTH_GT300', 'TH']

plot_width_dict = {
    "1" : "1",
    "2" : "0.49",
    "3" : "0.32"
}

def add_preamble():
    return r"""\begin{figure}[!htbp]
  \centering"""

def add_postamble(name="category_plots", plot_index=0):
    return r"""  \caption{Add caption.}
  \label{fig:""" + name + """_""" + str(plot_index) + r"""}
\end{figure}"""

parser = argparse.ArgumentParser()
parser.add_argument("--plot-path", type=str, required=True, help="Path to pdf files")
parser.add_argument("--plot-handle", type=str, required=True, help="Handle for the plot files")
parser.add_argument("--plot-name", type=str, required=True, help="Name for the plot files")
parser.add_argument("--plots-per-row", type=str, required=True, help="Number of plots per row")
parser.add_argument("--plots-per-figure", type=str, required=True, help="Number of plots per figure")
parser.add_argument('--loop', dest='loop', default='cats', help="Loop over 'cats' or 'procs'")
args = parser.parse_args()

# Split up cats into chunks of size plots_per_figure
plots_per_figure = int(args.plots_per_figure)
cat_chunks = [cats_ordered[i:i + plots_per_figure] for i in range(0, len(cats_ordered), plots_per_figure)]
proc_chunks = [procs_ordered[i:i + plots_per_figure] for i in range(0, len(procs_ordered), plots_per_figure)]

if args.loop == 'cats':
    chunks = cat_chunks
elif args.loop == 'procs':
    chunks = proc_chunks

for i, chunk in enumerate(chunks):
    print(add_preamble())
    for j, cat in enumerate(chunk):
        print(r"  \includegraphics[width=" + plot_width_dict.get(args.plots_per_row, "1") + r"\textwidth]{" + os.path.join(args.plot_path, f"{args.plot_handle}_{cat}.pdf") + "}")
    print(add_postamble(name=args.plot_name, plot_index=i))
    print()