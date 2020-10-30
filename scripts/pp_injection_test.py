import bilby
import json

res_list = []
for injection_id in range(100):
    with open(f'{str(injection_id).zfill(2)}_params.json') as f:
        injection_params = json.load(f)
    res = bilby.result.read_in_result(f'sliding_window_5_64Hz_one_qpo_injections/one_qpo/results/{str(injection_id).zfill(2)}_result.json')
    res.injection_parameters = injection_params
    res_list.append(res)

bilby.result.make_pp_plot(results=res_list, outdir='.')