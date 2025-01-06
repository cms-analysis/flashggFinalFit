# Final Fits (higgsdnafinalfit)

This is the branch for using final fits with the output of HiggsDNA using the [Luigi Analysis Workflow (law)](https://arxiv.org/abs/2402.17949).

First make sure that you can run CMSSW v14 and run 

```bash
source setup.sh
law index --verbose
```

## Configuring the Analysis

Our law implementation of FinalFits uses a central YAML file located in the subfolder `./config` with the following structure `<year>_inclusive.yml` for the inclusive analysis and `<year>_<variable>.yml` for the differential analysis. These files unify the many `.py` config files found in the FinalFit subfolders. Currently only the year `2022` is available, along with the variables `PTH`,`rapidity`,`Njets2p5` and `ptJ0`.


## Running the Analysis

In order to run the analysis, one simply have to execute

```
law run EarlyRun3 --workers 4
```

This launches the analysis chain using 4 worker nodes.

Currently, there is a [bug](https://github.com/riga/law/issues/193) in law which prevents launching jobs from HTCondor nodes. As a workaround, all the necessary steps have to run sequentially (while the computationally intensive ones can still be put to condor) for the **differential** results. The **inclusive** results for the cross section can be computed locally.
In order to start the differentials, one has to call:

```
./law_run_htcondor.sh <differential_variable>
```
