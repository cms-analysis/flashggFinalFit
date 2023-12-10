import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import uproot
import sys
import numpy as np
from scipy import interpolate
import subprocess
import os

BR_H_GG = 2.27e-3
BR_H_TT = 6.27e-2
BR_H_BB = 5.84e-1

BR_HH_GGTT = 2 * BR_H_GG * BR_H_TT
BR_HH_GGBB = 2 * BR_H_GG * BR_H_BB

# def getGGTTLimits(collected_plots_path, scalelumi=False):
#   mX = [300,400,500,800,1000]
#   filenames = [collected_plots_path+"radionm%d/higgsCombine_AsymptoticLimit_r.AsymptoticLimits.mH125.root"%m for m in mX]
#   print(filenames)

#   limits = []

#   for filename in filenames:
#     f = uproot.open(filename)
#     limits.append(f["limit/limit"].array(library='np'))

#   limits = np.array(limits).T

#   if scalelumi:
#     limits = limits / np.sqrt(139/59)

#   return mX, limits

def getGGTTLimits(collected_plots_path, scalelumi=False):
  mX = sorted([int(d.split("m")[1]) for d in os.listdir(collected_plots_path)])
  filenames = [collected_plots_path+"radionm%d/higgsCombine_AsymptoticLimit_r_ggtt_resonant_%d.AsymptoticLimits.mH125.root"%(m,m) for m in mX]

  limits = []

  # for filename in filenames:
  #   f = uproot.open(filename)
  #   limits.append(f["limit/limit"].array())

  failed_mX = []
  for mass in mX:
    try:
      f = uproot.open(collected_plots_path+"radionm%d/higgsCombine_AsymptoticLimit_r_ggtt_resonant_%d.AsymptoticLimits.mH125.root"%(mass,mass))
      limits.append(f["limit/limit"].array())
    except Exception as e:
      print(e)
      failed_mX.append(mass)
  print("Failed masses:", failed_mX)

  for mass in failed_mX:
    mX.remove(mass)

  limits = np.array(limits).T

  if scalelumi:
    limits = limits / np.sqrt(139/59)

  return mX, limits


def getGGBBLimits():
  mX = [260, 270, 280, 300, 320, 350, 400, 450, 550, 600, 650, 700, 800, 900, 1000]
  limits = np.array([0.71, 0.70, 0.72, 0.74, 0.69, 0.58, 0.42, 0.30, 0.21, 0.14, 0.14, 0.12, 0.09, 0.08, 0.08])
  return mX, limits

def get2016GGBBLimits(scalelumi=False):
  mX = [300,400,500,800]
  limits = np.array([2.5, 1.35, 0.8, 0.39])

  if scalelumi:
    limits = limits / np.sqrt(139/35.9)

  return mX, limits

def plotLimits(mX, limits, ylabel, savename=None):
  plt.scatter(mX, limits[2], zorder=3, facecolors="none", edgecolors="blue", label="Expected 95% CL limit")
  plt.plot(mX, limits[2], 'b--', zorder=3)
  plt.fill_between(mX, limits[1], limits[3], zorder=2, facecolor="green", label=r"$\pm$ $1\sigma$")
  plt.fill_between(mX, limits[0], limits[4], zorder=1, facecolor="yellow", label=r"$\pm$ $2\sigma$")
  plt.xlabel(r"$m_X$")
  plt.ylabel(ylabel)
  plt.yscale("log")
  plt.legend()
  bottom, top = plt.ylim()
  #plt.ylim(bottom, top*10)
  
  if savename!=None:
    plt.savefig(savepath+savename+".png")
    plt.savefig(savepath+savename+".pdf")
    plt.clf()

def plotCompare(ggtt_mX, ggtt_limits, ggbb_mX, ggbb_limits, savename=None):
  f, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [5, 2]})

  axs[0].scatter(ggtt_mX, ggtt_limits[2], zorder=3, facecolors="none", edgecolors="blue", label="Expected 95% limit")
  axs[0].plot(ggtt_mX, ggtt_limits[2], 'b--', zorder=3)
  axs[0].fill_between(ggtt_mX, ggtt_limits[1], ggtt_limits[3], zorder=2, facecolor="green", label=r"$\pm$ $1\sigma$")
  axs[0].fill_between(ggtt_mX, ggtt_limits[0], ggtt_limits[4], zorder=1, facecolor="yellow", label=r"$\pm$ $2\sigma$")
  
  axs[0].scatter(ggbb_mX, ggbb_limits, zorder=3, facecolors="none", edgecolors="red", label=r"$bb\gamma\gamma$ limit")
  axs[0].plot(ggbb_mX, ggbb_limits, 'r--', zorder=3)

  ggtt_interp = interpolate.interp1d(ggtt_mX, ggtt_limits[2])
  ggbb_interp = interpolate.interp1d(ggbb_mX, ggbb_limits)

  mX_min = max([min(ggtt_mX), min(ggbb_mX)])
  mX_max = min([max(ggtt_mX), max(ggbb_mX)])
  mX_ratio = np.linspace(mX_min, mX_max, 100)
  limit_ratio = ggtt_interp(mX_ratio)/ggbb_interp(mX_ratio)

  axs[1].plot(mX_ratio, limit_ratio)
  target_line = axs[1].plot([mX_min, mX_max], [6, 6], '--', label="target ratio = 6")
  target_line = target_line[0]

  axs[1].set_xlabel(r"$m_X$")
  axs[0].set_ylabel(r"$\sigma(pp \rightarrow X) B(X \rightarrow HH)$ [fb]")
  axs[1].set_ylabel("ratio")  

  axs[0].set_yscale("log")
  handles, labels = axs[0].get_legend_handles_labels()
  handles.append(target_line)
  handles[2], handles[4] = handles[4], handles[2]
  handles[1], handles[3] = handles[3], handles[1]
  axs[0].legend(handles=handles, ncol=2)
  bottom, top = axs[0].set_ylim()
  axs[0].set_ylim(bottom, top*10)

  axs[1].set_ylim(5, 20)

  if savename!=None:
    f.savefig(savepath+savename+".png")
    f.savefig(savepath+savename+".pdf")
    plt.clf()


if __name__=="__main__":
  collected_plots_path = sys.argv[1]
  savepath = "LimitsPlots/"

  ggtt_mX, ggtt_limits = getGGTTLimits(collected_plots_path, scalelumi=True)
  ggbb_mX, ggbb_limits = getGGBBLimits()
  ggbb2016_mX, ggbb2016_limits = get2016GGBBLimits(scalelumi=True)

  print("ggtt limits:")
  print(ggtt_mX)
  print(ggtt_limits[2])
  print(ggtt_limits[2]/BR_HH_GGTT)

  print("ggbb limits:")
  print(ggbb_mX)
  print(ggbb_limits)
  print(ggbb_limits/BR_HH_GGBB)

  print("ggbb 2016 scaled limits")
  print(ggbb2016_mX)
  print(ggbb2016_limits)
  print(ggbb2016_limits/BR_HH_GGBB)


  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow HH \rightarrow \gamma\gamma\tau\tau)$ [fb]"
  plotLimits(ggtt_mX, ggtt_limits, ylabel, "ggtt_limits")

  ylabel = r"$\sigma(pp \rightarrow X) B(X \rightarrow HH)$ [fb]"
  plotLimits(ggtt_mX, ggtt_limits/BR_HH_GGTT, ylabel, "ggtt_limits_BR_scaled")
 
  plotCompare(ggtt_mX, ggtt_limits/BR_HH_GGTT, ggbb_mX, ggbb_limits/BR_HH_GGBB, "compare")
 

