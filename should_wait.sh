#!/usr/bin/env bash

while [[ -n $(qstat | grep "something") ]]; do
  qstat
  echo "Still jobs"
  sleep 1
done
