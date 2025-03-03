# coding: utf-8

"""
Law example tasks to demonstrate HTCondor workflows at CERN.

In this file, some really basic tasks are defined that can be inherited by
other tasks to receive the same features. This is usually called "framework"
and only needs to be defined once per user / group / etc.
"""


import os
import math

import luigi
import law


# the htcondor workflow implementation is part of a law contrib package
# so we need to explicitly load it
law.contrib.load("htcondor")
law.contrib.load("slurm")


class Task(law.Task):
    """
    Base task that we use to force a version parameter on all inheriting tasks, and that provides
    some convenience methods to create local file and directory targets at the default data path.
    """

    version = luigi.Parameter()

    def store_parts(self):
        return (self.__class__.__name__, self.version)

    def local_path(self, *path):
        # DATA_PATH is defined in setup.sh
        output_folder = "$ANALYSIS_PATH/law/remote"
        # os.mkdir(output_folder)
        parts = (output_folder,) + self.store_parts() + path
        return os.path.join(*parts)

    def local_target(self, *path):
        return law.LocalFileTarget(self.local_path(*path))


class HTCondorWorkflow(law.htcondor.HTCondorWorkflow):
    """
    Batch systems are typically very heterogeneous by design, and so is HTCondor. Law does not aim
    to "magically" adapt to all possible HTCondor setups which would certainly end in a mess.
    Therefore we have to configure the base HTCondor workflow in law.contrib.htcondor to work with
    the CERN HTCondor environment. In most cases, like in this example, only a minimal amount of
    configuration is required.
    """

    htcondor_max_runtime = law.DurationParameter(
        default=16.0,
        unit="h",
        significant=False,
        description="maximum runtime; default unit is hours; default: 1",
    )
    transfer_logs = luigi.BoolParameter(
        default=True,
        significant=False,
        description="transfer job logs to the output directory; default: True",
    )
    
    htcondor_job_kwargs_submit = {"spool": True}

    def htcondor_output_directory(self):
        # the directory where submission meta data should be stored
        return law.LocalDirectoryTarget(self.local_path())

    def htcondor_bootstrap_file(self):
        # each job can define a bootstrap file that is executed prior to the actual job
        # configure it to be shared across jobs and rendered as part of the job itself
        bootstrap_file = law.util.rel_path(__file__, "bootstrap.sh")
        return law.JobInputFile(bootstrap_file, share=True, render_job=True)

    def htcondor_job_config(self, config, job_num, branches):
        # render_variables are rendered into all files sent with a job
        config.render_variables["analysis_path"] = os.getenv("ANALYSIS_PATH")
        config.render_variables["law_dir"] = os.getenv("LAW_DIR")

        # configure to run in a "el7" container
        # https://batchdocs.web.cern.ch/local/submit.html#os-selection-via-containers
        config.custom_content.append(("MY.WantOS", "el9"))
        
        config.custom_content.append(("RequestMemory", 4)) # 4GB

        # maximum runtime
        config.custom_content.append(("+MaxRuntime", int(math.floor(self.htcondor_max_runtime * 3600)) - 1))

        # copy the entire environment
        config.custom_content.append(("getenv", "false"))
        
        # config.custom_content.append(("+AccountingGroup", "'group_u_CMS.u_zh.users'"))
        config.custom_content.append(("+AccountingGroup", '"group_u_CMS.u_zh.users"'))

        # the CERN htcondor setup requires a "log" config, but we can safely set it to /dev/null
        # if you are interested in the logs of the batch system itself, set a meaningful value here
        config.custom_content.append(("log", "/dev/null"))

        return config


class SlurmWorkflow(law.slurm.SlurmWorkflow):
    """
    Batch systems are typically very heterogeneous by design, and so is Slurm. Law does not aim
    to "magically" adapt to all possible Slurm setups which would certainly end in a mess.
    Therefore we have to configure the base Slurm workflow in law.contrib.slurm to work with
    the Maxwell cluster environment. In most cases, like in this example, only a minimal amount of
    configuration is required.
    """

    slurm_partition = luigi.Parameter(
        default="standard",
        significant=False,
        description="target queue partition; default: standard",
    )
    slurm_max_runtime = law.DurationParameter(
        default=2,
        unit="h",
        significant=False,
        description="the maximum job runtime; default unit is hours; default: 1h",
    )

    def slurm_output_directory(self):
        # the directory where submission meta data should be stored
        return law.LocalDirectoryTarget(self.local_path())

    def slurm_bootstrap_file(self):
        # each job can define a bootstrap file that is executed prior to the actual job
        # configure it to be shared across jobs and rendered as part of the job itself
        bootstrap_file = law.util.rel_path(__file__, "bootstrap.sh")
        return law.JobInputFile(bootstrap_file, share=True, render_job=True)
    
    def htcondor_log_directory(self):
        # the directory where submission meta data should be stored
        return law.LocalDirectoryTarget(self.local_path())

    def slurm_job_config(self, config, job_num, branches):
        # render_variables are rendered into all files sent with a job
        config.render_variables["analysis_path"] = os.getenv("ANALYSIS_PATH")
        config.render_variables["law_dir"] = os.getenv("LAW_DIR")

        # useful defaults
        job_time = law.util.human_duration(
            seconds=law.util.parse_duration(self.slurm_max_runtime, input_unit="h") - 1,
            colon_format=True,
        )
        
        config.custom_content.append(("time", job_time))
        config.custom_content.append(("mem", 8000))
        config.custom_content.append(("nodes", 1))

        return config