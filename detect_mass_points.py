import os
import sys

def detect_mass_points(root_file_dir):
  root_files = os.listdir(root_file_dir)
  masses = []
  for f in root_files:
    masses.append("mx" + f.split("cat")[0].split("mx")[-1])
  masses = sorted(set(masses))
  return masses

if __name__ == '__main__':
  masses = detect_mass_points(sys.argv[1])
  for m in masses:
    print(m)
