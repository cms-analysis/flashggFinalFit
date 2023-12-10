import uproot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

def getLimit(r, NLL):
  best_r = 9999
  best_diff = 9999
  for i in range(len(NLL)):
    diff = abs(NLL[i]-2)
    if diff < best_diff:
      best_r = r[i]
      best_diff = diff
  return best_r      

f = uproot.open(sys.argv[1])

scan = f["limit"].arrays(["deltaNLL", "r"])
#print(scan["r"])
#print(scan['deltaNLL'])

r = scan["r"][1:]
NLL = scan["deltaNLL"][1:]

r_lim = getLimit(r, NLL)

plt.plot(r, NLL)
plt.plot([0,5],[0.5,0.5],'k--')
plt.plot([0,5],[2,2],'k--')
plt.plot([r_lim,r_lim], [0,5], 'r--', label="r = %.2f"%r_lim)
plt.ylabel("$\Delta$ NLL")
plt.xlabel("r")
plt.ylim(0, 5)
plt.legend()
#plt.show()
plt.savefig("NLL_scan.pdf")
plt.savefig("NLL_scan.png")
