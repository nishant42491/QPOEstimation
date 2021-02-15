import bilby
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from QPOEstimation.stabilisation import bar_lev
# matplotlib.use("Qt5Agg")
from copy import deepcopy

segments = np.arange(0, 8)
mean_log_bfs = []

n_periods = 47
period_one_log_bf_data = []
period_two_log_bf_data = []

band_minimum = 5
band_maximum = 64

pulse_period = 7.56
segment_step = 0.945
segment_length = 2.8
data_mode = "smoothed_residual"
likelihood_model = "gaussian_process_windowed"
alpha = 0.02

if band_maximum <= 64:
    sampling_frequency = 256
elif band_maximum <= 128:
    sampling_frequency = 512
else:
    sampling_frequency = 1024

band = f'{band_minimum}_{band_maximum}Hz'
suffix = ''

outdir = f'sliding_window_{band}_{data_mode}'

if data_mode == 'smoothed':
    data = np.loadtxt(f'data/sgr1806_{sampling_frequency}Hz_exp_smoothed_alpha_{alpha}.dat')
elif data_mode == 'smoothed_residual':
    data = np.loadtxt(f'data/sgr1806_{sampling_frequency}Hz_exp_residual_alpha_{alpha}.dat')
else:
    data = np.loadtxt(f'data/sgr1806_{sampling_frequency}Hz.dat')

times = data[:, 0]
counts = data[:, 1]


for period in range(n_periods):
    log_bfs_general_qpo = []
    mean_frequency_qpo = []
    std_frequency_qpo = []
    mean_frequency_mixed = []
    std_frequency_mixed = []

    for run_id in range(len(segments)):
        try:
            # res_white_noise = bilby.result.read_in_result(f"{outdir}/period_{period}/white_noise/results/{run_id}_{likelihood_model}_result.json")
            res_red_noise = bilby.result.read_in_result(f"{outdir}/period_{period}/red_noise/results/{run_id}_{likelihood_model}_result.json")
            res_general_qpo = bilby.result.read_in_result(f"{outdir}/period_{period}/general_qpo/results/{run_id}_{likelihood_model}_result.json")
            log_bf_general_qpo = res_general_qpo.log_bayes_factor - res_red_noise.log_bayes_factor

            log_f_samples_mixed = np.array(res_general_qpo.posterior['kernel:terms[0]:log_f'])
            frequency_samples_mixed = np.exp(log_f_samples_mixed)
            mean_frequency_mixed.append(np.mean(frequency_samples_mixed))
            std_frequency_mixed.append(np.std(frequency_samples_mixed))

        except Exception as e:
            print(e)
            log_bf_general_qpo = np.nan
            mean_frequency_qpo.append(np.nan)
            std_frequency_qpo.append(np.nan)
        log_bfs_general_qpo.append(log_bf_general_qpo)

        print(f"{period} {run_id} zeroed mixed: {log_bf_general_qpo}")

    np.savetxt(f'{outdir}/log_bfs_period_mixed_{period}', np.array(log_bfs_general_qpo))
    np.savetxt(f'{outdir}/mean_frequencies_{period}', np.array(mean_frequency_qpo))
    np.savetxt(f'{outdir}/std_frequencies_{period}', np.array(std_frequency_qpo))

    xs = np.arange(len(segments))
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('segment start time [s]')
    ax1.set_ylabel('ln BF', color=color)
    ax1.plot(xs, log_bfs_general_qpo, color=color, ls='solid', label='One QPO vs white noise')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('frequency [Hz]', color=color)  # we already handled the x-label with ax1
    ax2.plot(xs, mean_frequency_qpo, color=color)
    mean_frequency_qpo = np.array(mean_frequency_qpo)
    std_frequency_qpo = np.array(std_frequency_qpo)
    plt.fill_between(xs, mean_frequency_qpo + std_frequency_qpo, mean_frequency_qpo - std_frequency_qpo, color=color, alpha=0.3,
                     edgecolor="none")
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.legend()
    plt.savefig(f'{outdir}/log_bfs_period_{period}')
    plt.clf()
