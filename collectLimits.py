import os
import json
from collections import OrderedDict as od


def findMasses(lines):
  masses = []
  for line in lines:
    mass = int(line.split("/")[1].split("m")[1])
    if mass not in masses:
      masses.append(mass)
  return masses

os.system('grep "Expected" CollectedPlots/*/*.txt > ggtt_limits.txt')
with open("ggtt_limits.txt", "r") as f:
  lines = f.read().split("\n")

masses = findMasses(lines)

all_limits = od()

for line in lines:
  limits = od()
  limits["nominal"] = [-1,-1,-1,-1,-1]
  limits["nominal"] = [-1,-1,-1,-1,-1]
  limits["nominal"] = [-1,-1,-1,-1,-1]
  limits["nominal"] = [-1,-1,-1,-1,-1]
  limits["nominal"] = [-1,-1,-1,-1,-1]