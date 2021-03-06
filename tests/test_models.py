#
# Copyright (C) 2016 Jerome Kelleher <jerome.kelleher@well.ox.ac.uk>
#
# This file is part of msprime.
#
# msprime is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# msprime is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with msprime.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Test cases for simulation models to see if they have the correct
basic properties.
"""
from __future__ import print_function
from __future__ import division

import unittest

import _msprime
import msprime


class TestRejectedCommonAncestorEventCounts(unittest.TestCase):
    """
    Tests to see if we get the correct number of rejected commone ancestor
    events from the various models.
    """
    def test_hudson(self):
        threshold = 20
        sim = msprime.simulator_factory(sample_size=10, recombination_rate=5)
        sim.run()
        self.assertGreater(sim.get_num_common_ancestor_events(), threshold)
        self.assertGreater(sim.get_num_recombination_events(), threshold)
        self.assertEqual(sim.get_num_rejected_common_ancestor_events(), 0)

        sim = msprime.simulator_factory(
            sample_size=10, recombination_rate=5, model="hudson")
        sim.run()
        self.assertGreater(sim.get_num_common_ancestor_events(), threshold)
        self.assertGreater(sim.get_num_recombination_events(), threshold)
        self.assertEqual(sim.get_num_rejected_common_ancestor_events(), 0)

    def test_smc_variants(self):
        for model in ["smc", "smc_prime"]:
            threshold = 20
            sim = msprime.simulator_factory(
                sample_size=10, recombination_rate=5, model=model)
            sim.run()
            self.assertGreater(sim.get_num_common_ancestor_events(), threshold)
            self.assertGreater(sim.get_num_recombination_events(), threshold)
            self.assertGreater(sim.get_num_rejected_common_ancestor_events(), 0)


class TestCoalescenceRecords(unittest.TestCase):
    """
    Tests that the coalescence records have the correct properties.
    """
    def test_gaps(self):
        # SMC simulations should never have adjacent coalescence records with
        # a non-zero distance between them and the same time/node value.
        # First we do a simulation with the standard model to make sure
        # we have plausible parameter values.
        sample_size = 10
        recombination_rate = 20
        random_seed = 1

        ts = msprime.simulate(
            sample_size=sample_size, recombination_rate=recombination_rate,
            random_seed=random_seed)
        records = list(ts.records())
        num_found = 0
        for j in range(1, len(records)):
            r = records[j - 1]
            s = records[j]
            if r.right != s.left and r.node == s.node:
                num_found += 1
        self.assertGreater(num_found, 10)  # Make a reasonable threshold

        # Now do the same for SMC and SMC'.
        for model in ["smc", "smc_prime"]:
            ts = msprime.simulate(
                sample_size=sample_size, recombination_rate=recombination_rate,
                random_seed=random_seed, model=model)
            records = list(ts.records())
            num_found = 0
            for j in range(1, len(records)):
                r = records[j - 1]
                s = records[j]
                if r.right != s.left and r.node == s.node:
                    num_found += 1
            self.assertEqual(num_found, 0)


class TestModelParsing(unittest.TestCase):
    """
    Tests the parsing code for model strings.
    """
    def test_bad_models(self):
        for bad_model in ["NOT", "",  "MODEL"]:
            self.assertRaises(ValueError, msprime.simulate, 10, model=bad_model)

    def test_model_variants(self):
        for model in ["hudson", "smc", "smc_prime"]:
            sim = msprime.simulator_factory(sample_size=10, model=model.upper())
            self.assertEqual(sim.get_model(), model)
            sim = msprime.simulator_factory(sample_size=10, model=model.title())
            self.assertEqual(sim.get_model(), model)


class TestUnsupportedDemographicEvents(unittest.TestCase):
    """
    Some demographic events are not supported until specific models.
    """
    def test_smc_bottlenecks(self):
        # TODO we should have a better exception here.
        for model in ["smc", "smc_prime"]:
            self.assertRaises(
                _msprime.InputError, msprime.simulate, 10, model=model,
                demographic_events=[msprime.SimpleBottleneck(1)])
            self.assertRaises(
                _msprime.InputError, msprime.simulate, 10, model=model,
                demographic_events=[msprime.InstantaneousBottleneck(1)])
