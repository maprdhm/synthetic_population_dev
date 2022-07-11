#!/bin/bash

# This script must be run with qsub

#$ -cwd -V
#$ -l h_rt=24:00:00
#$ -l h_vmem=10G
#$ -m e
#$ -M m.predhumeau@leeds.ac.uk
#$ -o ./logs
#$ -e ./logs

if [ "$#" != "3" ]; then
  echo "usage: qsub $0 <path> <year> <from>"
  exit 1
fi

python nb2.py $1 $2 $3
