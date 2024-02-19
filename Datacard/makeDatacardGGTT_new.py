from audioop import add
from csv import excel_tab
import pandas as pd
import tools.writeToDatacard as td
import argparse
import ROOT
import os
from commonObjects import lumiMap
import systematics_ggbbres
import json
import numpy as np
import copy

class Options:
  def __init__(self, args):
    self.years = '2016,2017,2018'
    self.prune = args.prune
    self.doSTXSMerging = False
    self.doSTXSScaleCorrelationScheme = False

def renameProc(proc, year, args):
  if proc == "sig":
    return args.procTemplate+"mx%dmy%d_%s_hgg"%(args.MX, args.MY, year)
  else:
    return proc+"_%s_hgg"%year

def renameCat(cat, args):
  return args.procTemplate+"mx%dmy%d"%(args.MX, args.MY)+cat

def getProcesses(model_dir, args, nCatPerMasspoint):
  files = os.listdir(model_dir)

  all_processes = []
  for f in files:
    #files are formatted like proc_year_cat.root
    fname = f
    parts = f.split(".root")[0].split("_")
    year = parts[-2]
    proc = renameProc("_".join(parts[:-2]), year, args)
    cat = renameCat(parts[-1], args)

    procName = cat.split("cat")[0]
    catN = cat.split("cat")[1]
    if int(catN) > int(nCatPerMasspoint[procName]):
      continue

    if parts[0] == "sig":
      model = "wsig_13TeV:"+"sig_%s_%s"%(year, parts[-1]) # e.g sig_2016_cat0
    else:
      basic_proc = "_".join(parts[:-2]) # e.g. ttH_M125
      model = "wsig_13TeV:"+"sig_%s_%s_%s"%(year, parts[-1], basic_proc)
    
    all_processes.append([f, model, proc, cat, year])
  return all_processes

def attemptLoadSystematics(json_location):
  if (json_location != None):
    with open(json_location, "r") as f:
      return json.load(f)
  else:
    return None

def getValFromDict(sys_dict, sys_name):
  possible_sys = sys_dict.keys()
  if sys_name in possible_sys:
    val = [sys_dict[sys_name], sys_dict[sys_name]]
  else:
    val = [sys_dict[sys_name+"_left"], sys_dict[sys_name+"_right"]]
  return val

def findFactorySystematic(sys_name, proc, cat, year, sig_systematics, res_bkg_systematics, args):
  if args.procTemplate in proc:
    if sig_systematics != None:
      sys_dict = sig_systematics[str(year)][str(cat[-1])]["%d_%d"%(args.MX, args.MY)]
      val = getValFromDict(sys_dict, sys_name)
    else:
      val = [1,1]
  else:
    if (res_bkg_systematics != None) and ("Interpolation" not in sys_name):
      slimmed_proc = "_".join(proc.split("_")[:-2]) #take away the year_hgg suffix
      sys_dict = res_bkg_systematics[str(year)][str(cat[-1])]["%d_%d"%(args.MX, args.MY)][slimmed_proc]
      val = getValFromDict(sys_dict, sys_name)        
    else:
      val = [1,1]

  val = ["%.4f"%val[0], "%.4f"%val[1]]
  if val[0] == val[1] == "1.0000":
    val = "-"
  elif abs(float(val[0]) - 1) == abs(float(val[1]) - 1):
    val = val[0]
  else:
    val = "%s/%s"%(val[0], val[1])

  return val

def addMigrationSystematics(df):
  """Add interpolation migration systematics to list of systematics"""
  template = {'name':'','title':'','type':'factory','prior':'lnN','correlateAcrossYears':0}

  nCats = len([cat for cat in df.cat.unique() if "cr" not in cat])
  for i in range(nCats-1):    
    template_copy = copy.deepcopy(template)
    template_copy["name"] = template_copy["title"] = "Interpolation_migration_%d_%d"%(i, i+1)
    systematics_ggbbres.experimental_systematics.append(template_copy)

def grabSystematics(df, args):
  sig_systematics = attemptLoadSystematics(args.sig_syst)
  res_bkg_systematics = attemptLoadSystematics(args.res_bkg_syst)

  #addMigrationSystematics(df)

  years = df.year.unique()

  for syst in systematics_ggbbres.experimental_systematics:
    if syst["correlateAcrossYears"] == -1:
      df[syst["name"]] = '-'
      df_name = lambda sys_name, year: sys_name
    else:
      for year in years:
        df["%s_%s"%(syst["name"], year)] = '-'
      df_name = lambda sys_name, year: "%s_%s"%(sys_name, year)

    for idx, row in df.iterrows():
      proc, cat, year = row[["proc", "cat", "year"]]
      if (proc == "bkg_mass") or (proc == "data_obs") or (proc == "dy_merged_hgg"):
        val = '-'
      elif syst["type"] == "factory":
        val = findFactorySystematic(syst["name"], proc, cat, year, sig_systematics, res_bkg_systematics, args)
      elif syst["type"] == "constant":
        val = syst["value"][str(year)]
      else:
        raise Exception()
      df.loc[idx, df_name(syst["name"], year)] = val

  for syst in systematics_ggbbres.theory_systematics:
    assert syst["correlateAcrossYears"] == 1
    df[syst["name"]] = '-'

    for idx, row in df.iterrows():
      proc, cat, year = row[["proc", "cat", "year"]]
      if (proc == "bkg_mass") or (proc == "data_obs") or (args.procTemplate in proc) or (proc == "dy_merged_hgg"):
        val = '-'
      elif syst["type"] == "constant":
        nc = {"ggH":"ggH", "qqH":"VBF", "VH":"VH", "ttH":"ttH"} # name conversion
        if (syst["name"] == "BR_hgg") or (nc[syst["name"].split("_")[-1]] in proc):
          val = syst["value"]
        else:
          val = '-'
      else:
        raise Exception()

      df.loc[idx, syst["name"]] = val

  return df

def getNorm(current_modelWSFile, model, args):
  f = ROOT.TFile(current_modelWSFile,"read")
  w = f.Get(model.split(":")[0])
  # only set MH for the signal model and not res bkg where it doesn't exist
  try:
    w.var("MH").setVal(args.MH)
  except:
    pass
  w.var("MX").setVal(args.MX)
  w.var("MY").setVal(args.MY)

  #w.Print()
  #print("%s_norm"%model.split(":")[1])

  norm = w.function("%s_norm"%model.split(":")[1]).getVal()
  f.Close()
  return norm

def getBackgroundYield(f, cat, my):
  f = ROOT.TFile(f,"read")
  w = f.Get("multipdf")
  xvar = w.var("CMS_hgg_mass")

  if (xvar.getMin() == 65) or (xvar.getMax()==1000): # if Y->gg
    mggl, mggh = my-1.5*(my/125.), my+1.5*(my/125.)
  else:
    mggl, mggh = 125.0-1.5, 125.0+1.5

  xvar.setRange("sig_region",mggl,mggh)
  xvar_argset = ROOT.RooArgSet(xvar)

  # Load multipdf for category and create integral
  multipdf = w.pdf("CMS_hgg_%s_combined_13TeV_bkgshape"%cat)
  multipdfIntegral = multipdf.createIntegral(xvar_argset,xvar_argset,"sig_region")
  multipdfIntegral.SetName("b_integral")

  # Also create integral scaled by total number of Bkg events (actual integral)
  bnorm = w.var("CMS_hgg_%s_combined_13TeV_bkgshape_norm"%cat)
  # Create product of norm with integral
  prod = ROOT.RooProduct("b_integral_extended","b_integral_extended",ROOT.RooArgList(multipdfIntegral,bnorm))

  bkg_yields = []
  for i in range(10):
    w.cat("pdfindex_%s_combined_13TeV"%cat).setIndex(i)
    prodVal = prod.getVal()
    if prodVal == 0:
      prodVal = (mggh-mggl) / (xvar.getMax()-xvar.getMin())
    bkg_yields.append(prodVal)
  print(bkg_yields)
  
  f.Close()
  return max(bkg_yields)
  #return prod.getVal()

def grabYields(df, args):
  df["sig_yield"] = 0
  df["bkg_yield"] = 0
  for idx, row in df.iterrows():
    if (row.proc == "bkg_mass") or (row.proc == "data_obs") or (row.proc == "dy_merged_hgg"):
      #norm = np.inf #ensure does not get pruned
      norm = 0
    else:
      norm = getNorm(row.current_modelWSFile, row.model, args)
      
    sf = 1.
    if args.procTemplate in row.proc:
      sf = 1. / 1000.
    df.loc[idx, "sig_yield"] = norm * sf * row.rate

    if (args.procTemplate in row.proc) and (row.year == "2016"): # only need bkg yield in one row (choose 2016)
      bkg_workspace_file = "/home/users/evourlio/CMSSW_10_2_13/src/flashggFinalFit/Background/massDecorSRs_noSys_DY/outdir_%s_combined_mx%dmy%d/fTest/output/CMS-HGG_multipdf_%s_combined.root"%(args.procTemplate, args.MX, args.MY, row["cat"])
      #bkg_workspace_file = "../Background/outdir_%s_combined_mx%dmy%d/fTest/output/CMS-HGG_multipdf_%s_combined.root"%(args.procTemplate, args.MX, args.MY, row["cat"])
      df.loc[idx, "bkg_yield"] = getBackgroundYield(bkg_workspace_file, row["cat"], args.MY)

  return df

def doPruning(df, args):
  """
  Three types of pruning:
  1) Drop the last category that has terrible S/B (very specific to ggtt)
  2) Drop categories where the s/b is < threshold of total total s/b
  3) Drop resonant background where the contribition is < 0.1*threshold of the signal efficiency in that category
  The lowest limits are O(0.1) fb, so a 0.1*threshold represents a best-case scenario for keeping the res bkg.
  """
  # type 1)
  #cats = sorted(df.cat.unique())
  #print("Pruning %s"%cats[-1])
  #df.loc[df.cat==cats[-1], "prune"] = 1

  # type 2)
  sig_cat_yields = {cat:0 for cat in df.cat.unique()}
  bkg_cat_yields = {cat:0 for cat in df.cat.unique()}
  for cat in df.cat.unique():
    for proc in df.proc.unique():
      if args.procTemplate in proc:
        df_cat_proc = df[(df.cat==cat)&(df.proc==proc)]
        print(df_cat_proc)
        assert len(df_cat_proc) == 1
        sig_cat_yields[cat] += df_cat_proc.iloc[0]["sig_yield"]
        bkg_cat_yields[cat] += df_cat_proc.iloc[0]["bkg_yield"]

  s_b = {cat: sig_cat_yields[cat]/bkg_cat_yields[cat] for cat in df.cat.unique()}
  tot_s_b = np.sqrt(sum([s_b[cat]**2 for cat in df.cat.unique()]))
  for cat in df.cat.unique():
    print(cat, sig_cat_yields[cat], bkg_cat_yields[cat], s_b[cat])
    if s_b[cat] < args.pruneThreshold*tot_s_b:
      print("Pruning %s, s=%.2f, b=%.2f, s/b=%.2f, total s/b=%.2f"%(cat, sig_cat_yields[cat], bkg_cat_yields[cat], s_b[cat], tot_s_b))
      df.loc[df.cat==cat, "prune"] = 1

  # type 3)
  for cat in df.cat.unique():
    if df[df.cat==cat].iloc[0]["prune"] == 1:
      continue

    #tot_yield = df[df.cat==cat]["sig_yield"].sum()
    tot_yield = sum([row["sig_yield"] for i, row in df[df.cat==cat].iterrows() if args.procTemplate in row.proc])
    print("Total %s yield at xs=1fb: %.2f"%(args.procTemplate,tot_yield))

    for proc in df[df.cat==cat].proc.unique():
      df_cat_proc = df[(df.cat==cat)&(df.proc==proc)]
      #print(df_cat_proc)
      assert len(df_cat_proc) == 1
      #if (proc != "bkg_mass") & (proc != "data_obs") & (proc != "dy_merged_hgg") & (df_cat_proc.iloc[0]["sig_yield"] < 0.1*args.pruneThreshold*tot_yield):
      if (proc != "bkg_mass") & (proc != "data_obs") & (proc != "dy_merged_hgg") & (df_cat_proc.iloc[0]["sig_yield"] < 0.01):
        print("Pruning %s from %s, yield = %.2f"%(proc,cat,df_cat_proc.iloc[0]["sig_yield"]))
        df.loc[(df.cat==cat)&(df.proc==proc), "prune"] = 1

  return df

def removeEmptySystematics(df, datacard_loc):
  """After writing datacard, go back and remove lines where systematics don't contribute"""
  n_proc_cat = sum(df["prune"] == 0) - len(df[df["prune"] == 0].cat.unique())

  with open(datacard_loc, "r") as f:
    datacard = f.readlines()

  pruned_datacard = []
  for line in datacard:
    if ("lnN" not in line) or (line.count("-") != n_proc_cat):
      pruned_datacard.append(line)
    else:
      print("Pruning %s"%line.split("lnN")[0])
  
  with open(datacard_loc, "w") as f:
    f.writelines(pruned_datacard)

def createDYSystematics(df):
  cats = df[df.prune==0].cat.unique()
  systematics = [
    {'name':'sig_norm_merged_dy','title':'sig_norm_merged_dy','type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'},
    {'name':'sig_mean_merged_dy','title':'sig_mean_merged_dy','type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'},
    {'name':'sig_sigma_merged_dy','title':'sig_sigma_merged_dy','type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'}
  ]
  for cat in cats:
    num = int(cat[-1])
    cat = "cat%d"%num
    systematics.extend([
      {'name':'sig_norm_merged_%s_dy'%cat,'title':'sig_norm_merged_%s_dy'%cat,'type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'},
      {'name':'sig_mean_merged_%s_dy'%cat,'title':'sig_mean_merged_%s_dy'%cat,'type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'},
      {'name':'sig_sigma_merged_%s_dy'%cat,'title':'sig_sigma_merged_%s_dy'%cat,'type':'signal_shape','mode':'other','mean':'0.0','sigma':'1.0'}
    ])
  return systematics

def getNEvents(modelWSFile, current_modelWSFile):
  f = ROOT.TFile(modelWSFile,"read")
  f.Print()
  w = f.Get(current_modelWSFile.split(":")[0])
  f.Print()
  datahist = w.data(current_modelWSFile.split(":")[1])
  nevents = datahist.sumEntries()
  f.Close()
  return nevents

def main(args):
  columns = ["proc", "cat", "year", "rate", "modelWSFile", "current_modelWSFile", "model", "prune"]
  rows = []

  with open(args.n_in_sideband, "r") as fS:
    sidebands = json.load(fS)
  nCatPerMasspoint = {}
  for sideband in sidebands:
    nCatPerMasspoint[args.procTemplate+'mx'+sideband['sig_proc'].split('_')[-3]+'my'+sideband['sig_proc'].split('_')[-1]] = len(sideband['N'])

  for fname, model, proc, cat, year in getProcesses(args.sig_model_dir, args, nCatPerMasspoint):
    rows.append([proc, cat, year, lumiMap[year]*1000, os.path.join("./Models/signal", fname), os.path.join(args.sig_model_dir, fname), model, 0])

  if args.do_res_bkg:
    for fname, model, proc, cat, year in getProcesses(args.res_bkg_model_dir, args, nCatPerMasspoint):
      rows.append([proc, cat, year, lumiMap[year]*1000, os.path.join("./Models/res_bkg", fname), os.path.join(args.res_bkg_model_dir, fname), model, 0])

  # if args.do_dy_bkg:
  #   for fname, model, proc, cat, year in getProcesses(args.dy_bkg_model_dir, args):
  #     rows.append([proc, cat, year, lumiMap[year]*1000, os.path.join("./Models/dy_bkg", fname), os.path.join(args.dy_bkg_model_dir, fname), model, 0])
  #     print(model)

  df = pd.DataFrame(rows, columns=columns)

  new_rows = []
  for cat in df.cat.unique():
    new_rows.append(["bkg_mass", cat, "merged", 1, "./Models/background/CMS-HGG_multipdf_%s_combined.root"%cat, "", "multipdf:CMS_hgg_%s_combined_13TeV_bkgshape"%cat, 0])
    new_rows.append(["data_obs", cat, "merged", -1, "./Models/background/CMS-HGG_multipdf_%s_combined.root"%cat, "", "multipdf:roohist_data_mass_%s"%cat, 0])
  
    if args.doABCD:
      new_rows.append(["bkg_mass", cat+"cr", "merged", 1, "./Models/background/CMS-HGG_ws_%s_combined.root"%(cat+"cr"), "", "w_control_regions:CMS_hgg_%s_combined_13TeV_bkgshape"%(cat+"cr"), 0])
      new_rows.append(["data_obs", cat+"cr", "merged", -1, "./Models/background/CMS-HGG_ws_%s_combined.root"%(cat+"cr"), "", "w_control_regions:roohist_data_mass_%s"%(cat+"cr"), 0])
      catnum = int(cat.split("cat")[1].split("cr")[0])
      new_rows.append(["dy_merged_hgg", cat+"cr", "merged", 1, "./Models/background/CMS-HGG_ws_%s_combined.root"%(cat+"cr"), "", "w_control_regions:bkg_combined_cat%d_dy"%catnum, 0])
      new_rows.append(["dy_merged_hgg", cat, "merged", 1, "./Models/background/CMS-HGG_ws_%s_combined.root"%(cat+"cr"), "", "w_control_regions:bkg_combined_cat%d_dy"%catnum, 0])


  df = pd.concat([df, pd.DataFrame(new_rows, columns=columns)], ignore_index=True)

  if args.prune:
    if not args.doABCD:
      df = grabYields(df, args)
      df = doPruning(df, args)
    else:
      cr_cats = [cat for cat in df.cat.unique() if cat[-2:]=="cr"]
      nCats = len(cr_cats)
      print(cr_cats)

      df_cr = df[df.cat.isin(cr_cats)]

      df_sr = df[~df.cat.isin(cr_cats)]
      df_sr = grabYields(df_sr, args)
      df_sr = doPruning(df_sr, args)

      for cat in df_sr.cat.unique():
        catnum = int(cat.split("cat")[1])
        if catnum == nCats - 1:
          print("Putting %s back in case it was pruned"%cat)
          df_sr.loc[df_sr.cat==cat, "prune"] = 0
        
        # if prune all rows of this category (pruning whole category)
        if df_sr[df_sr.cat==cat].prune.sum() == sum(df_sr.cat==cat):
          cat_cr = cat+"cr"
          print("Pruning %s because %s was pruned"%(cat_cr, cat))
          df_cr.loc[df_cr.cat==cat_cr, "prune"] = 1

      df = pd.concat([df_sr, df_cr])    
      
  df = grabSystematics(df, args)

  with open(args.output, "w") as f:
    opt=Options(args)
    td.writePreamble(f, opt)
    td.writeProcesses(f,df,opt,args.procTemplate)
    for syst in systematics_ggbbres.experimental_systematics:
      td.writeSystematic(f,df,syst,opt)
    for syst in systematics_ggbbres.theory_systematics:
      td.writeSystematic(f,df,syst,opt)
    td.writeBreak(f)
    for syst in systematics_ggbbres.signal_shape_systematics:
      td.writeSystematic(f,df,syst,opt)
    # if args.do_dy_bkg:
    #   dy_systematics = createDYSystematics(df)
    #   for syst in dy_systematics:
    #     td.writeSystematic(f,df,syst,opt)
    td.writeBreak(f)
    cr_cats = [cat for cat in df.cat.unique() if cat[-2:]=="cr"]
    td.writePdfIndex(f,df[~df.cat.isin(cr_cats)],opt,"_combined")

    f.write("\nsignal_scaler rateParam * %s* 0.001\nnuisance edit freeze signal_scaler"%(args.procTemplate))
    for proc in df[df.prune==0].proc.unique():
      if "M125" in proc: #only write lines when the resonant background is there
        f.write("\nres_bkg_scaler rateParam * *M125* 1\nnuisance edit freeze res_bkg_scaler")
        break
    if args.do_dy_bkg:
      f.write("\ndy_bkg_scaler rateParam * *dy* 1\nnuisance edit freeze dy_bkg_scaler")
      f.write("\ndy_corr group = "+" ".join(["CMS_hgg_nuisance_"+syst["name"] for syst in dy_systematics if "cat" not in syst["name"]]))
      #f.write("\nnuisance edit freeze dy_corr")
      f.write("\ndy_uncorr group = "+" ".join(["CMS_hgg_nuisance_"+syst["name"] for syst in dy_systematics if "cat" in syst["name"]]))
      #f.write("\nnuisance edit freeze dy_uncorr")
      #f.write("\nnuisance edit freeze *nuisance*dy")
      #for syst in dy_systematics:
      #  f.write("\nnuisance edit freeze %s"%("CMS_hgg_nuisance_"+syst["name"]))

    if args.doABCD:
      nCats = len(df.cat.unique())/2

      to_add_to_group = []
      for cat in df[df.prune==0].cat.unique():
        if cat[-2:] == "cr":
          continue
        catnum = int(cat.split("cat")[1])
        df_row = df[(df.proc=="data_obs")&(df.cat==cat+"cr")].iloc[0]
        df_row.current_modelWSFile = bkg_workspace_file = "/home/users/evourlio/CMSSW_10_2_13/src/flashggFinalFit/Background/massDecorSRs_noSys_DY/outdir_%s_combined_mx%dmy%d/fTest/output/CMS-HGG_ws_%s_combined.root"%(args.procTemplate, args.MX, args.MY, df_row["cat"])
        #df_row.current_modelWSFile = bkg_workspace_file = "../Background/outdir_%s_combined_mx%dmy%d/fTest/output/CMS-HGG_ws_%s_combined.root"%(args.procTemplate, args.MX, args.MY, df_row["cat"])
        cr_yield = getNEvents(df_row.current_modelWSFile, df_row.model)
        upper_bound = cr_yield*2

        if catnum == nCats - 1:
          f.write("\nABCD_A rateParam %scr dy_merged_hgg %d [0,%d]"%(cat, cr_yield, upper_bound))
          #f.write("\nABCD_A rateParam %scr dy_merged_hgg %d [0,3000000]"%(cat, cr_yield))
          to_add_to_group.append("ABCD_A")
          #TODO find a way to not hard code 5800
          f.write("\nABCD_C rateParam %s dy_merged_hgg 5800 [0,%d]"%(cat, upper_bound))
          #f.write("\nABCD_C rateParam %s dy_merged_hgg 5800 [0,10000]"%cat)
          to_add_to_group.append("ABCD_C")
        else:
          f.write("\nABCD_B%d rateParam %scr dy_merged_hgg %d [0,%d]"%(catnum, cat, cr_yield, upper_bound))
          #f.write("\nABCD_B%d rateParam %scr dy_merged_hgg %d [0,20000]"%(catnum, cat, cr_yield))
          to_add_to_group.append("ABCD_B%d"%catnum)
          f.write("\nABCD_D%d rateParam %s dy_merged_hgg (@0*(@1/@2)) ABCD_C,ABCD_B%d,ABCD_A"%(catnum, cat, catnum))
        f.write("\ndy_bkg_scaler rateParam %s dy_merged_hgg 1"%cat)

      f.write("\nnuisance edit freeze dy_bkg_scaler")
      f.write("\nABCD group = "+" ".join(to_add_to_group))

      #f.write("\nABCD_veto_eff rateParam !(*cat) dy_merged_hgg 1 0,1")

  #removeEmptySystematics(df, args.output)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--sig-syst', type=str, default=None, required=False)
  parser.add_argument('--do-res-bkg', action="store_true")
  parser.add_argument('--do-dy-bkg', action="store_true")
  parser.add_argument('--res-bkg-syst', type=str, default=None, required=False)
  parser.add_argument('--output', '-o', type=str, required=True)
  parser.add_argument('--n-in-sideband', type=str, required=True)
  parser.add_argument('--MH', type=float, required=True)
  parser.add_argument('--MX', type=float, required=True)
  parser.add_argument('--MY', type=float, required=True)

  parser.add_argument('--sig-model-dir', type=str, default="../SignalModelInterpolation/outdir", required=False)
  parser.add_argument('--res-bkg-model-dir', type=str, default="../SignalModelInterpolation/res_bkg_outdir", required=False)
  parser.add_argument('--dy-bkg-model-dir', type=str, default="../SignalModelInterpolation/dy_bkg_outdir", required=False)
  parser.add_argument('--procTemplate', type=str, default="ggbbres", required=False)
  parser.add_argument('--doABCD', action="store_true")

  parser.add_argument('--prune', action="store_true")
  parser.add_argument('--pruneThreshold', type=float, default=0.01)

  args = parser.parse_args()

  # turn off res bkg if MH not close to 125
  #if not (115 < args.MH < 135):
  #  args.do_res_bkg = False

  if args.sig_syst == None:
    print("Not doing signal systematics")
  if args.do_res_bkg:
    if args.res_bkg_syst == None:
      print("Not doing res bkg systematics")

  main(args)

