# Final Fits (higgsdnafinalfit)

This is the branch for using final fits with the output of HiggsDNA using the [Luigi Analysis Workflow (law)](https://arxiv.org/abs/2402.17949).

First make sure that you can run CMSSW v14 and run 

```bash
source setup.sh
law index --verbose
```

## Configuring the Analysis

Our law implementation of FinalFits uses a central YAML file located in the subfolder `./config` with the following structure `<year>_inclusive.yml` for the inclusive analysis and `<year>_<variable>.yml` for the differential analysis. These files unify the many `.py` config files found in the FinalFit subfolders. Currently only the year `2022` is available, along with the variables `PTH`,`rapidity`,`Njets2p5` and `ptJ0`.

## Notes about the law implementation

The law implementation of the finalfits framework has some intricacies that will be explained in the following.
If you do not care about this at the moment, skip ahead to the section about "Running the Analysis".

### Implementation

todo

### Modules, Tasks, Subtasks

The command `law index --verbose` gives you an overview of the analysis chain.
You will see that there are modules and tasks.
For example, you will see
```
module 'Trees2WS.law_trees2ws', 2 task(s):
    - Trees2WS
    - Trees2WSSingleProcess
```
The logic here is that `Trees2WS` is a valid `law` task that can be run by executing `law run Trees2WS`.
The task is defined as a class in `../Trees2WS/law_trees2ws.py`.
You will notice that we also have a class `Trees2WSSingleProcess`, which also appears as a task in the module.
Colloquially, we call this a subtask, since it is run when asking `law` to perform the `Trees2WS` task.
This can be seen in the line
```
tasks.append(Trees2WSSingleProcess(input_paths=path_to_root_files, era=era, apply_mass_cut=mass_cut, mass_cut_range=mass_cut_r, year=f"{self.year}{era}", doSystematics=doSystematics, doDiffSplitting=doDiffSplitting, doSTXSSplitting=doSTXSSplitting, doInOutSplitting=doInOutSplitting, output_dir=current_output_path, variable=var, version=f"v{i}", workflow=config['execution'], batch_flavor=self.batch_flavor))
```
in the requirements of the `Tree2WS` task class.
Technically, this defines the individual `Trees2WSSingleCategory` executions as requirements.
The `Trees2WS` task, which just consists of bookkeeping (copying everything into `ws_signal`) can only proceed when the single category tasks are all finished.

This structure leads to the behaviour that the "Supertasks" do not rely so much on batch submissions, which is why they do not receive `law` workflow classes as arguments.
However, the subtasks do and they can be conveniently submitted to a batch system for suitable scaleout (see also the subsection about "Running locally or via batch").

### Scheduling

`law` can use both a central, remote scheduler and local scheduling for each batch job.
Both have advantages and disadvantges.
The remote scheduler allows more control and oversight over the whole process, but it is more work to set up and it might be prone for issues.
Local scheduling means that each individual job acquires and manages its resources after it is submitted by the nanny process.
This means less overhead, although the overall control is reduced.
We recommend using a local scheduler as a first resort.
This is already realised as the default setting by the following lines in the `law.cfg`:
```
[luigi_core]

local_scheduler: True
```

If you want to use a remote scheduler, please adjust to
```
local_scheduler: False
scheduler_host: <your_machine>
scheduler_port: 8082 
```
Then, to work with this remote scheduler, you have to start it in another shell (it will be blocked) on the same machine by `luigid --port 8080 --address 0.0.0.0`.
Then, you can tell `law` to use this remote scheduler to manage the jobs by `law run <task_name> <other argumnts> --scheduler-host lxbatch08.physik.rwth-aachen.de --scheduler-port 8082`.

### Running locally or via batch

The `law` package can be understood as a HEP-ready wrapper for the workflow management package `luigi`.
Therefore, it offers local submission as well as batch submission.

A taks can be submitted locally by using `--batch-flavor local`.
In this context, locally means that the individual processes will run on the machine from which you execute the `law run` command.
This does not necessarily mean that all dependencies will be run locally, though!
Take a look at your config, e.g., `../config/2023_PTH.yml`.
There, search for `execution:`.
You will see that you can toggle the batch submission for individual steps in the analysis chain.
`law` will check this option when launching dependency subtasks after submitting a "Supertask".
For example, running
```
law run Trees2WS --variable PTH --year 2023 --batch-flavor local
```
will execute the `Trees2WS` task locally on your machine, but if `execution: 'htcondor'` is set for the `trees2wsCfg`, then the single category conversion of the trees to workspaces will be scaled out to htcondor, which you might want to do to accelerate the process if your machine is not powerful.

Note that the `--batch-flavor` command-line argument to `law run <task>` does not do anything except when it is set to `slurm/psi`.
This is caused by specific requiremnts of the PSI T3 computing infrastructure.

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

to produce the RooWorkspace input for Combine, as well as the first blinded NLL scans.

Once ready for unblinding, one can produce stage 1 to 3 by calling:

```
./law_run_unblind.sh <differential_variable>
```

As soon as the (un)blinded fits are produced, one can start the production of the (un)blinded differential spectra with:

```
law run CreateDiffSpectra --variable <differential_variable> --is-unblinded (True)False
```
