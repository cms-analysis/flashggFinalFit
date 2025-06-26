#!/usr/bin/env bash

action() {

    cd /net/data_cms3a-1/spaeh/private/PhD/analyses/partial_Run3_differential/Hgg-PartialRun3-3A-ETH-Analysis/fitting/CMSSW_14_1_0_pre4/src/flashggFinalFit
    export ANALYSIS_PATH="$(pwd)"
    # The following source of cmsset_default.sh is needed on architectures other than lxplus, when the default cms commands are not sourced at startup
    export VO_CMS_SW_DIR="/cvmfs/cms.cern.ch"
    source $VO_CMS_SW_DIR/cmsset_default.sh
    cmsenv
    source setup.sh
    local shell_is_zsh="$( [ -z "${ZSH_VERSION}" ] && echo "false" || echo "true" )"
    local this_file="$( ${shell_is_zsh} && echo "${(%):-%x}" || echo "${BASH_SOURCE[0]}" )"
    local this_dir="$( cd "$( dirname "${this_file}" )" && pwd )"

    if [ ! -d "${PWD}/law/install_dir" ] || [ -z "$(ls -A "${PWD}/law/install_dir")" ]; then
        PYTHONUSERBASE="${PWD}/law/install_dir" pip3 install --user --no-cache-dir --force-reinstall "git+https://github.com/JaLuka98/law.git@master"
    else
        echo "Directory ${PWD}/law/install_dir already exists and is not empty. Using local law installation..."
    fi

    export INSTALL_DIR="${PWD}/law/install_dir"
    export PYTHONPATH="${PYTHONPATH}:${INSTALL_DIR}/lib/python3.9/site-packages"
    export PATH="${INSTALL_DIR}/bin:${PATH}"

    export PYTHONPATH="${this_dir}:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Background:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Trees2WS:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Trees2WS/T2WSTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Signal:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Signal/tools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/commonTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Datacard:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Datacard/datacardTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Combine:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Plots/Spectra:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Plots/Spectra/fidXS:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/law/:${PYTHONPATH}"
    export LAW_HOME="${this_dir}/law/.law"
    export LAW_CONFIG_FILE="${this_dir}/law/law.cfg"
    export LAW_DIR="${this_dir}/law"

    source "$( law completion )" ""
}
action
