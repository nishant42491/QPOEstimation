import bilby
import json
import numpy as np
from copy import deepcopy
from QPOEstimation.prior.minimum import MinimumPrior
reslist = []
samples = []
injection_mode = 'qpo'
polynomial_max = 10
min_log_a = -2
max_log_a = 1
min_log_c = -1

band_minimum = 5
band_maximum = 64

segment_length = 1
sampling_frequency = 256
t = np.linspace(0, segment_length, int(sampling_frequency * segment_length))

likelihood_model = 'gaussian_process'

for i in range(2200, 2300):
    try:
        with open(f'injection_files/qpo/{i}_params.json') as f:
            injection_params = json.load(f)

        if likelihood_model == 'gaussian_process_windowed':
            res = bilby.result.read_in_result(f'injection_5_64Hz_normal_qpo/qpo/results/{i}_gaussian_process_windowed_result.json')
        else:
            res = bilby.result.read_in_result(f'injection_5_64Hz_normal_qpo/qpo/results/{i}_gaussian_process_result.json')
            # del injection_params['window_minimum']
            # del injection_params['window_maximum']

        reslist.append(res)
        reslist[-1].injection_parameters = injection_params
    except (OSError, FileNotFoundError) as e:
        print(e)
        continue


if likelihood_model == 'gaussian_process_windowed':
    bilby.result.make_pp_plot(results=reslist, filename='qpo_pp_plot_windowed_new.png')
else:
    bilby.result.make_pp_plot(results=reslist, filename='qpo_pp_plot_unwindowed_new.png')