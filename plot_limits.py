import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep
mplhep.set_style("CMS")
plt.rcParams["figure.figsize"] = (12.5,10)

import numpy as np
import sys
import tabulate
import pandas as pd
import os

import scipy.interpolate as spi

import common

BR_H_GG = 2.27e-3
BR_H_TT = 6.27e-2
BR_H_BB = 5.84e-1

BR_HH_GGTT = 2 * BR_H_GG * BR_H_TT
BR_HH_GGBB = 2 * BR_H_GG * BR_H_BB

#NMSSM_max_allowed_Y_gg = pd.DataFrame({"MX":   [650, 650,  650, 650, 650],
#                                       "MY":   [70,    250,   550,   800,   70,    100,   70,    70,    125,   300,   90,    400,   70,    100,   300,   250,   500,   70,    190,   450,   550,   70,    500,   600,   70,    170,   400,   650,   70,    80,    190,   650,   700,   70,    500], 
#                                       "limit":[0.0559,0.1305,0.1922,0.4891,0.7906,0.8094,0.3141,0.1508,0.3344,0.7500,0.1289,0.6969,0.0871,0.1262,0.3438,0.2656,0.6969,0.0699,0.1953,0.3734,0.7312,0.0645,0.3750,0.7719,0.0633,0.1414,0.2227,0.7469,0.1063,0.0621,0.1266,0.3562,0.4969,0.0535,0.1914]})


def getLimits(results_path):
  with open(results_path, "r") as f:
    results = f.readlines()

  masses = []
  for line in results:
    m = line.split(".")[0].split("_")[-1]
    mx = int(m.split("mx")[1].split("my")[0])
    my = int(m.split("my")[1].split("mh")[0])
    if "mh" in m: mh = int(m.split("mh")[1])
    else:         mh = 125
    if [mx, my, mh] not in masses:
      masses.append([mx, my, mh])

  limits = np.zeros((5, len(masses)))
  limits_no_sys = np.zeros((5, len(masses)))
  limits_no_res_bkg = np.zeros((5, len(masses)))
  limits_no_dy_bkg = np.zeros((5, len(masses)))

  for line in results:
    m = line.split(".")[0].split("_")[-1]
    mx = int(m.split("mx")[1].split("my")[0])
    my = int(m.split("my")[1].split("mh")[0])
    if "mh" in m: mh = int(m.split("mh")[1])
    else:         mh = 125
    idx1 = masses.index([mx, my, mh])
    if "2.5%" in line:
      idx2=0
    elif "16.0%" in line:
      idx2=1
    elif "50.0%" in line:
      idx2=2
    elif "84.0%" in line:
      idx2=3
    elif "97.5%" in line:
      idx2=4
    
    limit = float(line.split("r < ")[1])

    if "no_sys" in line:
      limits_no_sys[idx2][idx1] = limit
    elif "no_res_bkg" in line:
      limits_no_res_bkg[idx2][idx1] = limit
    elif "no_dy_bkg" in line:
      limits_no_dy_bkg[idx2][idx1] = limit
    else:
      limits[idx2][idx1] = limit

  #print(limits[2])
  #print(limits_no_sys[2])

  masses = np.array(masses)
  #sort out scan over mh (mgg)
  if len(np.unique(np.array(masses)[:,2])) != 1: #if more than 125 in mh
    #find places where mx and mh overlap
    for mx in np.unique(masses[:,0]):
      uniques, counts = np.unique(masses[masses[:,0]==mx, 2], return_counts=True)
      assert sum(counts>2) == 0 #should not have more than 1 overlap
      overlap_mh = uniques[counts==2]

      for mh in overlap_mh:
        idx1, idx2 = np.where( (masses[:,0]==mx) & (masses[:,2]==mh) )[0]
        if limits[2][idx1] < limits[2][idx2]:
          to_delete = idx2
        else:
          to_delete = idx1
        masses = np.delete(masses, to_delete, axis=0)
        limits = np.delete(limits, to_delete, axis=1)
        limits_no_sys = np.delete(limits_no_sys, to_delete, axis=1)
        limits_no_res_bkg = np.delete(limits_no_res_bkg, to_delete, axis=1)
        limits_no_dy_bkg = np.delete(limits_no_dy_bkg, to_delete, axis=1)

  #  masses[:,1] = masses[:,2] #set my to be mh
  
  #masses = masses[:,:2]
  #print(masses)

  return masses, limits, limits_no_sys, limits_no_res_bkg, limits_no_dy_bkg
    
def plotLimits(mX, limits, ylabel, nominal_masses, savename=None, xlabel=r"$m_X$"):
  plt.scatter(mX, limits[2], zorder=3, facecolors="none", edgecolors="blue")
  plt.scatter(mX[np.isin(mX, nominal_masses)], limits[2][np.isin(mX, nominal_masses)], zorder=4, facecolors="none", edgecolors="red", label="Nominal masses")
  plt.plot(mX, limits[2], 'b--', zorder=3, label="Expected 95% CL limit")
  plt.fill_between(mX, limits[1], limits[3], zorder=2, facecolor="green", label=r"$\pm$ $1\sigma$")
  plt.fill_between(mX, limits[0], limits[4], zorder=1, facecolor="yellow", label=r"$\pm$ $2\sigma$")
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  
  plt.legend()
  bottom, top = plt.ylim()
  
  mplhep.cms.label(llabel="Work in Progress", data=True, lumi=common.tot_lumi, loc=0)

  if savename!=None:
    plt.savefig(savename+".png")
    plt.savefig(savename+".pdf")
    plt.yscale("log")
    plt.savefig(savename+"_log.png")
    plt.savefig(savename+"_log.pdf")
    plt.clf()

def plotLimitsStackMX(masses, limits, ylabel, nominal_mx, nominal_my, savename):
  label1 = "Nominal masses"
  label2 = "Expected 95% CL limit"
  label3 = r"$\pm$ $1\sigma$"
  label4 = r"$\pm$ $2\sigma$"

  for i, mx in enumerate(np.sort(np.unique(masses[:,0]))):
    my = masses[masses[:,0]==mx,1]
    limits_slice = limits[:,masses[:,0]==mx]
    
    limits_slice = limits_slice[:,np.argsort(my)]
    my = my[np.argsort(my)]
    limits_slice *= 10**i

    plt.scatter(my, limits_slice[2], zorder=3, facecolors="none", edgecolors="blue")
    if mx in nominal_mx:
      plt.scatter(my[np.isin(my, nominal_my)], limits_slice[2][np.isin(my, nominal_my)], zorder=4, facecolors="none", edgecolors="red", label=label1)
    plt.plot(my, limits_slice[2], 'b--', zorder=3, label=label2)
    plt.fill_between(my, limits_slice[1], limits_slice[3], zorder=2, facecolor="green", label=label3)
    plt.fill_between(my, limits_slice[0], limits_slice[4], zorder=1, facecolor="yellow", label=label4)
    label1 = label2 = label3 = label4 = None

    plt.text(my[-1]+10, limits_slice[2][-1], r"$m_X=%d$ GeV $(\times 10^%d)$"%(mx, i), fontsize=12, verticalalignment="center")

  plt.xlabel(r"$m_Y$")
  plt.ylabel(ylabel)  
  plt.legend(ncol=2)
  bottom, top = plt.ylim()
  plt.ylim(limits.min(), limits.max()*10**(i+1))
  left, right = plt.xlim()
  plt.xlim(left, my.max()*1.2)
  #TODO: Fix the lumi call
  mplhep.cms.label(llabel="Work in Progress", data=True, lumi=139, loc=0)

  if savename!=None:
    plt.savefig(savename+".png")
    plt.savefig(savename+".pdf")
    plt.yscale("log")
    plt.savefig(savename+"_log.png")
    plt.savefig(savename+"_log.pdf")
    plt.clf()

def plotLimitsStackMY(masses, limits, ylabel, nominal_mx, nominal_my, savename):
  label1 = "Nominal masses"
  label2 = "Expected 95% CL limit"
  label3 = r"$\pm$ $1\sigma$"
  label4 = r"$\pm$ $2\sigma$"

#  for i, my in enumerate(nominal_my):
  for i, my in enumerate(np.sort(np.unique(masses[:,1]))):
    mx = masses[masses[:,1]==my,0]
    limits_slice = limits[:,masses[:,1]==my]
    
    limits_slice = limits_slice[:,np.argsort(mx)]
    mx = mx[np.argsort(mx)]

    limits_slice *= 10**{i}

    plt.scatter(mx, limits_slice[2], zorder=3, facecolors="none", edgecolors="blue")
    if my in nominal_my:
      plt.scatter(mx[np.isin(mx, nominal_mx)], limits_slice[2][np.isin(mx, nominal_mx)], zorder=4, facecolors="none", edgecolors="red", label=label1)
    plt.plot(mx, limits_slice[2], 'b--', zorder=3, label=label2)
    plt.fill_between(mx, limits_slice[1], limits_slice[3], zorder=2, facecolor="green", label=label3)
    plt.fill_between(mx, limits_slice[0], limits_slice[4], zorder=1, facecolor="yellow", label=label4)
    label1 = label2 = label3 = label4 = None

    plt.text(mx[-1]+10, limits_slice[2][-1], r"$m_Y=%d$ GeV $(\times 10^%d)$"%(my, i), fontsize=12, verticalalignment="center")

  plt.xlabel(r"$m_X$")
  plt.ylabel(ylabel)  
  plt.legend(ncol=2)
  bottom, top = plt.ylim()
  plt.ylim(limits.min(), limits.max()*10**(i+1))
  left, right = plt.xlim()
  plt.xlim(left, 1175)
    
  mplhep.cms.label(llabel="Work in Progress", data=True, lumi=common.tot_lumi, loc=0)

  if savename!=None:
    plt.savefig(savename+".png")
    plt.savefig(savename+".pdf")
    plt.yscale("log")
    plt.savefig(savename+"_log.png")
    plt.savefig(savename+"_log.pdf")
    plt.clf()

def plotLimits2D(masses, limits, ylabel, savename):
  bin_edges = []
  mx = np.sort(np.unique(masses[:,0]))
  my = np.sort(np.unique(masses[:,1]))
  mx_edges = np.array([mx[0] - (mx[1]-mx[0])/2] + list(mx[:-1] + (mx[1:] - mx[:-1])/2) + [mx[-1] + (mx[-1]-mx[-2])/2])
  my_edges = np.array([my[0] - (my[1]-my[0])/2] + list(my[:-1] + (my[1:] - my[:-1])/2) + [my[-1] + (my[-1]-my[-2])/2])

  #spline = spi.interp2d(NMSSM_max_allowed_Y_gg.MX, NMSSM_max_allowed_Y_gg.MY, NMSSM_max_allowed_Y_gg.limit, kind='linear', fill_value=0)
  #max_allowed_values = [spline(m[0], m[1])[0] for m in masses]
  #for i, m in enumerate(masses):
  #  print(m, max_allowed_values[i])
  
  #plt.hist2d(masses[:,0], masses[:,1], [mx_edges, my_edges], weights=limits[2], norm=matplotlib.colors.LogNorm())
  mx_edge_centers = (mx_edges[:-1]+mx_edges[1:])/2
  my_edge_centers = (my_edges[:-1]+my_edges[1:])/2
  interp_masses = []
  interp_limits = []
  for mxi in mx_edge_centers:
    for myi in my_edge_centers:
      interp_masses.append([mxi, myi])
  interp_masses = np.array(interp_masses)
  interp_limits = spi.griddata(masses[:,:2], limits[2], interp_masses, method="linear", fill_value=0)
#  plt.hist2d(interp_masses[:,0], interp_masses[:,1], [mx_edges, my_edges], weights=interp_limits, norm=matplotlib.colors.LogNorm())
  plt.hist2d(interp_masses[:,0], interp_masses[:,1], [mx_edges, my_edges], weights=interp_limits)  
  cbar = plt.colorbar()
  cbar.set_label(ylabel)
  plt.xlabel(r"$m_X$")
  plt.ylabel(r"$m_Y$")

  plt.text(0.25, 0.9, r"$H\rightarrow bb$", transform=plt.gca().transAxes, fontsize=32)
  plt.text(0.05, 0.9, r"$Y\rightarrow\gamma\gamma$", transform=plt.gca().transAxes, fontsize=32)

  mplhep.cms.label(llabel="Work in Progress", data=True, lumi=common.tot_lumi, loc=0)

  plt.savefig(savename+".png")
  plt.savefig(savename+".pdf")
  
  plt.fill_between([250,650],[65,65],[my_edges[-1],my_edges[-1]],facecolor="none",hatch="/",edgecolor="red", label="Limit below maximally\nallowed in NMSSM")
  plt.legend(frameon=True)
  plt.savefig(savename+"_exclude.png")
  plt.savefig(savename+"_exclude.pdf")
  #s = limits[2] < max_allowed_values
  s = limits[2]
  plt.scatter(masses[s,0], masses[s,1], marker='x', color="r", label="Limit below maximally allowed in NMSSM") 
  plt.savefig(savename+"_exclude_points.png")
  plt.savefig(savename+"_exclude_points.pdf")

  plt.clf()

def plotSystematicComparison(mx, limits, limits_no_sys, nominal_masses, savename, xlabel=r"$m_X$"):
  ratio = limits[2]/limits_no_sys[2]
  plt.plot(mx, ratio)
  plt.scatter(mx[np.isin(mx, nominal_masses)], ratio[np.isin(mx, nominal_masses)], zorder=4, facecolors="none", edgecolors="red", label="Nominal masses")
  plt.xlabel(xlabel)
  plt.ylabel("Exp. limit w / wo systematics")

  plt.legend()

  plt.savefig(savename+".png")
  plt.savefig(savename+".pdf")
  plt.clf()

def plotSystematicComparison2(mx, limits, limits_no_sys, ylabel, nominal_masses, savename, xlabel=r"$m_X$" ):
  f, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

  ratio = limits[2]/limits_no_sys[2]
  
  axs[0].plot(mx, limits[2], zorder=3, label="Expected 95% CL limit")
  axs[0].plot(mx, limits_no_sys[2], zorder=3, label="Expected 95% CL limit (no sys)")

  axs[0].set_ylabel(ylabel)
  axs[0].legend()
  axs[0].set_yscale("log")
  
  axs[1].plot(mx, ratio)
  axs[1].scatter(mx[np.isin(mx, nominal_masses)], ratio[np.isin(mx, nominal_masses)], zorder=4, facecolors="none", edgecolors="red", label="Nominal masses")
  axs[1].legend()
  axs[1].set_ylabel("Ratio")
  axs[1].set_xlabel(xlabel)

  plt.savefig(savename+".png")
  plt.savefig(savename+".pdf")
  plt.clf()
  plt.close(f)

def plotResBkgComparison2(mx, limits, limits_no_sys, ylabel, nominal_masses, savename, xlabel=r"$m_X$"):
  f, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

  ratio = limits[2]/limits_no_sys[2]
  
  axs[0].plot(mx, limits[2], zorder=3, label="Expected 95% CL limit")
  axs[0].plot(mx, limits_no_sys[2], zorder=3, label="Expected 95% CL limit (no res bkg)")

  axs[0].set_ylabel(ylabel)
  axs[0].legend()
  axs[0].set_yscale("log")
  
  axs[1].plot(mx, ratio)
  axs[1].scatter(mx[np.isin(mx, nominal_masses)], ratio[np.isin(mx, nominal_masses)], zorder=4, facecolors="none", edgecolors="red", label="Nominal masses")
  axs[1].legend()
  axs[1].set_ylabel("Ratio")
  axs[1].set_xlabel(xlabel)

  plt.savefig(savename+".png")
  plt.savefig(savename+".pdf")
  plt.clf()
  plt.close(f)

def plotDYBkgComparison2(mx, limits, limits_no_sys, ylabel, nominal_masses, savename, xlabel=r"$m_X$"):
  f, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

  ratio = limits[2]/limits_no_sys[2]
  
  axs[0].plot(mx, limits[2], zorder=3, label="Expected 95% CL limit")
  axs[0].plot(mx, limits_no_sys[2], zorder=3, label="Expected 95% CL limit (no dy bkg)")

  axs[0].set_ylabel(ylabel)
  axs[0].legend()
  axs[0].set_yscale("log")
  
  axs[1].plot(mx, ratio)
  axs[1].scatter(mx[np.isin(mx, nominal_masses)], ratio[np.isin(mx, nominal_masses)], zorder=4, facecolors="none", edgecolors="red", label="Nominal masses")
  axs[1].legend()
  axs[1].set_ylabel("Ratio")
  axs[1].set_xlabel(xlabel)

  plt.savefig(savename+".png")
  plt.savefig(savename+".pdf")
  plt.clf()
  plt.close(f)

def tabulateLimits(masses, limits, path):
  df = pd.DataFrame({"MX": masses[:,0], "MY": masses[:,1], "Expected 95% CL Limit [fb]": limits[2]})
  df.sort_values(["MX", "MY"], inplace=True)

  table = tabulate.tabulate(df, headers='keys', floatfmt=".4f")
  
  with open(os.path.join(path, "param_test_results.txt"), "w") as f:
    f.write(table)
  with open(os.path.join(path, "param_test_results.tex"), "w") as f:
    f.write(df.to_latex(float_format="%.4f"))
  df.to_csv(os.path.join(path, "param_test_results.csv"), float_format="%.4f")

def tabulateLimitsAll(masses, limits, limits_no_sys, limits_no_res_bkg, path):
  df = pd.DataFrame({"MX": masses[:,0], "MY": masses[:,1], "Expected 95% CL Limit [fb]": limits[2], "No Systematics": limits_no_sys[2], "No Single SM Higgs": limits_no_res_bkg[2]})
  df.sort_values(["MX", "MY"], inplace=True)

  table = tabulate.tabulate(df, headers='keys', floatfmt=".4f")
  
  with open(os.path.join(path, "limits.txt"), "w") as f:
    f.write(table)
  with open(os.path.join(path, "limits.tex"), "w") as f:
    f.write(df.to_latex(float_format="%.4f", index=False))
  df.to_csv(os.path.join(path, "limits.csv"), float_format="%.4f")

masses, limits, limits_no_sys, limits_no_res_bkg, limits_no_dy_bkg = getLimits(sys.argv[1])
print(masses)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs_br"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs_br_no_sys"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs_no_sys"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_xs_no_res_bkg"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_systematics_comparison"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_res_bkg_comparison"), exist_ok=True)
os.makedirs(os.path.join(sys.argv[2], "Limits_dy_bkg_comparison"), exist_ok=True)


tabulateLimits(masses, limits, os.path.join(sys.argv[2], "Limits_xs_br"))
tabulateLimitsAll(masses, limits, limits_no_sys, limits_no_res_bkg, os.path.join(sys.argv[2], "Limits_xs_br"))
tabulateLimits(masses, limits / BR_HH_GGBB, os.path.join(sys.argv[2], "Limits_xs"))

tabulateLimits(masses, limits_no_sys, os.path.join(sys.argv[2], "Limits_xs_br_no_sys"))
tabulateLimits(masses, limits_no_sys / BR_HH_GGBB, os.path.join(sys.argv[2], "Limits_xs_no_sys"))

tabulateLimits(masses, limits_no_res_bkg, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg"))
tabulateLimits(masses, limits_no_res_bkg / BR_HH_GGBB, os.path.join(sys.argv[2], "Limits_xs_no_res_bkg"))

if len(np.unique(masses[:,1])) == 1: #if 1D (graviton or radion)
  mx = masses[:,0]
  limits = limits[:,np.argsort(mx)]
  limits_no_sys = limits_no_sys[:,np.argsort(mx)]
  limits_no_res_bkg = limits_no_res_bkg[:,np.argsort(mx)]
  limits_no_dy_bkg = limits_no_dy_bkg[:,np.argsort(mx)]

  mx = mx[np.argsort(mx)]

  nominal_masses = [260,270,280,290,300,320,350,400,450,500,550,600,650,700,750,800,900,1000]
  
  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow HH \rightarrow \gamma\gamma bb)$ [fb]"
  plotLimits(mx, limits, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs_br", "limits"))
  plotLimits(mx, limits_no_sys, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_no_sys"))
  plotLimits(mx, limits_no_res_bkg, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_no_res_bkg"))

  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow HH)$ [fb]"
  plotLimits(mx, limits / BR_HH_GGBB, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs", "limits"))
  plotLimits(mx, limits_no_sys / BR_HH_GGBB, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs_no_sys", "limits_no_sys"))
  plotLimits(mx, limits_no_res_bkg / BR_HH_GGBB, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_xs_no_res_bkg", "limits_no_res_bkg"))

  plotSystematicComparison(mx, limits, limits_no_sys, nominal_masses, os.path.join(sys.argv[2], "Limits_systematics_comparison", "125"))
  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow HH \rightarrow \gamma\gamma bb)$ [fb]"
  plotSystematicComparison2(mx, limits, limits_no_sys, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_systematics_comparison", "125_2"))
  plotResBkgComparison2(mx, limits, limits_no_res_bkg, ylabel, nominal_masses, os.path.join(sys.argv[2], "Limits_res_bkg_comparison", "125_2"))

else:
  #nominal_mx = [300,400,500,600,700,800,900,1000]
  #nominal_my = [70,80,90,100,125]
  #nominal_my = [70,80,90,100,125,150,200,250,300,400,500,600,700,800]
  #nominal_my = [125,150,200,250,300,400,500,600,700,800]
  nominal_mx = [240,280,300,320,360,400,450,500,550,600,650,700,750,800,850,900,950,1000]
  nominal_my = [70,80,90,100,125,150,170,190,250,300,350,400,450,500,550,600,650,700,800]

  #only grab the nominal points
  # s = np.isin(masses[:,0], nominal_mx) & np.isin(masses[:,1], nominal_my)
  # limits = limits[:, s]
  # limits_no_sys = limits_no_sys[:, s]
  # masses = masses[s]
  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow YH \rightarrow \gamma\gamma bb)$ [fb]"
  plotLimitsStackMX(masses, limits,             ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br", "limits_stack_mx"))
  plotLimitsStackMX(masses, limits_no_sys,      ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_stack_mx_no_sys"))
  plotLimitsStackMX(masses, limits_no_res_bkg,  ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_stack_mx_no_res_bkg"))
#  plotLimitsStackMY(masses, limits,             ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br", "limits_stack_my"))
#  plotLimitsStackMY(masses, limits_no_sys,      ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_stack_my_no_sys"))
#  plotLimitsStackMY(masses, limits_no_res_bkg,  ylabel, nominal_mx, nominal_my, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_stack_my_no_res_bkg"))
#  plotLimits2D(masses, limits,        ylabel, os.path.join(sys.argv[2], "Limits_xs_br", "limits_2d"))
#  plotLimits2D(masses, limits_no_sys, ylabel, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_2d_no_sys"))
#  plotLimits2D(masses, limits_no_res_bkg, ylabel, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_2d_no_res_bkg"))

  for mx in np.unique(masses[:,0]):
    my = masses[masses[:,0]==mx,1]
    limits_slice = limits[:,masses[:,0]==mx]
    limits_no_sys_slice = limits_no_sys[:,masses[:,0]==mx]
    limits_no_res_bkg_slice = limits_no_res_bkg[:,masses[:,0]==mx]
    limits_no_dy_bkg_slice = limits_no_dy_bkg[:,masses[:,0]==mx]

    limits_slice = limits_slice[:,np.argsort(my)]
    limits_no_sys_slice = limits_no_sys_slice[:,np.argsort(my)]
    limits_no_res_bkg_slice = limits_no_res_bkg_slice[:,np.argsort(my)]
    limits_no_dy_bkg_slice = limits_no_dy_bkg_slice[:,np.argsort(my)]
    my = my[np.argsort(my)]

    if mx in nominal_mx:
      nm = nominal_my
    else:
      nm = []

    print(mx)
    print(my, limits_slice)

    ylabel = r"$\sigma(pp \rightarrow X(%d)) B(X \rightarrow YH \rightarrow \gamma\gamma bb)$ [fb]"%mx
    plotLimits(my, limits_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br", "limits_mx%d"%mx), xlabel=r"$m_Y$")
    plotLimits(my, limits_no_sys_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_mx%d_no_sys"%mx), xlabel=r"$m_Y$")
    plotLimits(my, limits_no_res_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_mx%d_no_res_bkg"%mx), xlabel=r"$m_Y$")
    plotSystematicComparison(my, limits_slice, limits_no_sys_slice, nm, os.path.join(sys.argv[2], "Limits_systematics_comparison", "mx%d"%mx), xlabel=r"$m_Y$")
    plotSystematicComparison2(my, limits_slice, limits_no_sys_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_systematics_comparison", "mx%d_2"%mx), xlabel=r"$m_Y$")
    plotResBkgComparison2(my, limits_slice, limits_no_res_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_res_bkg_comparison", "mx%d_2"%mx), xlabel=r"$m_Y$")
    plotDYBkgComparison2(my, limits_slice, limits_no_dy_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_dy_bkg_comparison", "mx%d_2"%mx), xlabel=r"$m_Y$")

  for my in np.unique(masses[:,1]):
    mx = masses[masses[:,1]==my,0]
    limits_slice = limits[:,masses[:,1]==my]
    limits_no_sys_slice = limits_no_sys[:,masses[:,1]==my]
    limits_no_res_bkg_slice = limits_no_res_bkg[:,masses[:,1]==my]
    limits_no_dy_bkg_slice = limits_no_dy_bkg[:,masses[:,1]==my]


    limits_slice = limits_slice[:,np.argsort(mx)]
    limits_no_sys_slice = limits_no_sys_slice[:,np.argsort(mx)]
    limits_no_res_bkg_slice = limits_no_res_bkg_slice[:,np.argsort(mx)]
    limits_no_dy_bkg_slice = limits_no_dy_bkg_slice[:,np.argsort(mx)]
    mx = mx[np.argsort(mx)]

    if my in nominal_my:
      nm = nominal_mx
    else:
      nm = []

    ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow Y(%d)H \rightarrow \gamma\gamma bb)$ [fb]"%my
    plotLimits(mx, limits_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br", "limits_my%d"%my))
    plotLimits(mx, limits_no_sys_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br_no_sys", "limits_my%d_no_sys"%my))
    plotLimits(mx, limits_no_res_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_xs_br_no_res_bkg", "limits_my%d_no_res_bkg"%my))
    plotSystematicComparison(mx, limits_slice, limits_no_sys_slice, nm, os.path.join(sys.argv[2], "Limits_systematics_comparison", "my%d"%my))
    plotSystematicComparison2(mx, limits_slice, limits_no_sys_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_systematics_comparison", "my%d_2"%my))
    plotResBkgComparison2(mx, limits_slice, limits_no_res_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_res_bkg_comparison", "my%d_2"%my))
    plotDYBkgComparison2(mx, limits_slice, limits_no_dy_bkg_slice, ylabel, nm, os.path.join(sys.argv[2], "Limits_dy_bkg_comparison", "my%d_2"%my))

  
