import uproot
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
from scipy.interpolate import interp1d

hep.style.use("CMS")

def process_scan(file_path):
    # Open the ROOT file
    file = uproot.open(file_path)

    # Access the tree containing the scan results
    tree = file["limit"]

    # Extract the parameter of interest (e.g., r) and the likelihood values (-2 Delta NLL)
    poi_values = tree["r"].array()
    nll_values = tree["deltaNLL"].array()

    # Convert the uproot arrays to numpy arrays for easier handling
    # Also slice away the first value because it is best fit and we do not want an extra line
    poi_values = np.array(poi_values)[1:]
    nll_values = np.array(nll_values)[1:]

    nll_values = 2 * nll_values  # convert to -2 Delta NLL

    return poi_values, nll_values

# Process the scans
poi_values_statonly, nll_values_statonly = process_scan("../Combine/higgsCombine.observed_scan.statonly.MultiDimFit.mH125.38.root")
poi_values_with_syst, nll_values_with_syst = process_scan("../Combine/higgsCombine.observed_scan.with_syst.MultiDimFit.mH125.38.root")

theory_uncertainty = 3.80
do_xsec = True
if do_xsec:
    theory_value = 67.80
    poi_values_statonly *= theory_value
    poi_values_with_syst *= theory_value
else:
    theory_value = 1.0
    theory_uncertainty = theory_uncertainty / 67.80

# Plot the likelihood scans
plt.plot(poi_values_statonly, nll_values_statonly, color='blue', ls='dashdot', label='Observed - Stat. only')
plt.plot(poi_values_with_syst, nll_values_with_syst, color='black', linestyle='-', lw=2, label='Observed')

# Add the theoretical prediction with uncertainty
y_theo_max = 3.0
plt.plot([theory_value, theory_value], [0, y_theo_max], color='red', linestyle='-', linewidth=3, label=r'MG5_aMC@NLO, NNLOPS')
plt.fill_betweenx(y=[0, y_theo_max], x1=theory_value - theory_uncertainty, x2=theory_value + theory_uncertainty, color='none', edgecolor='red', facecolor='none', hatch='//')

# Grey line at -2dLL=1
plt.axhline(1.0, color='grey', linestyle='--', linewidth=2)

# Find the crossing points at -2 Δln(L) = 1 using interpolation for the with_syst scan
crossing_indices = np.where(np.diff(np.sign(nll_values_with_syst - 1)))[0]
crossing_points = []
for idx in crossing_indices:
    x0, x1 = poi_values_with_syst[idx], poi_values_with_syst[idx + 1]
    y0, y1 = nll_values_with_syst[idx], nll_values_with_syst[idx + 1]
    crossing_points.append(x0 + (1 - y0) * (x1 - x0) / (y1 - y0))

# Add grey lines for the ±1 sigma intervals
for cp in crossing_points:
    plt.plot([cp, cp], [0, 1], color='grey', linestyle='--')

# Customize the plot
plt.xlabel(r'$\sigma_{\mathrm{fid}}$ (fb)')
plt.ylabel(r'$-2 \Delta \ln L$')
plt.xlim(62.5, 93.5)
plt.ylim(0, 2.25)
plt.legend(loc='upper right')
hep.cms.label('Preliminary', data=True, lumi=34.7, com=13.6)
plt.tight_layout()

# Save the plot
plt.savefig("likelihood_scan_with_theory_prediction.pdf")
