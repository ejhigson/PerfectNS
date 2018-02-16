#!/usr/bin/env python
"""
Wrapper functions for generating nested sampling runs and performing functions
on them in parallel, using the concurrent.futures module.
"""

import concurrent.futures
import numpy as np
import tqdm
import perfectns.nested_sampling as ns
import nestcheck.io_utils as iou


@iou.timing_decorator
def func_on_runs(single_run_func, run_list, estimator_list, **kwargs):
    """
    Performs input analysis function on a list of nested sampling runs.
    Parallelised by default.

    Parameters
    ----------
    single_run_func: function
        Function acting on a nested sampling run with arguments
            ns_run
            estimator_list
            **kwargs
        Must return a 1-dimensional numpy array of the same length as
        estimator_list
    run_list: list of nested sampling run dictionaries
    estimator_list: list of estimator objects
    parallelise: bool, optional
        To turn off parallelisation if needed.
    max_workers: int or None, optional
        Number of processes.
        If max_workers is None then concurrent.futures.ProcessPoolExecutor
        defaults to using the number of processors of the machine.
        N.B. If max_workers=None and running on supercomputer clusters with
        multiple nodes, this may default to the number of processors on a
        single node and therefore there will be no speedup from multiple
        nodes (must specify manually in this case).
    results_as_list: bool
        Should results for each run be returned as a list (rather than as an
        array with each result as a column). This must be True if the function
        does not return 1d numpy arrays.
    Returns
    -------
    results: numpy array or list
        A list of results or a 2d numpy array where each result is a column
        (behavior determined by results_as_list parameter).
    """
    max_workers = kwargs.pop('max_workers', None)
    parallelise = kwargs.pop('parallelise', True)
    results_as_list = kwargs.pop('results_as_list', False)
    results_list = []
    print('func_on_runs: calculating ' + single_run_func.__name__ + ' for ' +
          str(len(run_list)) + ' runs')
    if parallelise:
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        futures = []
        for run in run_list:
            futures.append(pool.submit(single_run_func, run,
                                       estimator_list, **kwargs))
        for fut in tqdm.tqdm(concurrent.futures.as_completed(futures),
                             leave=False, total=len(futures)):
            results_list.append(fut.result())
        del futures
        del pool
    else:
        print('Warning: func_on_runs not parallelised!')
        for run in tqdm.tqdm(run_list, leave=False):
            results_list.append(single_run_func(run, estimator_list, **kwargs))
    if results_as_list:
        return results_list
    else:
        # Merge results_list (containing 1d arrays) into a 2d array where each
        # element of results list is a column
        return np.stack(results_list, axis=1)


@iou.timing_decorator
def generate_runs(settings, n_repeat, max_workers=None, parallelise=True):
    """
    Generate n_repeat nested sampling runs in parallel.

    Parameters
    ----------
    settings: PerfectNSSettings object
    n_repeat: int
        Number of nested sampling runs to generate.
    parallelise: bool, optional
        Should runs be generated in parallel?
    max_workers: int or None, optional
        Number of processes.
        If max_workers is None then concurrent.futures.ProcessPoolExecutor
        defaults to using the number of processors of the machine.
        N.B. If max_workers=None and running on supercomputer clusters with
        multiple nodes, this may default to the number of processors on a
        single node and therefore there will be no speedup from multiple
        nodes (must specify manually in this case).

    Returns
    -------
    run_list
        list of n_repeat nested sampling runs.
    """
    run_list = []
    if parallelise is False:
        print('Warning: generate_runs not parallelised!')
        for _ in tqdm.tqdm(range(n_repeat), leave=False):
            run_list.append(ns.generate_ns_run(settings))
    else:
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        futures = []
        for _ in range(n_repeat):
            futures.append(pool.submit(ns.generate_ns_run, settings))
        for fut in tqdm.tqdm(concurrent.futures.as_completed(futures),
                             leave=False, total=len(futures)):
            run_list.append(fut.result())
        del futures
        del pool
    return run_list


def get_run_data(settings, n_repeat, **kwargs):
    """
    Tests if runs with the specified settings are already cached. If not
    the runs are generated and saved.

    Parameters
    ----------
    settings: PerfectNSSettings object
    n_repeat: int
        Number of nested sampling runs to generate.
    parallelise: bool, optional
        Should runs be generated in parallel?
    max_workers: int or None, optional
        Number of processes.
        If max_workers is None then concurrent.futures.ProcessPoolExecutor
        defaults to using the number of processors of the machine.
        N.B. If max_workers=None and running on supercomputer clusters with
        multiple nodes, this may default to the number of processors on a
        single node and therefore there will be no speedup from multiple
        nodes (must specify manually in this case).
    load: bool
        Should previously saved runs be loaded? If False, new runs are
        generated.
    save: bool
        Should any new runs generated be saved?
    overwrite_existing: bool, optional
        if a file exists already but we generate new run data, should we
        overwrite the existing file when saved?
    check_loaded_settings: bool, optional
        if we load a cached file, should we check if the loaded file's settings
        match the current settings (and generate fresh runs if they do not)?

    Returns
    -------
    run_list
        list of n_repeat nested sampling runs.
    """
    parallelise = kwargs.pop('parallelise', True)
    max_workers = kwargs.pop('max_workers', None)
    load = kwargs.pop('load', True)
    save = kwargs.pop('save', True)
    overwrite_existing = kwargs.pop('overwrite_existing', False)
    check_loaded_settings = kwargs.pop('check_loaded_settings', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)
    save_name = 'data/' + iou.data_save_name(settings, n_repeat)
    if load:
        print('get_run_data: ' + save_name)
        try:
            data = iou.pickle_load(save_name)
        except OSError:  # FileNotFoundError is a subclass of OSError
            print('File not found - try generating new data')
            load = False
        except EOFError:
            print('EOFError loading file - try generating new data and '
                  'overwriting current file')
            load = False
            overwrite_existing = True
        if check_loaded_settings:
            # Assume all runs in the loaded list have the same settings, in
            # which case we only need check the first one.
            if settings.get_settings_dict() == data[0]['settings']:
                print('Loaded settings = current settings')
            else:
                print('Loaded settings =')
                print(data[0]['settings'])
                print('are not equal to current settings =')
                print(settings.get_settings_dict())
                del data
                load = False
    if not load:
        data = generate_runs(settings, n_repeat, max_workers=max_workers,
                             parallelise=parallelise)
        if save:
            print('Generated new runs: saving to ' + save_name)
            iou.pickle_save(data, save_name,
                            overwrite_existing=overwrite_existing)
    return data