from copy import deepcopy

import numpy as np
from celerite.modeling import Model
from ..stabilisation import bar_lev
import stingray


def burst_envelope(times, amplitude, t_max, sigma, skewness):
    if amplitude == 0:
        return np.zeros(len(times))
    before_burst_indices = np.where(times <= t_max)
    after_burst_indices = np.where(times > t_max)
    envelope = np.zeros(len(times))
    envelope[before_burst_indices] = amplitude * np.exp((times[before_burst_indices] - t_max) / sigma)
    envelope[after_burst_indices] = amplitude * np.exp(-(times[after_burst_indices] - t_max) / sigma / skewness)
    return envelope


def burst_envelope_ps(frequencies, amplitude, t_start, t_max, sigma, skewness):
    delta_freq = frequencies[1] - frequencies[0]
    duration = 1 / delta_freq
    times = np.arange(t_start, t_start + duration, 1 / int(frequencies[-1] * duration))
    envelope = burst_envelope(times=times, amplitude=amplitude, t_max=t_max, sigma=sigma, skewness=skewness)
    lc = stingray.Lightcurve.make_lightcurve(envelope, dt=times[1] - times[0])
    ps = stingray.Powerspectrum(lc)
    return ps


def burst_qpo_model(times, background_rate=0,
                    amplitude_0=0, t_max_0=0, sigma_0=1, skewness_0=1,
                    amplitude_1=0, t_max_1=0, sigma_1=1, skewness_1=1,
                    amplitude_2=0, t_max_2=0, sigma_2=1, skewness_2=1,
                    amplitude_3=0, t_max_3=0, sigma_3=1, skewness_3=1,
                    amplitude_4=0, t_max_4=0, sigma_4=1, skewness_4=1,
                    amplitude_qpo_0=0, phase_0=0, frequency_0=1, t_qpo_0=0, decay_time_0=1,
                    amplitude_qpo_1=0, phase_1=0, frequency_1=1, t_qpo_1=0, decay_time_1=1,
                    **kwargs):
    offset_0 = amplitude_qpo_0
    offset_1 = amplitude_qpo_1
    return \
        burst_envelope(times=times, amplitude=amplitude_0, t_max=t_max_0, sigma=sigma_0, skewness=skewness_0) + \
        burst_envelope(times=times, amplitude=amplitude_1, t_max=t_max_1, sigma=sigma_1, skewness=skewness_1) + \
        burst_envelope(times=times, amplitude=amplitude_2, t_max=t_max_2, sigma=sigma_2, skewness=skewness_2) + \
        burst_envelope(times=times, amplitude=amplitude_3, t_max=t_max_3, sigma=sigma_3, skewness=skewness_3) + \
        burst_envelope(times=times, amplitude=amplitude_4, t_max=t_max_4, sigma=sigma_4, skewness=skewness_4) + \
        qpo_shot(times=times, offset=offset_0, amplitude=amplitude_qpo_0, frequency=frequency_0, t_qpo=t_qpo_0,
                 phase=phase_0, decay_time=decay_time_0) + \
        qpo_shot(times=times, offset=offset_1, amplitude=amplitude_qpo_1, frequency=frequency_1, t_qpo=t_qpo_1,
                 phase=phase_1, decay_time=decay_time_1) + \
        background_rate


def burst_qpo_model_norm(times, background_rate=0,
                         amplitude_0=0, t_max_0=0, sigma_0=1, skewness_0=1,
                         amplitude_1=0, t_max_1=0, sigma_1=1, skewness_1=1,
                         amplitude_2=0, t_max_2=0, sigma_2=1, skewness_2=1,
                         amplitude_3=0, t_max_3=0, sigma_3=1, skewness_3=1,
                         amplitude_4=0, t_max_4=0, sigma_4=1, skewness_4=1,
                         amplitude_qpo_0=0, phase_0=0, frequency_0=1, t_qpo_0=0, decay_time_0=1,
                         amplitude_qpo_1=0, phase_1=0, frequency_1=1, t_qpo_1=0, decay_time_1=1,
                         **kwargs):
    T = times[-1] - times[0]
    nbin = len(times)
    norm = nbin/T
    return burst_qpo_model(times, background_rate,
                           amplitude_0, t_max_0, sigma_0, skewness_0,
                           amplitude_1, t_max_1, sigma_1, skewness_1,
                           amplitude_2, t_max_2, sigma_2, skewness_2,
                           amplitude_3, t_max_3, sigma_3, skewness_3,
                           amplitude_4, t_max_4, sigma_4, skewness_4,
                           amplitude_qpo_0, phase_0, frequency_0, t_qpo_0, decay_time_0,
                           amplitude_qpo_1, phase_1, frequency_1, t_qpo_1, decay_time_1,
                           **kwargs) / norm


def merged_qpo_model(times, amplitude_spike, amplitude_qpo, t_spike, t_qpo, f_qpo, phase, decay_time, skewness):
    if amplitude_spike == 0:
        return np.zeros(len(times))
    before_burst_indices = np.where(times <= t_spike)
    after_burst_indices = np.where(times > t_spike)
    after_qpo_indices = np.where(times > t_qpo)
    envelope = np.zeros(len(times))
    envelope[before_burst_indices] = amplitude_spike * np.exp((times[before_burst_indices] - t_spike) / decay_time)
    envelope[after_burst_indices] = amplitude_spike * np.exp(-(times[after_burst_indices] - t_spike) / decay_time / skewness)
    if amplitude_qpo != 0:
        envelope[after_qpo_indices] += amplitude_qpo * np.cos(2 * np.pi * f_qpo * times[after_qpo_indices] + phase) * np.exp(-(times[after_qpo_indices] - t_spike) / decay_time / skewness)
    return envelope


def merged_qpo_model_multi(
        times, background_rate,
        amplitude_spike_0, amplitude_qpo_0, t_spike_0, t_qpo_0, f_qpo_0, phase_0, decay_time_0, skewness_0,
        amplitude_spike_1, amplitude_qpo_1, t_spike_1, t_qpo_1, f_qpo_1, phase_1, decay_time_1, skewness_1,
        amplitude_spike_2, amplitude_qpo_2, t_spike_2, t_qpo_2, f_qpo_2, phase_2, decay_time_2, skewness_2,
        amplitude_spike_3, amplitude_qpo_3, t_spike_3, t_qpo_3, f_qpo_3, phase_3, decay_time_3, skewness_3,
        amplitude_spike_4, amplitude_qpo_4, t_spike_4, t_qpo_4, f_qpo_4, phase_4, decay_time_4, skewness_4, **kwargs):
    res = merged_qpo_model(times, amplitude_spike_0, amplitude_qpo_0, t_spike_0, t_qpo_0, f_qpo_0, phase_0, decay_time_0, skewness_0) + \
          merged_qpo_model(times, amplitude_spike_1, amplitude_qpo_1, t_spike_1, t_qpo_1, f_qpo_1, phase_1, decay_time_1, skewness_1) + \
          merged_qpo_model(times, amplitude_spike_2, amplitude_qpo_2, t_spike_2, t_qpo_2, f_qpo_2, phase_2, decay_time_2, skewness_2) + \
          merged_qpo_model(times, amplitude_spike_3, amplitude_qpo_3, t_spike_3, t_qpo_3, f_qpo_3, phase_3, decay_time_3, skewness_3) + \
          merged_qpo_model(times, amplitude_spike_4, amplitude_qpo_4, t_spike_4, t_qpo_4, f_qpo_4, phase_4, decay_time_4, skewness_4) + background_rate
    return res


def merged_qpo_model_multi_norm(
        times, background_rate,
        amplitude_spike_0, amplitude_qpo_0, t_spike_0, t_qpo_0, f_qpo_0, phase_0, decay_time_0, skewness_0,
        amplitude_spike_1, amplitude_qpo_1, t_spike_1, t_qpo_1, f_qpo_1, phase_1, decay_time_1, skewness_1,
        amplitude_spike_2, amplitude_qpo_2, t_spike_2, t_qpo_2, f_qpo_2, phase_2, decay_time_2, skewness_2,
        amplitude_spike_3, amplitude_qpo_3, t_spike_3, t_qpo_3, f_qpo_3, phase_3, decay_time_3, skewness_3,
        amplitude_spike_4, amplitude_qpo_4, t_spike_4, t_qpo_4, f_qpo_4, phase_4, decay_time_4, skewness_4, **kwargs):
    res = merged_qpo_model_multi(times, background_rate,
                           amplitude_spike_0, amplitude_qpo_0, t_spike_0, t_qpo_0, f_qpo_0, phase_0, decay_time_0, skewness_0,
                           amplitude_spike_1, amplitude_qpo_1, t_spike_1, t_qpo_1, f_qpo_1, phase_1, decay_time_1, skewness_1,
                           amplitude_spike_2, amplitude_qpo_2, t_spike_2, t_qpo_2, f_qpo_2, phase_2, decay_time_2, skewness_2,
                           amplitude_spike_3, amplitude_qpo_3, t_spike_3, t_qpo_3, f_qpo_3, phase_3, decay_time_3, skewness_3,
                           amplitude_spike_4, amplitude_qpo_4, t_spike_4, t_qpo_4, f_qpo_4, phase_4, decay_time_4, skewness_4)
    T = times[-1] - times[0]
    nbin = len(times)
    norm = nbin/T
    return res / norm


def qpo_shot(times, offset, amplitude, frequency, t_qpo, phase, decay_time):
    if amplitude == 0:
        return np.zeros(len(times))
    res = np.zeros(len(times))
    idxs = [np.where(times >= t_qpo)][0]
    res[idxs] = amplitude*(1 + np.cos(2 * np.pi * frequency * (times[idxs] - t_qpo) + phase)) * np.exp(
        -(times[idxs] - t_qpo) / decay_time)
    return res


def zeroed_qpo_shot(times, start_time, amplitude, decay_time, frequency, phase, **kwargs):
    t = deepcopy(times)
    t -= times[0]
    start_time -= times[0]
    qpo = np.zeros(len(t))
    if decay_time > 0:
        indices = np.where(t > start_time)
        qpo[indices] = amplitude * np.exp(-(t[indices] - start_time) / decay_time) * \
                       np.cos(2 * np.pi * frequency * (t[indices] - start_time) + phase)
    if decay_time <= 0:
        indices = np.where(t < start_time)
        qpo[indices] = amplitude * np.exp(-(t[indices] - start_time) / decay_time) * \
                       np.cos(2 * np.pi * frequency * (t[indices] - start_time) + phase)

    return qpo


def two_sided_qpo_shot(times, peak_time, amplitude, decay_time, frequency, phase, **kwargs):
    t = deepcopy(times)
    t -= times[0]
    peak_time -= times[0]
    qpo = np.zeros(len(t))
    falling_indices = np.where(t > peak_time)
    qpo[falling_indices] = amplitude * np.exp(-(t[falling_indices] - peak_time) / decay_time) * \
                   np.cos(2 * np.pi * frequency * (t[falling_indices] - peak_time) + phase)
    rising_indices = np.where(t < peak_time)
    qpo[rising_indices] = amplitude * np.exp(+(t[rising_indices] - peak_time) / decay_time) * \
                   np.cos(2 * np.pi * frequency * (t[rising_indices] - peak_time) + phase)
    return qpo


def norm_gaussian(x, mu, sigma, **kwargs):
    return np.exp(-(x - mu) ** 2. / (2 * sigma ** 2.)) / np.sqrt(2 * np.pi * sigma ** 2)


def sine_model(times, amplitude, frequency, phase, **kwargs):
    t = deepcopy(times)
    t -= times[0]
    return amplitude * np.sin(2*np.pi*t*frequency + phase)


def sine_gaussian(t, mu, sigma, amplitude, frequency, phase, **kwargs):
    return sine_model(times=t, amplitude=amplitude, frequency=frequency, phase=phase) \
           * norm_gaussian(x=t, mu=mu, sigma=sigma)


def exponential_background(times, tau, offset, **kwargs):
    return np.exp(times/tau) + offset


def sine_gaussian_with_background(times, tau, offset, amplitude, mu, sigma, frequency, phase, **kwargs):
    return exponential_background(times=times, tau=tau, offset=amplitude+offset) + \
           sine_gaussian(t=times, amplitude=amplitude, mu=mu, sigma=sigma, frequency=frequency, phase=phase) * np.sqrt(2 * np.pi * sigma ** 2)


def two_frequency_model(time_array, mu_1, mu_2, sigma_1, sigma_2, amplitude_1, amplitude_2, frequency_1, frequency_2, phase_1, phase_2, **kwargs):
    t = deepcopy(time_array)
    signal_1 = sine_gaussian(t, mu_1, sigma_1, amplitude_1, frequency_1, phase_1)
    signal_2 = sine_gaussian(t, mu_2, sigma_2, amplitude_2, frequency_2, phase_2)
    signal = signal_1 + signal_2
    signal[np.where(signal < 0)] = 0
    return signal


class PolynomialMeanModel(Model):

    parameter_names = ("a0", "a1", "a2", "a3", "a4")

    def get_value(self, t):
        times = t - t[0] - 0.5
        return self.a0 + self.a1 * times + self.a2 * times**2 + self.a3 * times**3 + self.a4 * times**4

    def compute_gradient(self, *args, **kwargs):
        pass


class ExponentialMeanModel(Model):
    parameter_names = ("tau", "offset")

    def get_value(self, t):
        return exponential_background(times=t, tau=self.tau, offset=self.offset)

    def compute_gradient(self, *args, **kwargs):
        pass


class ExponentialStabilisedMeanModel(Model):
    parameter_names = ("tau", "offset")

    def get_value(self, t):
        return bar_lev(exponential_background(times=t, tau=self.tau, offset=self.offset))

    def compute_gradient(self, *args, **kwargs):
        pass
