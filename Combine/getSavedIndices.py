import uproot
import sys
f=uproot.open(sys.argv[1])["limit"]

indices = filter(lambda x: "index" in x, f.keys())
to_print = ""
for index in indices:
  to_print += ",%s=%d"%(index, f[index].array())
print(to_print)
