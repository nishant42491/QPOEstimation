#!/bin/bash

#for segment in {0..27}
#do
#  for period in {0..46}
#  do
#    sbatch submit.sh $segment $period gaussian_process 64 128
#  done
#done

#for i in {0..51}
#do
#  sbatch submit.sh ${i} gaussian_process 5 64
#done
#for i in {0..45}
#do
#  sbatch submit.sh ${i} gaussian_process 64 128
#done
#for i in {0..29}
#do
#  sbatch submit.sh ${i} gaussian_process 128 256
#done

#
#for i in {0..22}
#do
#  sbatch submit.sh ${i} gaussian_process 10 40
#  sbatch submit.sh ${i} periodogram 40 128
#done
#
#for i in {0..11}
#do
#  sbatch submit.sh ${i} gaussian_process 40 128
#  sbatch submit.sh ${i} periodogram 40 128
#done
for i in {0..999}
do
  sbatch submit.sh ${i}
done