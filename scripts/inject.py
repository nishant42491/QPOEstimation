import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
import matplotlib.pyplot as plt

import bilby
import celerite
import matplotlib
import numpy as np

from QPOEstimation.likelihood import QPOTerm, ExponentialTerm, ZeroedQPOTerm
from QPOEstimation.model.series import PolynomialMeanModel
from QPOEstimation.injection import create_injection
from QPOEstimation.prior.minimum import MinimumPrior

if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum_id", default=0, type=int)
    parser.add_argument("--maximum_id", default=100, type=int)
    parser.add_argument("--injection_mode", default="qpo", choices=["qpo", "white_noise", "red_noise"], type=str)
    parser.add_argument("--likelihood_model", default="gaussian_process", choices=["gaussian_process", "gaussian_process_windowed"], type=str)
    parser.add_argument("--sampling_frequency", default=256, type=int)
    parser.add_argument("--polynomial_max", default=10, type=int)
    parser.add_argument("--plot", default=False, type=bool)
    parser.add_argument("--segment_length", default=1.0, type=float)
    parser.add_argument("--outdir", default='injection_files', type=str)
    args = parser.parse_args()
    minimum_id = args.minimum_id
    maximum_id = args.maximum_id
    injection_mode = args.injection_mode
    likelihood_model = args.likelihood_model
    sampling_frequency = args.sampling_frequency
    polynomial_max = args.polynomial_max
    plot = args.plot
    segment_length = args.segment_length
    outdir = args.outdir
else:
    matplotlib.use('Qt5Agg')
    minimum_id = 0
    maximum_id = 1000

    sampling_frequency = 256
    polynomial_max = 10
    injection_mode = "qpo"
    likelihood_model = "gaussian_process_windowed"
    plot = True
    segment_length = 1
    outdir = 'testing'


# def conversion_function(sample):
#     out_sample = deepcopy(sample)
#     out_sample['decay_constraint'] = out_sample['kernel:log_c'] - out_sample['kernel:log_f']
#     return out_sample
t = np.linspace(0, segment_length, int(sampling_frequency * segment_length))
min_log_a = -2
max_log_a = 1
min_log_c = -1

band_minimum = 5
band_maximum = 64

priors = bilby.core.prior.ConditionalPriorDict()
priors['mean:a0'] = bilby.core.prior.Uniform(minimum=-polynomial_max, maximum=polynomial_max, name='mean:a0')
priors['mean:a1'] = bilby.core.prior.Uniform(minimum=-polynomial_max, maximum=polynomial_max, name='mean:a1')
priors['mean:a2'] = bilby.core.prior.Uniform(minimum=-polynomial_max, maximum=polynomial_max, name='mean:a2')
priors['mean:a3'] = bilby.core.prior.Uniform(minimum=-polynomial_max, maximum=polynomial_max, name='mean:a3')
priors['mean:a4'] = bilby.core.prior.Uniform(minimum=-polynomial_max, maximum=polynomial_max, name='mean:a4')

if injection_mode == "white_noise":
    kernel = celerite.terms.JitterTerm(log_sigma=-20)
    priors['kernel:log_sigma'] = bilby.core.prior.DeltaFunction(peak=-20, name='log_sigma')
elif injection_mode == "qpo":
    kernel = QPOTerm(log_a=0.1, log_b=-10, log_c=-0.01, log_f=3)
    priors['kernel:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a, name='log_a')
    priors['kernel:log_b'] = bilby.core.prior.DeltaFunction(peak=-10, name='log_b')
    priors['kernel:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum), name='log_c')
    priors['kernel:log_f'] = bilby.core.prior.Uniform(minimum=np.log(band_minimum), maximum=np.log(band_maximum),
                                                      name='log_f')
    priors['decay_constraint'] = bilby.core.prior.Constraint(minimum=-1000, maximum=0.0, name='decay_constraint')
elif injection_mode == "zeroed_qpo":
    kernel = ZeroedQPOTerm(log_a=0.1, log_c=-0.01, log_f=3)
    priors['kernel:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a, name='log_a')
    priors['kernel:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum), name='log_c')
    priors['kernel:log_f'] = bilby.core.prior.Uniform(minimum=np.log(band_minimum), maximum=np.log(band_maximum),
                                                      name='log_f')
    priors['decay_constraint'] = bilby.core.prior.Constraint(minimum=-1000, maximum=0.0, name='decay_constraint')
elif injection_mode == "red_noise":
    kernel = ExponentialTerm(log_a=0.1, log_c=-0.01)
    priors['kernel:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a, name='log_a')
    priors['kernel:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum), name='log_c')
elif injection_mode == "mixed":
    kernel = QPOTerm(log_a=0.1, log_b=-10, log_c=-0.01, log_f=3) + ExponentialTerm(log_a=0.1, log_c=-0.01)
    priors['kernel:terms[0]:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a,
                                                               name='terms[0]:log_a')
    priors['kernel:terms[0]:log_b'] = bilby.core.prior.DeltaFunction(peak=-10, name='terms[0]:log_b')
    priors['kernel:terms[0]:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum),
                                                               name='terms[0]:log_c')
    priors['kernel:terms[0]:log_f'] = bilby.core.prior.Uniform(minimum=np.log(band_minimum),
                                                               maximum=np.log(band_maximum), name='terms[0]:log_f')
    priors['kernel:terms[1]:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a,
                                                               name='terms[1]:log_a')
    priors['kernel:terms[1]:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum),
                                                               name='terms[1]:log_c')
    priors['decay_constraint'] = bilby.core.prior.Constraint(minimum=-1000, maximum=0.0, name='decay_constraint')
elif injection_mode == "zeroed_mixed":
    kernel = ZeroedQPOTerm(log_a=0.1, log_c=-0.01, log_f=3) + ExponentialTerm(log_a=0.1, log_c=-0.01)
    priors['kernel:terms[0]:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a,
                                                               name='terms[0]:log_a')
    priors['kernel:terms[0]:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum),
                                                               name='terms[0]:log_c')
    priors['kernel:terms[0]:log_f'] = bilby.core.prior.Uniform(minimum=np.log(band_minimum),
                                                               maximum=np.log(band_maximum), name='terms[0]:log_f')
    priors['kernel:terms[1]:log_a'] = bilby.core.prior.Uniform(minimum=min_log_a, maximum=max_log_a,
                                                               name='terms[1]:log_a')
    priors['kernel:terms[1]:log_c'] = bilby.core.prior.Uniform(minimum=min_log_c, maximum=np.log(band_maximum),
                                                               name='terms[1]:log_c')
    priors['decay_constraint'] = bilby.core.prior.Constraint(minimum=-1000, maximum=0.0, name='decay_constraint')
else:
    raise ValueError('Recovery mode not defined')

def conversion_function(sample):
    out_sample = deepcopy(sample)
    if 'kernel:log_c' in sample.keys():
        out_sample['decay_constraint'] = out_sample['kernel:log_c'] - out_sample['kernel:log_f']
    else:
        out_sample['decay_constraint'] = out_sample['kernel:terms[0]:log_c'] - out_sample['kernel:terms[0]:log_f']
    return out_sample

if likelihood_model == "gaussian_process_windowed":
    priors['window_minimum'] = bilby.core.prior.Beta(minimum=t[0], maximum=t[-1], alpha=1, beta=2, name='window_minimum')
    priors['window_maximum'] = MinimumPrior(minimum=t[0], maximum=t[-1], order=1, reference_name='window_minimum', name='window_maximum', minimum_spacing=0.5)
    def window_conversion_func(params):
        params['window_maximum'] = params['window_minimum'] + params['window_size']
        if injection_mode in ['qpo', 'zeroed_qpo', 'mixed', 'zeroed_mixed']:
            params = conversion_function(sample=params)
        return params
    if injection_mode in ['qpo', 'zeroed_qpo', 'mixed', 'zeroed_mixed']:
        priors.conversion_function = conversion_function
else:
    if injection_mode in ['qpo', 'zeroed_qpo', 'mixed', 'zeroed_mixed']:
        priors.conversion_function = conversion_function




for injection_id in range(minimum_id, maximum_id):
    params = priors.sample()
    while np.isinf(priors.ln_prob(params)):
        params = priors.sample()
    Path(f'injection_files/{injection_mode}').mkdir(exist_ok=True, parents=True)
    create_injection(params=params, injection_mode=injection_mode, sampling_frequency=sampling_frequency,
                     segment_length=segment_length, outdir=outdir, injection_id=injection_id, plot=plot,
                     likelihood_model=likelihood_model)

#
#
# params['mean:a0'] = 0
# params['mean:a1'] = 0
# params['mean:a2'] = 0
# params['mean:a3'] = 0
# params['mean:a4'] = 0

# log_as = np.linspace(maximum_log_a, maximum_log_a, 10)
# log_cs = np.linspace(minimum_log_c, minimum_log_c, 10)
# log_fs = [np.log(20)] * 10
#
# for injection_id in range(minimum_id, maximum_id):
#     bilby.core.utils.logger.info(f"ID: {injection_id}")
#     log_a = log_as[int(str(injection_id%1000).zfill(3)[1])]
#     log_c = log_cs[int(str(injection_id%1000).zfill(3)[2])]
    # log_f = log_fs[int(str(injection_id).zfill(3)[0])]
    # log_f = np.log(20)
    #
    # params['kernel:log_a'] = log_a
    # params['kernel:log_c'] = log_c
    #
    # if injection_mode == "qpo":
    #     params['kernel:log_b'] = -10
    #     params['kernel:log_f'] = log_f
    #
