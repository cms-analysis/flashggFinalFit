import law
import os, sys
import matplotlib.pyplot as plt
import ROOT
import re
import uproot
from collections import OrderedDict as od
import glob, shutil
import errno
import yaml

from functools import partial
import CombineHarvester.CombineTools.plotting as plot
from six.moves import range

import pandas
import numpy as np
import mplhep as hep

# Use CMS style from mplhep for plotting
plt.style.use(hep.style.CMS)

from commonTools import *
from commonObjects import *

from Combine.law_combine import *

from framework import Task
from framework import HTCondorWorkflow

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)
  
def convert_boolean_string(string):
    if (string == "True") or (string == "true") or (string == True):
        return True
    else:
        return False

class CreateDiffSpectra(law.Task):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default='', description="Variable to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    is_unblinded = law.Parameter(default=False, description="Flag that signifies if spectrum is created for the unblinded results.")

    # htcondor_job_kwargs_submit = {"spool": True}  
    
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        if convert_boolean_string(self.is_unblinded):
            tasks = [PValueCalculation(output_dir=output_dir, variable=self.variable, year=self.year)]
        else:
            tasks = [CreateAsimovFit(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")

        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):
        # current_mode_proc_mass = self.branch_data
        
        # returns output folder
        if self.variable == '':
            input_config = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            input_config = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        
        outputFileTargets = []
        
        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
            output = [] 
        else:
            fitFolderName = f'runFits_{self.variable}'
            if convert_boolean_string(self.is_unblinded):
                output = [os.path.join(output_dir, 'Combine', fitFolderName, 'spectra.pdf')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'spectra.png')]
            else:
                output = [os.path.join(output_dir, 'Combine', fitFolderName, 'spectra_blinded.pdf')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'spectra_blinded.png')]
            
        for current_output in output:
            outputFileTargets.append(law.LocalFileTarget(current_output))        
        return outputFileTargets

    def run(self):
        
        # current_mode_proc_mass = self.branch_data
        
        # returns output folder
        if self.variable == '':
            input_config = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            input_config = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        
        
        def read(scan, param, files, ycut):
            goodfiles = [f for f in files if plot.TFileIsGood(f)]
            limit = plot.MakeTChain(goodfiles, 'limit')
            graph = plot.TGraphFromTree(limit, param, '2*deltaNLL', 'quantileExpected > -1.5')
            graph.SetName(scan)
            graph.Sort()
            plot.RemoveGraphXDuplicates(graph)
            plot.RemoveGraphYAbove(graph, ycut)
            # graph.Print()
            return graph    


        def Eval(obj, x, params):
            return obj.Eval(x[0])


        def BuildScan(param, files, yvals, ycut):
            graph = read('1', param, files, ycut)
            if graph.GetN() <= 1:
                graph.Print()
                raise RuntimeError(f'Attempting to build {param} scan from TGraph with zero or one point (see above)')
            
            bestfit = None
            for i in range(graph.GetN()):
                if graph.GetY()[i] == 0.:
                    bestfit = graph.GetX()[i]
            
            spline = ROOT.TSpline3("spline3", graph)
            
            # Incrementally build the function name using a counter passed as a parameter
            func_method = partial(Eval, spline)
            func_name = f'splinefn_{param}'
            func = ROOT.TF1(func_name, func_method, graph.GetX()[0], graph.GetX()[graph.GetN() - 1], 1)
            func._method = func_method
            func.SetLineWidth(3)

            assert bestfit is not None
            crossings = {}
            cross_1sig = None
            cross_2sig = None
            other_1sig = []
            other_2sig = []
            val = None
            val_2sig = None

            # Find crossings for the 1-sigma and 2-sigma levels
            for yval in yvals:
                crossings[yval] = plot.FindCrossingsWithSpline(graph, func, yval)
                for cr in crossings[yval]:
                    cr["contains_bf"] = cr["lo"] <= bestfit and cr["hi"] >= bestfit
            
            # Process 1-sigma crossings
            for cr in crossings[yvals[0]]:
                if cr['contains_bf']:
                    val = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
                    cross_1sig = cr
                else:
                    other_1sig.append(cr)
            
            # Process 2-sigma crossings
            if len(yvals) > 1:
                for cr in crossings[yvals[1]]:
                    if cr['contains_bf']:
                        val_2sig = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
                        cross_2sig = cr
                    else:
                        other_2sig.append(cr)
            else:
                val_2sig = (0., 0., 0.)
                cross_2sig = cross_1sig

            return {
                "graph": graph,
                "spline": spline,
                "func": func,
                "crossings": crossings,
                "val": val,
                "val_2sig": val_2sig,
                "cross_1sig": cross_1sig,
                "cross_2sig": cross_2sig,
                "other_1sig": other_1sig,
                "other_2sig": other_2sig
            }

        # 1 sigma, 2 sigma
        yvals = [1., 4.]
        
        rounding_to_digits = 3
        # Remove points with y > y-cut
        y_cut = 7.
        
        if self.variable == '':
            # Spectra with only one POI does not make any sense
            return True
        else:
            cat_list = combineVariableDict[f'{self.variable}']['paramStrNoOne'] #has to be in the correct order
            fitFolderName = f'runFits_{self.variable}'
            
            oneSigmaDict = {}
            stat_up_list = []
            stat_down_list = []
            
            exp_xs_list = []
            err_up_list = []
            err_down_list = []
            for cat in cat_list:
                # oneSigmaDict[f'{cat}'] = {}
                
                if convert_boolean_string(self.is_unblinded):
                    main_scan_syst = BuildScan(cat, [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanFit_{cat}.MultiDimFit.mH125.38.root')], yvals, y_cut)
                    main_scan_stat = BuildScan(cat, [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanStat_{cat}.MultiDimFit.mH125.38.root')], yvals, y_cut)
                    
                    pvalue_path = os.path.join(output_dir, 'Combine', fitFolderName, 'pvalue.txt')
                    
                    with open(pvalue_path, 'r') as file:
                        pvalue = file.readline()
                    
                else:
                    main_scan_syst = BuildScan(cat, [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')], yvals, y_cut)
                    main_scan_stat = BuildScan(cat, [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')], yvals, y_cut)
                    
                    pvalue = 1
                
                stat_up_list.append(abs(round(main_scan_stat['val'][1],rounding_to_digits)))
                stat_down_list.append(abs(round(main_scan_stat['val'][2],rounding_to_digits)))
                
                exp_xs_list.append(round(main_scan_syst['val'][0],rounding_to_digits))
                err_up_list.append(abs(round(main_scan_syst['val'][1],rounding_to_digits)))
                err_down_list.append(abs(round(main_scan_syst['val'][2],rounding_to_digits)))
                
        # print(exp_xs_list)
        # print(err_up_list)
        # print(err_down_list)
        # print(stat_up_list)
        # print(stat_down_list)
        
            
        current_config = config['spectra']

        xs = {}

        # List of variables to import
        vars = ['fidXS', 'fidXS_scale_up', 'fidXS_scale_dn', 'fidXS_pdf_up', 'fidXS_pdf_dn', 'fidXS_alpha_up', 'fidXS_alpha_dn', 'Boundaries']
        
        # Dynamically import the required module for ggH cross-section
        ggh_xs = __import__(current_config['ggh_xs'], globals(), locals(), vars)
        bins = ggh_xs.Boundaries
        bins_plot = np.array(bins)
        if "overflow" in current_config.keys(): bins_plot[-1] = current_config['overflow']
        
        # Calculate bin centers and widths
        bins_c = (bins_plot[1:]+bins_plot[:-1])*0.5
        bin_w = np.array([bins_plot[k+1]-bins_plot[k] for k in range(len(bins)-1)]) / 2
        bin_w_half = bin_w / 2
        xs['ggh'] = np.array(ggh_xs.fidXS)
        ggh_xs_norm = xs['ggh'] / bin_w

        # Dynamically import the required module for xH cross-section
        # xh_xs = __import__(current_config['xh_xs'], globals(), locals(), vars)
        # xh_xs_norm = np.array(xh_xs.fidXS) / bin_w

        # Dynamically import the required module for VBF, VH, and ttH cross-section
        vbf_xs = __import__(current_config['vbf_xs'], globals(), locals(), vars)
        xs['vbf'] = np.array(vbf_xs.fidXS)
        vbf_xs_norm = xs['vbf'] / bin_w

        vh_xs = __import__(current_config['vh_xs'], globals(), locals(), vars)
        xs['vh'] = np.array(vh_xs.fidXS)
        vh_xs_norm = xs['vh'] / bin_w

        tth_xs = __import__(current_config['tth_xs'], globals(), locals(), vars)
        xs['tth'] = np.array(tth_xs.fidXS)
        tth_xs_norm = xs['tth'] / bin_w

        # Dynamically import the required module for ggH POWHEG cross-section
        ggh_powheg_xs = __import__(current_config['ggh_powheg_xs'], globals(), locals(), vars)
        ggh_powheg_xs_norm = np.array(ggh_powheg_xs.fidXS) / bin_w

        # Dynamically import the required module for ggH MadGraph (w/o NNLOPS reweighting) cross-section
        ggh_no_nnlops_xs = __import__(current_config['ggh_no_nnlops_xs'], globals(), locals(), vars)
        ggh_no_nnlops_xs_norm = np.array(ggh_no_nnlops_xs.fidXS) / bin_w
        
        if current_config['underflow_bin_normalized'] == True:
            ggh_xs_norm[0] = ggh_xs_norm[0] * bin_w[0]
            vbf_xs_norm[0] = vbf_xs_norm[0] * bin_w[0]
            vh_xs_norm[0] = vh_xs_norm[0] * bin_w[0]
            tth_xs_norm[0] = tth_xs_norm[0] * bin_w[0]
            ggh_powheg_xs_norm[0] = ggh_powheg_xs_norm[0] * bin_w[0]
            ggh_no_nnlops_xs_norm[0] = ggh_no_nnlops_xs_norm[0] * bin_w[0]
        
        xh_xs_norm = vbf_xs_norm + vh_xs_norm + tth_xs_norm

        # Theoretical uncertainty
        sources_up = ["fidXS_scale_up", "fidXS_pdf_up", "fidXS_alpha_up"]

        ## [[fidXS_scale_up unc per bin], [fidXS_pdf_up unc per bin], [fidXS_alpha_up unc per bin]]
        ggh_up = [abs(np.array(getattr(ggh_xs, source)) - np.array(ggh_xs.fidXS)) for source in sources_up]
        ggh_powheg_up = [abs(np.array(getattr(ggh_powheg_xs, source)) - np.array(ggh_powheg_xs.fidXS)) for source in sources_up]
        ggh_no_nnlops_up = [abs(np.array(getattr(ggh_no_nnlops_xs, source)) - np.array(ggh_no_nnlops_xs.fidXS)) for source in sources_up]
        vbf_up = [abs(np.array(getattr(vbf_xs, source)) - np.array(vbf_xs.fidXS)) for source in sources_up]
        vh_up = [abs(np.array(getattr(vh_xs, source)) - np.array(vh_xs.fidXS)) for source in sources_up]
        tth_up = [abs(np.array(getattr(tth_xs, source)) - np.array(tth_xs.fidXS)) for source in sources_up]

        sources_dn = ["fidXS_scale_dn", "fidXS_pdf_dn", "fidXS_alpha_dn"]
        
        ggh_dn = [abs(np.array(getattr(ggh_xs, source)) - np.array(ggh_xs.fidXS)) for source in sources_dn]
        ggh_powheg_dn = [abs(np.array(getattr(ggh_powheg_xs, source)) - np.array(ggh_powheg_xs.fidXS)) for source in sources_dn]
        ggh_no_nnlops_dn = [abs(np.array(getattr(ggh_no_nnlops_xs, source)) - np.array(ggh_no_nnlops_xs.fidXS)) for source in sources_dn]
        vbf_dn = [abs(np.array(getattr(vbf_xs, source)) - np.array(vbf_xs.fidXS)) for source in sources_dn]
        vh_dn = [abs(np.array(getattr(vh_xs, source)) - np.array(vh_xs.fidXS)) for source in sources_dn]
        tth_dn = [abs(np.array(getattr(tth_xs, source)) - np.array(tth_xs.fidXS)) for source in sources_dn]
        
        ## sum of the contributions for each production mode
        ## Linear sum as each source of uncertainty is fully correlated across the production modes
        madgraph_up = np.sum([ggh_up,vbf_up,vh_up,tth_up], axis=0)
        powheg_up = np.sum([ggh_powheg_up,vbf_up,vh_up,tth_up], axis=0)
        no_nnlops_up = np.sum([ggh_no_nnlops_up,vbf_up,vh_up,tth_up], axis=0)

        madgraph_dn = np.sum([ggh_dn,vbf_dn,vh_dn,tth_dn], axis=0)
        powheg_dn = np.sum([ggh_powheg_dn,vbf_dn,vh_dn,tth_dn], axis=0)
        no_nnlops_dn = np.sum([ggh_no_nnlops_dn,vbf_dn,vh_dn,tth_dn], axis=0)

        ## Sum in quadrature of the different sources of uncertainties + uncertainty on the BR
        unc_th_up = (np.sqrt((np.sqrt(np.sum(np.square(madgraph_up), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth'])) / bin_w
        unc_th_dn = (np.sqrt((np.sqrt(np.sum(np.square(madgraph_dn), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth'])) / bin_w

        unc_th_powheg_up = np.sqrt((np.sqrt(np.sum(np.square(powheg_up), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']) / bin_w
        unc_th_powheg_dn = np.sqrt((np.sqrt(np.sum(np.square(powheg_dn), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']) / bin_w

        unc_th_no_nnlops_up = np.sqrt((np.sqrt(np.sum(np.square(no_nnlops_up), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']) / bin_w
        unc_th_no_nnlops_dn = np.sqrt((np.sqrt(np.sum(np.square(no_nnlops_dn), axis=0)) / (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']))**2 + 0.02**2 ) * (xs['ggh']+xs['vbf']+xs['vh']+xs['tth']) / bin_w
        
        if current_config['underflow_bin_normalized'] == True:
            unc_th_up[0] = unc_th_up[0] * bin_w[0]
            unc_th_dn[0] = unc_th_dn[0] * bin_w[0]
            unc_th_powheg_up[0] = unc_th_powheg_up[0] * bin_w[0]
            unc_th_powheg_dn[0] = unc_th_powheg_dn[0] * bin_w[0]
            unc_th_no_nnlops_up[0] = unc_th_no_nnlops_up[0] * bin_w[0]
            unc_th_no_nnlops_dn[0] = unc_th_no_nnlops_dn[0] * bin_w[0]
            bin_w[0] = 15
            bin_w[-1] = 100
            
        # Compute expected cross-section and uncertainties
        exp_xs = np.array(exp_xs_list) * (ggh_xs_norm + xh_xs_norm)
        err_up = np.array(err_up_list) * (ggh_xs_norm + xh_xs_norm)
        err_down = np.array(err_down_list) * (ggh_xs_norm + xh_xs_norm)

        stat_up = np.array(stat_up_list) * (ggh_xs_norm + xh_xs_norm)
        stat_down = np.array(stat_down_list) * (ggh_xs_norm + xh_xs_norm)
        
        sys_up = []
        sys_down = []
        
        for diff_up in (err_up**2 - stat_up**2):
            if diff_up >= 0:
                sys_up.append(np.sqrt(diff_up))
            else:
                print(f"(err_up**2 - stat_up**2) == {diff_up}: Setting sys_up == 0")
                sys_up.append(0)
        
        for diff_down in (err_down**2 - stat_down**2):
            if diff_down >= 0:
                sys_down.append(np.sqrt(diff_down))
            else:
                print(f"(err_down**2 - stat_down**2) == {diff_down}: Setting sys_down == 0")
                sys_down.append(0)
        
        # #######################################
        # ##### S T A R T   P L O T T I N G #####
        # #######################################

        plotting_config_path = os.path.join(os.environ["ANALYSIS_PATH"],"Plots", "Spectra", "config",f"{self.year}_{self.variable}.yml")
        
        with open(plotting_config_path, 'r') as file:
            plotting_config = yaml.safe_load(file)

        fig = plt.figure(figsize=(10,8), dpi=120) # (10,8)
        frame1 = fig.add_axes((.1, .35, .8, .6)) #(.1, .35, .8, .6)
        # frame1 = fig.add_axes((.1, .35, .8, .8))
        if current_config['no_preliminary']:
            cms_label = ""
        else:
            cms_label = "Preliminary"
        # print(args.no_preliminary, cms_label)
        hep.cms.label(cms_label, data=convert_boolean_string(self.is_unblinded), lumi=lumiMap[f'{self.year}'], fontsize=20, com=13.6)

        # Plot theoretical predictions and experimental data
        plt.stairs((ggh_xs_norm+xh_xs_norm), bins_plot, linewidth=2, label='ggH (MadGraph5_aMC@NLO + NNLOPS + Pythia) + xH', color='tab:blue')
        plt.stairs((ggh_no_nnlops_xs_norm+xh_xs_norm), bins_plot, linewidth=2, label='ggH (MadGraph5_aMC@NLO + Pythia) + xH', color='tab:purple')
        plt.stairs((ggh_powheg_xs_norm+xh_xs_norm), bins_plot, linewidth=2, label='ggH (POWHEG + Pythia) + xH', color='brown')
        plt.stairs(xh_xs_norm, bins_plot, linewidth=2, color='green')
        plt.stairs(xh_xs_norm, bins_plot, linewidth=2, label='xH = ttH + VH + VBF (MadGraph5_aMC@NLO + Pythia)', alpha=0.2, color='green', fill=True)
        
        if current_config['last_bin_center'] > 0:
            bins_c[-1] = current_config['last_bin_center']
            
        if current_config['first_bin_center'] > 0:
            bins_c[0] = current_config['first_bin_center']
        else:
            bins_c[0] = 0
        
        plt.rcParams['hatch.linewidth'] = 2
        for center, value, err_low, err_high, width in zip(bins_c, ggh_xs_norm+xh_xs_norm, unc_th_dn, unc_th_up, bin_w):
            plt.gca().add_patch(plt.Rectangle((center - width/2, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='tab:blue', hatch='///'))
        # POWHEG
        for center, value, err_low, err_high, width in zip(bins_c, ggh_powheg_xs_norm+xh_xs_norm, unc_th_powheg_dn, unc_th_powheg_up, bin_w):
            plt.gca().add_patch(plt.Rectangle((center + width/5, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='brown', hatch='////'))
        # Madgraph w/o NNLOPS
        for center, value, err_low, err_high, width in zip(bins_c, ggh_no_nnlops_xs_norm+xh_xs_norm, unc_th_no_nnlops_dn, unc_th_no_nnlops_up, bin_w):
            plt.gca().add_patch(plt.Rectangle((center + width/1.8, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='tab:purple', hatch='////'))
            
        # Default font sizes
        fontsize = 14
        title_fontsize = 14
            
        if 'frame1' in plotting_config:
            frameOneSettings = plotting_config['frame1']
            
            if 'custom_xtick_labels' in frameOneSettings:
                custom_xtick_labels = frameOneSettings["custom_xtick_labels"]
                custom_xticks = frameOneSettings["custom_xticks"]
                
                frame1.set_xticks(custom_xticks)
            
            if "axvline" in frameOneSettings:
                axvline_params = frameOneSettings["axvline"]
                plt.axvline(**axvline_params)
                
            if "figtext" in frameOneSettings:
                figtext_params = frameOneSettings["figtext"]
                plt.figtext(
                    figtext_params["x"],
                    figtext_params["y"],
                    figtext_params['text'],
                    horizontalalignment=figtext_params["horizontalalignment"],
                    rotation=figtext_params["rotation"],
                    fontsize=figtext_params["fontsize"]
                )
            # Apply ylabel if defined
            if "ylabel" in frameOneSettings:
                ylabel_params = frameOneSettings["ylabel"]
                plt.ylabel(ylabel_params["text"], fontsize=ylabel_params["fontsize"])
            
            # Apply ylim if defined
            if "ylim" in frameOneSettings:
                ylim_params = frameOneSettings["ylim"]
                plt.ylim(**ylim_params)
            
            # Override font sizes if specified in the config
            fontsize = frameOneSettings.get("fontsize", fontsize)
            title_fontsize = frameOneSettings.get("title_fontsize", title_fontsize)
        
        plt.errorbar(bins_c, exp_xs , yerr=[err_down,err_up], marker = 'o', linestyle = 'None', color = 'k', linewidth = 2, ms=5, capsize=4, label=r'Data (stat $\oplus$ sys unc.)')
        plt.errorbar(bins_c, exp_xs , yerr=[sys_down,sys_up], marker = 'None', linestyle = 'None', color = 'red', linewidth = 6, ms=5, capsize=4, label='Systematic uncertainty')
        
        if current_config['plot_log']:
            plt.yscale('log')
            
        plt.ylabel(r'$\Delta\sigma_{\text{fid}} / \Delta ' + current_config["variable"] + r'$ ' + current_config["y_unit"], fontsize=20)
        
        if "y_lim_top" in current_config.keys(): plt.ylim(top=current_config["y_lim_top"])
        plt.xlim(current_config['x_lim'])

        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
    
        legend_location = current_config.get('legend_location', 'upper right')
        
        plt.legend(fontsize=fontsize, title='p-value (MadGraph NNLOPS) = '+ str(pvalue), alignment='left', loc= legend_location, title_fontsize=title_fontsize)
        frame1.set_xticklabels([])

        frame2 = fig.add_axes((.1,.05,.8,.25))

        # Plot ratio (Data/Prediction) in a separate frame
        ratio_xs = exp_xs / (ggh_xs_norm+xh_xs_norm)
        ratio_powheg = (ggh_powheg_xs_norm+xh_xs_norm) / (ggh_xs_norm+xh_xs_norm)
        ratio_no_nnlops = (ggh_no_nnlops_xs_norm+xh_xs_norm) / (ggh_xs_norm+xh_xs_norm)
        ratio_madgraph = (ggh_xs_norm+xh_xs_norm) / (ggh_xs_norm+xh_xs_norm) # Dummy, it is always 1
        ratio_err_up = err_up / (ggh_xs_norm+xh_xs_norm)
        ratio_err_down = err_down / (ggh_xs_norm+xh_xs_norm)
        ratio_sys_up = sys_up / (ggh_xs_norm+xh_xs_norm)
        ratio_sys_down = sys_down / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_up = unc_th_up / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_dn = unc_th_dn / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_powheg_up = unc_th_powheg_up / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_powheg_dn = unc_th_powheg_dn / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_no_nnlops_up = unc_th_no_nnlops_up / (ggh_xs_norm+xh_xs_norm)
        ratio_unc_no_nnlops_dn = unc_th_no_nnlops_dn / (ggh_xs_norm+xh_xs_norm)

        plt.errorbar(bins_c, ratio_xs , yerr=[ratio_err_down,ratio_err_up], marker = 'o', linestyle = 'None', color = 'k', linewidth = 2, ms=5, capsize=4, label='Data (Stat + Syst)')
        plt.errorbar(bins_c, ratio_xs , yerr=[ratio_sys_down,ratio_sys_up], marker = 'None', linestyle = 'None', color = 'red', linewidth = 6, ms=5, capsize=4, label='Systematic error')

        plt.hlines(1, 0,500, color='tab:blue')

        for center, value, err_low, err_high, width in zip(bins_c, ratio_madgraph, ratio_unc_up, ratio_unc_dn, bin_w):
            plt.gca().add_patch(plt.Rectangle((center - width/2, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='tab:blue', hatch='/////')) #/2
        # POWHEG
        for center, value, err_low, err_high, width in zip(bins_c, ratio_powheg, ratio_unc_powheg_dn, ratio_unc_powheg_up, bin_w):
            plt.gca().add_patch(plt.Rectangle((center + width/5, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='brown', hatch='/////'))
        # Madgraph w/o NNLOPS
        for center, value, err_low, err_high, width in zip(bins_c, ratio_no_nnlops, ratio_unc_no_nnlops_dn, ratio_unc_no_nnlops_up, bin_w):
            plt.gca().add_patch(plt.Rectangle((center + width/1.8, value - err_low), width/4, err_low + err_high, fill=False, lw=0, color='tab:purple', hatch='////'))
        
        plt.stairs(ratio_powheg, bins_plot, linewidth=2, color='brown')
        plt.stairs(ratio_no_nnlops, bins_plot, linewidth=2, color='tab:purple')
        
        if 'frame2' in plotting_config:
            frameTwoSettings = plotting_config['frame2']
            
            # Apply xticks and xtick_labels
            if "xticks" in frameTwoSettings:
                custom_xticks = frameTwoSettings["xticks"]
                frame2.set_xticks(custom_xticks)
            if "xtick_labels" in frameTwoSettings:
                custom_xtick_labels = frameTwoSettings["xtick_labels"]
                frame2.set_xticklabels(custom_xtick_labels)

            # Apply yticks and ytick_labels depending on `is_data`
            if "yticks" in frameTwoSettings and "ytick_labels" in frameTwoSettings:
                if convert_boolean_string(self.is_unblinded):
                    custom_yticks = frameTwoSettings["yticks"].get("is_data", [])
                    custom_ytick_labels = frameTwoSettings["ytick_labels"].get("is_data", [])
                else:
                    custom_yticks = frameTwoSettings["yticks"].get("not_data", [])
                    custom_ytick_labels = frameTwoSettings["ytick_labels"].get("not_data", [])
                frame2.set_yticks(custom_yticks)
                frame2.set_yticklabels(custom_ytick_labels)

            # Apply additional labels for specific variables
            if "additional_labels" in frameTwoSettings:
                additional_labels = frameTwoSettings["additional_labels"]["is_data"] if convert_boolean_string(self.is_unblinded) else frameTwoSettings["additional_labels"]["not_data"]
                for label in additional_labels:
                    frame2.text(
                        label["position"][0],
                        label["position"][1],
                        label["text"],
                        rotation=label["rotation"],
                        fontsize=label["fontsize"]
                    )

            # Apply axvline if defined
            if "axvline" in frameTwoSettings:
                axvline_params = frameTwoSettings["axvline"]
                plt.axvline(**axvline_params)
        
        for b in bins_plot:
            plt.axvline(x=b, color='gray', ls='dashed', lw=1, alpha=0.5)
        
        plt.ylabel(r'Data / Prediction', fontsize=20) #Not MC, since NNLOPS is based on a calculation

        plt.xlabel(r'$' + current_config["variable"] + r'$ ' + current_config["x_unit"], fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        plt.xlim(current_config['x_lim'])
        plt.ylim(current_config['y_lim'])
        
        if convert_boolean_string(self.is_unblinded):
            plt.savefig(os.path.join(output_dir, 'Combine', fitFolderName, 'spectra.pdf'), bbox_inches='tight', dpi=120)
            plt.savefig(os.path.join(output_dir, 'Combine', fitFolderName, 'spectra.png'), bbox_inches='tight', dpi=120)
        else:
            plt.savefig(os.path.join(output_dir, 'Combine', fitFolderName, 'spectra_blinded.pdf'), bbox_inches='tight', dpi=120)
            plt.savefig(os.path.join(output_dir, 'Combine', fitFolderName, 'spectra_blinded.png'), bbox_inches='tight', dpi=120)