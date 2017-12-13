Perfect Nested Sampling
=======================

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ejhigson/PerfectNestedSampling/LICENSE)


Performs dynamic nested sampling and standard nested sampling for spherically symmetric likelihoods and priors, and analyses the samples produced.
In these cases the algorithms can be followed "perfectly" (without implementation-specific errors from correlated sampling), making them ideal for studying nested sampling.
This package contains the code used to generate results in the [dynamic nested sampling paper (Higson, 2017a)](https://arxiv.org/abs/1704.03459) and provides an example implementation of the algorithm to accompany the paper.

### Background

Nested sampling is a method for Bayesian computation which given some likelihood L(theta) and prior P(theta) will generate posterior samples and an estimate of the Bayesian evidence Z; for more details see [Skilling (2006)](https://projecteuclid.org/euclid.ba/1340370944) and the [dynamic nested sampling paper](https://arxiv.org/abs/1704.03459).
The module also includes an implementation of nested sampling error estimates using resampling (described in [Higson (2017b)](https://arxiv.org/abs/1703.09701)).

Nested sampling works by sampling some number of points randomly from the prior then iteratively replacing the point with the lowest likelihood with another point sampled from the region of the prior with a higher likelihood.
Generating uncorrelated samples within the likelihood constraint is computationally challenging and can only be done approximately by software such as MultiNest and PolyChord.
This module uses special cases where uncorrelated samples can be easily drawn from within some iso-likelihood contour to perform nested sampling perfectly in the manner described by [Keeton (2010)](https://academic.oup.com/mnras/article/414/2/1418/977810).

### Likelihoods and Priors

This module uses only spherical likelihoods and priors L(r) and P(r), where the radial coordinate r = |theta|.
Any perfect nested sampling evidence or parameter estimation calculation is equivalent to some problem with spherically symmetric likelihoods and priors (see [Section 3 of this paper](https://arxiv.org/abs/1703.09701) for more details), so with suitable choices of L(r), P(r) and the parameter estimation quantity a wide variety of tests can be performed with this package.
L(r) must be a monotonically decreasing function of the radius r, so that the likelihood increases as r decreases to a maximum at r=0.

Nested statistically estimating the shrinkage in the fraction of the prior volume remaining X.
This module generates nested sampling runs by sampling from the known distribution of prior volumes X, then using the prior to find the corresponding radial coordinates r(X) and the likelihood to find the likelihood values L(r(X)).
Parameter vectors theta_i for each point i are sampled from the hyper-spherical shell with radius r_i.

##### Implementation

New likelihoods and priors can be added to `likelihoods.py` and `priors.py`, and new parameter estimation quantities can be added to `estimators.py`.
See the documentation in each file for more details.

The package uses log likelihoods and log point weights throughout to prevent overflow errors from extreme numerical values - this is particularly important in high dimensions.
Most of the computation is done within the numpy package for computational efficiency.

### Setup

PerfectNestedSampling works for Python 2 (>= 2.7.10) and Python 3.
To pip install the requirements use
```
pip install -r requirements.txt --user
```

To install PerfectNestedSampling as a pip module for importing in other file locations, use

```
pip install file_location/PerfectNestedSampling --user
```

### Examples and testing

To see a demonstration of how the package works, run

```
python demo.py
```

This covers essentially all the package's functionality and doubles as a test; if it runs ok then everything should be working.

##### Replicating results from the dynamic nested sampling paper

The `demo.py` script illustrates the use of the results table generating functions used for the [dynamic nested sampling paper](https://arxiv.org/abs/1704.03459).
Any of the results can be replicated from these functions by choosing the settings to match those described. Note that the paper uses nbatch=1 and dynamic_fraction=0.9 throughout, and uses the 'cached_gaussian' prior in place of the 'gaussian' prior when the number of dimensions is 100 or more.
