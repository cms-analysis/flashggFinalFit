import uproot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np

def plot(path, label):
  f = uproot.open(path)
  scan = f["limit"].arrays(["deltaNLL", "r"])
  r = scan["r"][1:]
  NLL = scan["deltaNLL"][1:]
  plt.plot(r, NLL, label=label)

  return r, NLL

def load(path):
  f = uproot.open(path)
  scan = f["limit"].arrays(["deltaNLL", "r"])
  r = scan["r"][1:]
  NLL = scan["deltaNLL"][1:]
  return r, NLL

limit=float(sys.argv[1])
out_name = sys.argv[2]
no_sys_path = sys.argv[3]
sys_path = sys.argv[4]
fine_path = sys.argv[5]

plot(no_sys_path, "Without systematics")
plot(sys_path, "With systematics")
r, NLL = load(fine_path)

ytop = plt.ylim()[1]
xleft = plt.xlim()[0] + 0.01
plt.plot([limit, limit], [0, 0.8*ytop], 'k--', label="Expected Limit")

plt.text(xleft, 0.95*ytop, "Exp. limit = %.4f"%limit, verticalalignment="top", horizontalalignment="left")
interval = sorted([r[np.argmin(NLL)-1], r[np.argmin(NLL)+1]])
plt.text(xleft, 0.85*ytop, "r_min  = [%.4f, %.4f]"%tuple(interval), verticalalignment="top", horizontalalignment="left")

plt.ylabel("$\Delta$ NLL")
plt.xlabel("r")
plt.legend()
plt.ylim(bottom=0)
plt.savefig("%s.pdf"%out_name)
plt.savefig("%s.png"%out_name)
