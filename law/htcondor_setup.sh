#!/usr/bin/env bash

action() {

    cd /afs/cern.ch/user/n/niharrin/cernbox/PhD/Higgs/CMSSW_14_1_0_pre4/src/flashggFinalFit/law
    cmsenv
    local shell_is_zsh="$( [ -z "${ZSH_VERSION}" ] && echo "false" || echo "true" )"
    local this_file="$( ${shell_is_zsh} && echo "${(%):-%x}" || echo "${BASH_SOURCE[0]}" )"
    local this_dir="$( cd "$( dirname "${this_file}" )" && pwd )"

    # PYTHONUSERBASE="${PWD}/install_dir" pip3 install --user --no-cache-dir --force-reinstall "law"
    # PYTHONUSERBASE="${PWD}/install_dir" pip3 install --user --no-cache-dir --force-reinstall "git+https://github.com/riga/law.git@master"

    if [ ! -d "${PWD}/install_dir" ] || [ -z "$(ls -A "${PWD}/install_dir")" ]; then
        PYTHONUSERBASE="${PWD}/install_dir" pip3 install --user --no-cache-dir --force-reinstall "git+https://github.com/riga/law.git@master"
    else
        echo "Directory ${PWD}/install_dir already exists and is not empty. Using local law installation..."
    fi

    export INSTALL_DIR="${PWD}/install_dir"
    export PYTHONPATH="${PYTHONPATH}:${INSTALL_DIR}/lib/python3.9/site-packages"
    export PATH="${INSTALL_DIR}/bin:${PATH}"

    export PYTHONPATH="${this_dir}:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Background:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Trees2WS:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Trees2WS/T2WSTools:${PYTHONPATH}"
    # export PYTHONPATH="${this_dir}/Trees2WS/tools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Signal:${PYTHONPATH}"
    # export PYTHONPATH="${this_dir}/Signal/SignalTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Signal/tools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/commonTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Datacard:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Datacard/datacardTools:${PYTHONPATH}"
    export PYTHONPATH="${this_dir}/Combine:${PYTHONPATH}"
    export LAW_HOME="${this_dir}/.law"
    export LAW_CONFIG_FILE="${this_dir}/law.cfg"

    export ANALYSIS_PATH="${this_dir}"
    # export ANALYSIS_DATA_PATH="${ANALYSIS_PATH}/data"

    # source "/afs/cern.ch/user/m/mrieger/public/law_sw/setup.sh" ""
    source "$( law completion )" ""
}
action
