#!/usr/bin/env bash

# Bootstrap file for batch jobs that is sent with all jobs and
# automatically called by the law remote job wrapper script to find the
# setup.sh file of this example which sets up software and some environment
# variables. The "{{law_dir}}" variable is defined in the workflow
# base tasks in commonTools/framework.py.

action() {
    source "{{law_dir}}/remote_setup.sh" "$@"
}
action "$@"
