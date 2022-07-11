#!/bin/bash

# This script must be run with qsub

#$ -cwd -V
#$ -l h_rt=48:00:00
#$ -l h_vmem=10G
#$ -m e
#$ -M m.predhumeau@leeds.ac.uk
#$ -o ./logs
#$ -e ./errors

if [ "$#" != "2" ]; then
  echo "usage: qsub $0 <path> <year>"
  exit 1
fi

python nb4.py $1 $2
