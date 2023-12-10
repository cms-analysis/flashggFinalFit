import sys
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def plotGrid(masses, finer_masses=None):
  mx = [int(m.split("mx")[1].split("my")[0]) for m in masses]
  my = [int(m.split("my")[1]) for m in masses]
  plt.scatter(mx, my, marker="o")
  plt.savefig("grid.pdf")
  if finer_masses is not None:
    mx = [int(m.split("mx")[1].split("my")[0]) for m in finer_masses]
    my = [int(m.split("my")[1]) for m in finer_masses]
    plt.scatter(mx, my, marker=".")
  plt.savefig("grid_fine.pdf")
  plt.clf()

# def getToFitMY(step_sf, m, masses):
#   mx = int(m.split("mx")[1].split("my")[0])
#   my = int(m.split("my")[1])
#   mys = sorted([int(mass.split("my")[1]) for mass in masses if int(mass.split("mx")[1].split("my")[0]) == mx ])
#   if len(mys) == 1:
#     print(my)
#     exit()

#   assert len(np.unique(mys)) == len(mys)

#   res = lambda mgg: (mgg/125.) * 1.3

#   i = mys.index(my)

#   step = int(math.floor(res(my) * step_sf)) 
#   if step == 0: 
#     step = 0.5
#   if i == 0:
#     my_next = mys[i+1]
#     mid_point = (my_next+my)/2

#     #print(step, my_next, mid_point)
#     to_fit_my = [str(my+step*i) for i in range(int(math.ceil((mid_point-my)/step))+1)]
#   elif i == len(mys) - 1:
#     my_last = mys[i-1]
#     mid_point = (my+my_last)/2

#     #print(step, my_last, mid_point)
#     to_fit_my = [str(my-step*i) for i in range(int(math.ceil((my-mid_point)/step))+1)][::-1]
#   else:
#     my_last = mys[i-1]
#     my_next = mys[i+1]
#     mid_point_last = (my+my_last)/2
#     mid_point_next = (my_next+my)/2

#     #print(step, my_last, my_next, mid_point_last, mid_point_next)
#     to_fit_my = [str(my-step*i) for i in range(1, int(math.ceil((my-mid_point_last)/step))+1)][::-1]
#     to_fit_my += [str(my+step*i) for i in range(int(math.ceil((mid_point_next-my)/step))+1)]

#   return to_fit_my

def getToFitMY(step_sf, m, masses):
  mx = int(m.split("mx")[1].split("my")[0])
  my = int(m.split("my")[1])
  all_mys = [int(mass.split("my")[1]) for mass in masses]
  mys = sorted(list(set(all_mys)))
  if len(mys) == 1:
    print(my)
    exit()

  mys_to_keep = []
  this_mxs = np.array([int(mass.split("mx")[1].split("my")[0]) for mass in masses if "my%d"%my in mass])
  for trial_my in mys:
    trial_mxs = np.array([int(mass.split("mx")[1].split("my")[0]) for mass in masses if "my%d"%trial_my in mass])
    if mx in trial_mxs:
      mys_to_keep.append(trial_my)
      continue
    
    closest_mx = this_mxs[np.argsort(abs(this_mxs-mx))][:3]
    min_mx, max_mx = closest_mx.min(), closest_mx.max()
    if sum((trial_mxs > min_mx) & (trial_mxs < max_mx)).sum() > 0:
      mys_to_keep.append(trial_my)

    print(trial_my)
    print(trial_mxs)
    print(min_mx, max_mx)
    print(mys_to_keep)

  #print(mys_to_keep)
  mys = sorted(mys_to_keep)

  assert len(np.unique(mys)) == len(mys)

  res = lambda mgg: (mgg/125.) * 1.3

  i = mys.index(my)

  step = int(math.floor(res(my) * step_sf)) 
  if step == 0: 
    step = 0.5
  if i == 0:
    my_next = mys[i+1]
    mid_point = (my_next+my)/2

    #print(step, my_next, mid_point)
    to_fit_my = [str(my+step*i) for i in range(int(math.ceil((mid_point-my)/step))+1)]
  elif i == len(mys) - 1:
    my_last = mys[i-1]
    mid_point = (my+my_last)/2

    #print(step, my_last, mid_point)
    to_fit_my = [str(my-step*i) for i in range(int(math.ceil((my-mid_point)/step))+1)][::-1]
  else:
    my_last = mys[i-1]
    my_next = mys[i+1]
    mid_point_last = (my+my_last)/2
    mid_point_next = (my_next+my)/2

    #print(step, my_last, my_next, mid_point_last, mid_point_next)
    to_fit_my = [str(my-step*i) for i in range(1, int(math.ceil((my-mid_point_last)/step))+1)][::-1]
    to_fit_my += [str(my+step*i) for i in range(int(math.ceil((mid_point_next-my)/step))+1)]

  return to_fit_my

step_sf = float(sys.argv[1])
m = sys.argv[2]
masses = sys.argv[3:]

#plotGrid(masses)

to_fit_my = getToFitMY(step_sf, m, masses)
print(" ".join(to_fit_my))

# finer_masses = []
# for m in masses:
#   mx = int(m.split("mx")[1].split("my")[0])
#   to_fit_my = getToFitMY(step_sf, m, masses)
#   to_fit_my = [int(float(n)) for n in to_fit_my]
#   finer_masses += ["mx%dmy%d"%(mx, myi) for myi in to_fit_my]

# #print(finer_masses)
# #plotGrid(masses)
# plotGrid(masses, finer_masses)

