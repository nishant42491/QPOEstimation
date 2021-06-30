#!/bin/bash

#end_time=20
#extensions=($(seq 0 10 480))
#
#sbatch analyse_periodogram_submit.sh -${end_time} ${end_time} 6 red_noise boxcar
#sbatch analyse_periodogram_submit.sh -${end_time} ${end_time} 7 red_noise tukey
#sbatch analyse_periodogram_submit.sh -${end_time} ${end_time} 6 general_qpo boxcar
#sbatch analyse_periodogram_submit.sh -${end_time} ${end_time} 7 general_qpo tukey
#
#
#for i in {1..48}
#do
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 6 red_noise hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 7 red_noise hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 6 general_qpo hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 7 general_qpo hann
#done
#
#for i in {1..45}
#do
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 6 red_noise hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 7 red_noise hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 6 general_qpo hann
#  sbatch analyse_periodogram_submit.sh -$((end_time + extensions[$i])) $((end_time + extensions[$i])) 7 general_qpo hann
#done

start_times=(73000 74700 74900 73000)
end_times=(74700 74900 75800 75800)

for i in {0..3}
do
#  sbatch analyse_periodogram_submit.sh $((start_times[$i])) $((end_times[$i])) red_noise
#  sbatch analyse_periodogram_submit.sh $((start_times[$i])) $((end_times[$i])) general_qpo
  sbatch analyse_periodogram_submit.sh $((start_times[$i])) $((end_times[$i])) broken_power_law
done

#
#extensions=($(seq 0 10 200))
#start_time=-4
#end_time=103
#
#for i in {1..100}
#do
#  sbatch analyse_periodogram_submit.sh $((start_time - extensions[$i])) $((end_time + extensions[$i])) red_noise hann
#  sbatch analyse_periodogram_submit.sh $((start_time - extensions[$i])) $((end_time + extensions[$i])) general_qpo hann
#done