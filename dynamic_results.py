#!/usr/bin/python
"""
Contains the functions which perform nested sampling given input from settings.
These are all called from within the wrapper function
nested_sampling(settings).
"""

import pandas as pd
import pns_settings
import pns.estimators as e
# import pns.analysis_utils as au
# import pns.parallelised_wrappers as pw
# import pns.maths_functions as mf
import pns.results_generation as rg
import pns.likelihoods as likelihoods
import pns.priors as priors
settings = pns_settings.PerfectNestedSamplingSettings()
pd.set_option('display.width', 200)


# Settings
# --------
calc_type = 'test'
n_runs = 1000
parallelise = True
load = True
save = True
if calc_type == 'test':
    n_runs = 10
    parallelise = False
    load = False
    save = False
    dynamic_goals = [None, 0, 1]
    tuned_dynamic_ps = [False] * len(dynamic_goals)
    likelihood_list = [likelihoods.gaussian(1)]
    n_dim_list = [10]
    rmax_list = [10]
elif calc_type == 'n_dim' or calc_type == 'prior_scale':
    dynamic_goals = [None, 0, 1]
    tuned_dynamic_ps = [False] * len(dynamic_goals)
    likelihood_list = [likelihoods.gaussian(1),
                       likelihoods.exp_power(1, 0.75),
                       likelihoods.exp_power(1, 2)]
    if calc_type == 'ndim':
        n_dim_list = [10]
        rmax_list = [10]
    elif calc_type == 'prior_scale':
        n_dim_list = [2]
        rmax_list = [0.1, 0.3, 1, 3, 10, 30, 100]
elif calc_type == 'Cauchy':
    n_dim_list = [10]
    rmax_list = [10]
    likelihood_list = [likelihoods.cauchy(1)]
    dynamic_goals = [None, 0, 1, 1]
    tuned_dynamic_ps = [False] * (len(dynamic_goals) - 1) + [True]

estimator_list = [e.logzEstimator(),
                  e.paramMeanEstimator(),
                  e.paramSquaredMeanEstimator(),
                  e.paramCredEstimator(0.5),
                  e.paramCredEstimator(0.84)]
# Run program
# -----------
print("Running dynamic results:")
dr_list = []
for n_dim in n_dim_list:
    settings.n_dim = n_dim
    if n_dim >= 100:
        settings.nbatch = 2
    else:
        settings.nbatch = 1
    for rmax in rmax_list:
        if n_dim >= 100:
            settings.prior = priors.gaussian_cached(rmax, n_dim=n_dim)
        else:
            settings.prior = priors.gaussian(rmax)
        for likelihood in likelihood_list:
            settings.likelihood = likelihood
            dr = rg.get_dynamic_results(n_runs, dynamic_goals,
                                        estimator_list, settings,
                                        tuned_dynamic_ps=tuned_dynamic_ps,
                                        load=load, save=save,
                                        parallelise=parallelise)
            print(dr)
            dr_list.append(dr)
