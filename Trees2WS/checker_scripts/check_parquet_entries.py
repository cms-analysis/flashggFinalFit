import pandas as pd
import glob
import awkward as ak
import uproot

#path_to_merged_parquet = "/net/data_cms3a-1/daumann/Hgg-PartialRun3-3A-ETH-Analysis/postprocessing/2024_signal_vanilla_fiducial_25_samples/merged/GluGluHtoGG_M-125_2024/nominal/cat0_merged.parquet"

#df_merged = pd.read_parquet(path_to_merged_parquet, engine="pyarrow")

#print( df_merged["fiducialGeometricFlag"] )

### check the post processed stuff ...
path_post_processed_samples = "/net/data_cms3a-1/daumann/Hgg-PartialRun3-3A-ETH-Analysis/postprocessing/outputs/Preliminary_2024_MC_16_10_25/mc/inclusive/root/*"
paths = glob.glob(path_post_processed_samples)

for path in paths:
    final_path = glob.glob(path + "/*.root")
    if len(final_path) != 1:
        print( 'Error here: ', path )
        continue
    merged_root = uproot.open(final_path[0])
    size_keys =  len(merged_root.keys()) 
    print(path.split("/")[-1], size_keys)
    if size_keys != 52:
        print( path.split("/")[-1] )
        print("alarm! Size: ", size_keys)
        for key in merged_root.keys():
            print(key)
    #print( path.split("/")[-1].split("_")[0] )
    #print( root['DiphotonTree/ggh_125_13TeV_cat0;1']['fiducialGeometricFlag'].values() )

#merged_root = uproot.open(path_post_processed_samples)
#print( len(merged_root.keys()) )
#print(merged_root['DiphotonTree/ggh_125_13TeV_cat0;1']['fiducialGeometricFlag'].values() )

exit()

uncs = "/net/data_cms3a-1/daumann/Hgg-PartialRun3-3A-ETH-Analysis/HiggsDNA/runner_files/2024/base_processor/Samples_2024_signal_50_samples/GluGluHtoGG_M-125_2024/*"
uncs_path = glob.glob(uncs)

for unc_path in uncs_path:

    path = unc_path + "/*.parquet" #f'/net/data_cms3a-1/daumann/Hgg-PartialRun3-3A-ETH-Analysis/HiggsDNA/runner_files/2024/base_processor/Samples_2024_signal_50_samples/GluGluHtoGG_M-125_2024/{uncs_path}/*.parquet'

    paths = glob.glob(path)

    # Tell pandas explicitly to use pyarrow
    df = pd.concat([pd.read_parquet(p, engine="pyarrow") for p in paths], ignore_index=True)

    #for key in df.keys():
    #    print(key)
    print( unc_path.split("/")[-1] )
    print( "fiducialGeometricFlag",  len(df["fiducialGeometricFlag"]) )
    
    