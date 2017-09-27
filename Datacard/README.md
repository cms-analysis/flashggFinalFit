# Datacard Script
This is where the datacard for use in the `combine` tool  later..

## Datacard workflow

The workflow looks like this:
* Generate the datacard using `./makeParametricModelDatacardFLASHgg.py`

## Usage

You can use the script as follows:
```
./makeParametricModelDatacardFLASHgg.py -i <signal files at 125 separated by commas>  -o <output name of datacard> -p <comma separated list fo preocesses> -c <comma spearated list of tags/cats> --photonCatScales <photon energy scale cats> --photonCatSmears <photon energy smear cats> --isMultiPdf  
```

If the signal workspaces are split by STXS Stage 0 process, as for the main analysis, then use the option `--doSTXS`

For the HIG-16-040 paper, a new WG1 2017 uncertainty scheme will be used for ggH theory uncertainties. This results in a different nuisance scheme - the datacard can be constructed appropriately using the `--newGghScheme` option (off by default).
