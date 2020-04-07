#!/usr/bin/env python
"""Tests for `covid19_outbreak_simulator` package."""

import pytest
import math
from scipy.stats import norm
import numpy as np


def test_params_set_mean(params):
    params.set('prop_asym_carriers', 'loc', 0.3)
    assert params.prop_asym_carriers_loc == 0.3


def test_prop_asym_carriers(params):
    params.set('prop_asym_carriers', prop='loc', value=0.25)
    params.set('prop_asym_carriers', prop='quantile_2.5', value=0.1)

    dist = norm(
        loc=params.prop_asym_carriers_loc,
        scale=params.prop_asym_carriers_scale)

    assert math.fabs(dist.cdf(0.1) - 0.025) < 0.001
    assert math.fabs(dist.cdf(0.4) - 0.975) < 0.001


def test_symptomatic_r0(params):
    params.set('symptomatic_r0', prop='low', value=1.4)
    params.set('symptomatic_r0', prop='high', value=2.8)

    assert params.symptomatic_r0_low == 1.4
    assert params.symptomatic_r0_high == 2.8


def test_asymptomatic_r0(params):
    params.set('asymptomatic_r0', prop='low', value=0.14)
    params.set('asymptomatic_r0', prop='high', value=0.28)

    assert params.asymptomatic_r0_low == 0.14
    assert params.asymptomatic_r0_high == 0.28


def test_draw_prop_asym_carriers(default_model):
    props = []
    for i in range(1000):
        props.append(default_model.draw_prop_asym_carriers())

    assert math.fabs(
        sum(props) / 1000 - default_model.params.prop_asym_carriers_loc) < 0.05


def test_drawn_is_asymptomatic(default_model):
    prop = default_model.draw_prop_asym_carriers()
    is_asymp = []
    for i in range(1000):
        is_asymp.append(default_model.draw_is_asymptomatic())

    assert math.fabs(sum(is_asymp) / 1000) - prop < 0.05


def test_drawn_random_r0(default_model):
    symp_r0 = []
    N = 10000
    for i in range(N):
        symp_r0.append(default_model.draw_random_r0(symptomatic=True))
    #
    assert math.fabs(sum(symp_r0) /
                     N) - (default_model.params.symptomatic_r0_low +
                           default_model.params.symptomatic_r0_high) / 2 < 0.001

    asymp_r0 = []
    for i in range(N):
        asymp_r0.append(default_model.draw_random_r0(symptomatic=False))
    #
    assert math.fabs(sum(asymp_r0) / N) - (
        default_model.params.asymptomatic_r0_low +
        default_model.params.asymptomatic_r0_high) / 2 < 0.001


def draw_random_incubation_period(default_model):
    symp_r0 = []
    N = 10000
    for i in range(N):
        symp_r0.append(default_model.draw_random_incubation_period())
    #
    assert math.fabs(sum(symp_r0) / N) - scipy.stats.lognorm.mean(
        s=1,
        loc=self.params.incubation_period_mean,
        scale=self.params.incubation_period_sigma) < 0.001


def test_get_symptomatic_transmission_probability(default_model):

    incu = default_model.draw_random_incubation_period()
    R0 = default_model.draw_random_r0(symptomatic=True)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_symptomatic_transmission_probability(
            incu, R0)
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.01


def test_get_asymptomatic_transmission_probability(default_model):

    R0 = default_model.draw_random_r0(symptomatic=False)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_asymptomatic_transmission_probability(
            R0)
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.05
