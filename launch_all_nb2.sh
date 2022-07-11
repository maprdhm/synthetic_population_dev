#!/bin/bash

for i in {0..1400000..100000}
do
 qsub launch_nb2.sh /nobackup/geompr/westmidlands/synthetic_pop_SPENSER 2021 $i
done
