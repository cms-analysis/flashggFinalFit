import os
import math
from optparse import OptionParser
import json
import numpy as np
import pandas as pd
import uproot
import matplotlib
import glob
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (12.5,10)

def get_options():
    parser = OptionParser()
    parser.add_option('--use-mplhep', dest='use_mplhep', default=False, action="store_true")
    return parser.parse_args()
(opt,args) = get_options()

if opt.use_mplhep:
    import mplhep
    mplhep.style.use("CMS")

if not os.path.isdir("plots"): os.system("mkdir plots")

file_dict = {
    "fixed":"fit_fixed.root",
    "envelope":"fit_envelope.root"
}

Z_points = np.linspace(0,3,100)
p_gaus = []
for Z in Z_points: p_gaus.append( (1-math.erf(Z/math.sqrt(2)))/2 )
p_gaus = np.array( p_gaus )

z_thr = 4

# Make figure for all plots
fig = plt.figure( figsize=(12,12) )

f_fixed = uproot.open(file_dict['fixed'])
f_envelope = uproot.open(file_dict['envelope'])

z_fixed = np.array( f_fixed['limit'].arrays('limit')['limit'] )
z_envelope = np.array( f_envelope['limit'].arrays('limit')['limit'] )

# Drop failed fits with incorrect Z values
z_fixed = z_fixed[z_fixed<z_thr]
z_envelope = z_envelope[z_envelope<z_thr]

N_fixed = len(z_fixed)
N_envelope = len(z_envelope)

print("N_fixed = %g, N_envelope = %g"%(N_fixed,N_envelope))

p_fixed, p_envelope = [], []
err_fixed, err_envelope = [], []
for Z in Z_points:
    k_fixed = np.sum(z_fixed>Z, dtype='float')
    k_envelope = np.sum(z_envelope>Z, dtype='float')
    p_fixed.append( k_fixed/N_fixed )
    p_envelope.append( k_envelope/N_envelope )
    # Bayesian error estimate for efficiency
    err_fixed.append( np.sqrt( (((k_fixed+1)*(k_fixed+2))/((N_fixed+2)*(N_fixed+3))) - (((k_fixed+1)*(k_fixed+1))/((N_fixed+2)*(N_fixed+2))) ) )
    err_envelope.append( np.sqrt( (((k_envelope+1)*(k_envelope+2))/((N_envelope+2)*(N_envelope+3))) - (((k_envelope+1)*(k_envelope+1))/((N_envelope+2)*(N_envelope+2))) ) )

p_fixed = np.array( p_fixed )
p_envelope = np.array( p_envelope )
err_fixed = np.array( err_fixed )
err_envelope = np.array( err_envelope )

axs = []
left, width=0.08,0.82
bottom = 0.1
height = 0.18
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)
bottom = 0.32
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)
height = 0.4
bottom = 0.55
ax = fig.add_axes([left,bottom,width,height])
axs.append(ax)

axs[0].plot(Z_points, p_fixed/p_fixed, ls="-", color='red', linewidth=2 )
axs[0].fill_between(Z_points, (p_fixed-err_fixed)/p_fixed, (p_fixed+err_fixed)/p_fixed,  color='salmon', alpha=0.2 )
axs[0].plot(Z_points, p_envelope/p_fixed, ls="-", color='mediumblue', linewidth=2 )
axs[0].fill_between(Z_points, (p_envelope-err_envelope)/p_fixed, (p_envelope+err_envelope)/p_fixed,  color='cornflowerblue', alpha=0.2 )

axs[0].fill_between(Z_points, 0.8, 0.9,  color='orange', alpha=0.2 )
axs[0].fill_between(Z_points, 0.9, 1.1,  color='limegreen', alpha=0.2, label="$<10$%" )
axs[0].fill_between(Z_points, 1.1, 1.2,  color='orange', alpha=0.2, label="$<20$%" )
axs[0].legend(loc="upper left", fontsize=12, frameon=True)

axs[0].set_ylim(0.5,1.5)
axs[0].set_xlim(0,2.5)

axs[0].set_ylabel("Ratio to fixed", fontsize=16)
axs[0].set_xlabel("Z-score", fontsize=20)


axs[1].plot(Z_points, p_fixed/p_gaus, ls="-", color='red', linewidth=2 )
axs[1].fill_between(Z_points, (p_fixed-err_fixed)/p_gaus, (p_fixed+err_fixed)/p_gaus,  color='salmon', alpha=0.2 )
axs[1].plot(Z_points, p_envelope/p_gaus, ls="-", color='mediumblue', linewidth=2 )
axs[1].fill_between(Z_points, (p_envelope-err_envelope)/p_gaus, (p_envelope+err_envelope)/p_gaus,  color='cornflowerblue', alpha=0.2 )
axs[1].plot(Z_points, p_gaus/p_gaus, ls="--", color='black', linewidth=2 )
axs[1].fill_between(Z_points, 0.8, 0.9,  color='orange', alpha=0.2 )
axs[1].fill_between(Z_points, 0.9, 1.1,  color='limegreen', alpha=0.2, label="$<10$%" )
axs[1].fill_between(Z_points, 1.1, 1.2,  color='orange', alpha=0.2, label="$<20$%" )
axs[1].legend(loc="upper left", fontsize=12, frameon=True)


axs[1].set_ylim(0.5,1.5)
axs[1].set_xlim(0,2.5)

axs[1].set_ylabel("Ratio to Gaussian", fontsize=16)
axs[1].set_xticklabels(labels=[], fontsize=0)


axs[2].plot(Z_points, 100*p_fixed, ls="-", label="Toys (fixed)", color='red', linewidth=2 )
axs[2].fill_between(Z_points, 100*(p_fixed-err_fixed), 100*(p_fixed+err_fixed),  color='salmon', alpha=0.2 )
axs[2].plot(Z_points, 100*p_envelope, ls="-", label="Toys (envelope)", color='mediumblue', linewidth=2 )
axs[2].fill_between(Z_points, 100*(p_envelope-err_envelope), 100*(p_envelope+err_envelope),  color='cornflowerblue', alpha=0.2 )
axs[2].plot(Z_points, 100*p_gaus, ls="--", label="Gaussian", color='black', linewidth=2, alpha=0.8 )

axs[2].set_ylim(0.1,100)
axs[2].set_xlim(0,2.5)
axs[2].set_yscale("log")

axs[2].set_ylabel("Type-1 error rate [%]", fontsize=20)
axs[2].legend(loc='best', fontsize=16, frameon=True)

fig.savefig("plots/summary_significance.pdf", bbox_inches="tight")
fig.savefig("plots/summary_significance.png")

axs[1].clear()
axs[2].clear()

fig.clf()
