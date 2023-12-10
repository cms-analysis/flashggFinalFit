import json
import sys

with open(sys.argv[1], "r") as f:
  impacts = json.load(f)

new_impacts = {"POIs": impacts["POIs"], "method": impacts["method"], "params":[]}

for impact in impacts["params"]:
  if impact["type"] != "Unconstrained":
    new_impacts["params"].append(impact)

with open(sys.argv[2], "w") as f:
  json.dump(new_impacts, f, indent=4) 
