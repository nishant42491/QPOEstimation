import json
from pathlib import Path

import bilby
import celerite
import matplotlib.pyplot as plt
import numpy as np

from QPOEstimation.likelihood import QPOTerm, ExponentialTerm
from QPOEstimation.model.series import PolynomialMeanModel


class InjectionCreator(object):

    def __init__(self, params, injection_mode, sampling_frequency, segment_length,
                 outdir='injection_files', injection_id=0):
        self.params = params
        self.injection_mode = injection_mode
        self.sampling_frequency = sampling_frequency
        self.segment_length = segment_length
        self.outdir = outdir
        self.injection_id = str(injection_id).zfill(2)
        self.create_outdir()

        self.mean_model = PolynomialMeanModel(**self.params_mean)

        self.times = np.linspace(0, self.segment_length, int(self.sampling_frequency * self.segment_length))
        self.n = len(self.times)
        self.dt = self.times[1] - self.times[0]

        self.kernel = self.get_kernel()
        self.yerr = np.ones(self.n)
        self.cov = self.get_cov()
        self.y = self.get_y()

    def create_outdir(self):
        Path(f'{self.outdir}/{self.injection_mode}').mkdir(exist_ok=True, parents=True)

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        if isinstance(params, bilby.core.prior.PriorDict):
            self._params = params.sample()
        else:
            self._params = params

    @property
    def params_mean(self):
        params_mean = dict()
        for param, value in self.params.items():
            if param.startswith('mean:'):
                params_mean[param.replace('mean:', '')] = value
        return params_mean

    @property
    def params_kernel(self):
        params_kernel = dict()
        for param, value in self.params.items():
            if param.startswith('kernel:'):
                params_kernel[param.replace('kernel:', '')] = value
        if self.injection_mode == 'qpo':
            params_kernel['log_b'] = -10
        return params_kernel

    def get_kernel(self):
        if self.injection_mode == "red_noise":
            kernel = ExponentialTerm(**self.params_kernel)
        elif self.injection_mode == "qpo":
            kernel = QPOTerm(**self.params_kernel)
        else:
            kernel = None
        return kernel

    def get_cov(self):
        cov = np.diag(np.ones(self.n))
        taus = np.zeros(shape=(self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                taus[i][j] = np.abs(i - j) * self.dt
        cov += self.kernel.get_value(tau=taus)
        return cov

    def get_y(self):
        self.y = np.random.multivariate_normal(self.mean_model.get_value(self.times), self.cov)
        return self.y

    def save(self):
        np.savetxt(f'{self.outdir}/{self.injection_mode}/{self.injection_id}_data.txt',
                   np.array([self.times, self.y]).T)
        with open(f'{self.outdir}/{self.injection_mode}/{self.injection_id}_params.json', 'w') as f:
            json.dump(self.params, f)

    def plot(self):
        x = np.linspace(self.times[0], self.times[-1], 5000)
        color = "#ff7f0e"
        plt.errorbar(self.times, self.y, yerr=np.ones(self.n), fmt=".k", capsize=0, label='data')
        if self.injection_mode != 'white_nosie':
            gp = celerite.GP(kernel=self.kernel, mean=self.mean_model)
            gp.compute(self.times, self.yerr)
            for param, value in self.params.items():
                gp.set_parameter(param, value)
            pred_mean, pred_var = gp.predict(self.y, x, return_var=True)
            pred_std = np.sqrt(pred_var)
            plt.plot(x, pred_mean, color=color, label='Prediction')
            plt.fill_between(x, pred_mean + pred_std, pred_mean - pred_std,
                             color=color, alpha=0.3, edgecolor="none")

        pred_mean_poly = self.mean_model.get_value(x)
        plt.plot(x, pred_mean_poly, color='green', label='Mean function')
        plt.legend()
        plt.savefig(f'{self.outdir}/{self.injection_mode}/{self.injection_id}_data.pdf')
        plt.show()
        plt.clf()


def create_injection(params, injection_mode, sampling_frequency, segment_length,
                     outdir='injection_files', injection_id=0, plot=False):
    injection_creator = InjectionCreator(params=params, injection_mode=injection_mode,
                                         sampling_frequency=sampling_frequency, segment_length=segment_length,
                                         outdir=outdir, injection_id=injection_id)

    injection_creator.save()
    if plot:
        injection_creator.plot()