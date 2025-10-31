import os
import subprocess
from multiprocessing import Pool
import glob
import errno
import time

# Define an array of input masses
input_masses = [120, 125, 130]

# Define an array of eras
eras = ["preEE", "postEE"]

# Define an array of production modes and corresponding process strings
production_modes = [
    ("ggh", "GluGluHtoGG"),
    ("vbf", "VBFHtoGG"),
    ("vh", "VHtoGG"),
    ("tth", "ttHtoGG")
]

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Function to run the command
def run_process(args):
    mass, era, mode, process, path_to_root_files = args
    output_dir = "../input_output_2022{}".format(era)
    safe_mkdir(output_dir)  # Create output directory if it doesn't exist
    
    # Construct the command as a single string
    cmd = "python3 trees2ws.py --inputMass {mass} --productionMode {mode} --year 2022{era} --doSystematics --doInOutSplitting --inputConfig config_2022.py --inputTreeFile '{path_to_root_files}/{process}_M-{mass}_{era}/'*.root --outputWSDir {output_dir}".format(
        mass=mass, mode=mode, era=era, path_to_root_files=path_to_root_files, process=process, output_dir=output_dir)
    
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print("Error running process for mass {}, era {}, and mode {}:".format(mass, era, mode))
            print(stderr)
        else:
            print("Process for mass {}, era {}, and mode {} completed successfully.".format(mass, era, mode))
    except Exception as e:
        print("Exception running process for mass {}, era {}, and mode {}:".format(mass, era, mode))
        print(str(e))

# Main function to parallelize tasks
def main(path_to_root_files):
    
    num_workers = 24 # masses x 2 eras x 4 production modes = 24
    pool = Pool(processes=num_workers)
    tasks = [
        (mass, era, mode, process, path_to_root_files)
        for mode, process in production_modes
        for era in eras
        for mass in input_masses
    ]
    
    # Lets benchmark the time:
    start_time = time.time()  

    pool.map(run_process, tasks)

    end_time = time.time()  

    # Calculate and print the duration
    duration = end_time - start_time
    print("Process {:.2f} seconds.".format(duration))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: <script.py> <path_to_root_files>")
        sys.exit(1)
    
    path_to_root_files = sys.argv[1]
    main(path_to_root_files)