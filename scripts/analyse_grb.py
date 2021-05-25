import numpy as np
import bilby
from QPOEstimation.result import GPResult
from QPOEstimation.model.celerite import power_qpo
import matplotlib.pyplot as plt
import matplotlib
# matplotlib.use('Qt5Agg')

evidence_dict = dict()
evidence_err_dict = dict()

res_dict = {}

linestyle_dict = dict(fred='solid', skew_gaussian='dotted', fred_norris='dashed', fred_norris_extended='dashdot')
label_dict_mean = dict(fred='skew exp.', fred_norris='FRED', fred_norris_extended='FRED-x', skew_gaussian='skew gaus.')
label_dict_kernel = dict(general_qpo='qpo+rn', red_noise='rn')

plt.figure(figsize=(6.4, 6.4))
for mean_model in ['fred', 'fred_norris', 'fred_norris_extended', 'skew_gaussian']:
    print(mean_model)
    for recovery_mode in ['general_qpo', 'red_noise']:
        evidences = []
        evidence_errs = []
        res_list = []
        for n_component in range(1, 4):
            try:
                res = GPResult.from_json(
                    outdir=f'GRB090709A_swift/select_time/{recovery_mode}/'
                           f'gaussian_process/results/',
                    label=f'-4.0_103.0_{n_component}_{mean_model}s')
                if recovery_mode == 'general_qpo':
                    res_list.append(res)
                evidences.append(res.log_evidence)
                evidence_errs.append(res.log_evidence_err)
                print(f"{recovery_mode}\t{n_component}\t{res.log_evidence}\t{res.posterior.iloc[-1]['log_likelihood']}")
            except Exception as e:
                print(e)
                evidences.append(np.nan)
                evidence_errs.append(np.nan)
        if recovery_mode == 'general_qpo':
            res_dict[mean_model] = res_list
        evidence_dict[recovery_mode] = np.array(evidences)
        evidence_err_dict[recovery_mode] = np.array(evidence_errs)
    print()

    for k, v in evidence_dict.items():
        color_dict = dict(general_qpo="blue", red_noise="red")
        plt.plot(np.arange(len(v)), np.array(v), label=f"{label_dict_mean[mean_model]},  {label_dict_kernel[k]}",
                 color=color_dict[k], linestyle=linestyle_dict[mean_model])

plt.xlabel('Number of flare components')
plt.ylabel(f'ln Z')
plt.xticks(ticks=[0, 1, 2], labels=[1, 2, 3])
plt.ylim(88, 103)
plt.legend(ncol=2)
plt.savefig(f'GRB_Ln_Z_plot.png')
plt.show()


for mean_model, res_list in res_dict.items():
    for i, res in enumerate(res_list):
        n_component = 1 + i
        log_a_samples = np.array(res.posterior['kernel:terms[0]:log_a'])
        log_c_samples = np.array(res.posterior['kernel:terms[0]:log_c'])
        log_f_samples = np.array(res.posterior['kernel:terms[0]:log_f'])
        power_samples = np.log(
            power_qpo(a=np.exp(log_a_samples), c=np.exp(log_c_samples), f=np.exp(log_f_samples)))
        plt.hist(power_samples, bins="fd", density=True, histtype='step',
                 label=f"{n_component} {label_dict_mean[mean_model]} flares")
plt.xlabel()
plt.ylabel("Normalised PDF")
plt.legend()
plt.savefig(f"GRB_qpo_power_hist.png")
plt.clf()
