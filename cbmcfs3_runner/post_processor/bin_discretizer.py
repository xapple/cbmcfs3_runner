#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

When grouping rows from the simulated inventory we have to sum data
this is categorical (AveAge along with Area). To do this we need to
convert the data into discrete form for the addition then back to categorical.

To test this file you can proceed like this for instance:

    In [1]: from cbmcfs3_runner.core.continent import continent
    In [2]: inv = continent[('static_demand', 'LU', 0)].post_processor.inventory
    In [3]: inv.check_conservation()

If you just want to test one function:

    In [1]: from cbmcfs3_runner.post_processor.bin_discretizer import generate_bins
    In [1]: from cbmcfs3_runner.post_processor.bin_discretizer import bin_to_discrete
    In [2]: generate_bins()
"""

# Built-in modules #

# Third party modules #
import pandas, numpy

# First party modules #
from plumbing.common import sum_vectors_with_padding

# This value is in years and needs to be confirmed with Scott #
CBM_BIN_WIDTH = 20.0

# This value is in years and can be changed to adjust the granularity of the process #
CBM_PRECISION = 0.1

###############################################################################
def bin_to_discrete(bin_height, bin_center,
                    bin_width = CBM_BIN_WIDTH,
                    precision = CBM_PRECISION,
                    testing   = False):
    """
    This function is more or less the inverse of the pandas.cut method.
    Starting with binned data, we will assume a uniform distribution and
    transform it back to discrete data with a given precision.

    Given the center and width of a bin we will create a numpy vector
    with conservation of total mass (i.e. bin_height).

    We will check that we left bound cannot exceed zero.

    >>> bin_to_discrete(1, 6, 10, 1)
    array([0. , 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    """
    # Round to precision #
    bin_radius = bin_width / 2
    bin_radius = int(numpy.round(bin_radius / precision))
    bin_center = int(numpy.round(bin_center / precision))
    # Edges #
    bin_left   = bin_center - bin_radius
    bin_right  = bin_center + bin_radius
    # Check that the left edge is never negative #
    bin_left = max(bin_left, 0)
    # Build vector like this: 0,0,0,0,1,1,1,1,1,1,1,1 #
    vector = numpy.append(numpy.zeros(bin_left), numpy.ones(bin_right - bin_left))
    # Multiply by the matching height #
    vector *= bin_height / (bin_right - bin_left)
    # Check mass is conserved #
    if testing: numpy.testing.assert_allclose(vector.sum(), bin_height)
    # Return #
    return vector

###############################################################################
def aggregator(df, sum_col, bin_col):
    """
    The input df is a data frame with multiple rows and
    the grouping columns still present. One must return a numpy
    vector representing the Area per Age. (i.e. the sum_col per bin_col)
    """
    # Helper function #
    discretizer = lambda row: bin_to_discrete(row[sum_col], row[bin_col])
    # Get the discretized version of all rows as vectors #
    all_vectors = [discretizer(row) for i, row in df.iterrows()]
    # Sum them up vertically to get a single numpy vector #
    return sum_vectors_with_padding(all_vectors)

###############################################################################
###############################################################################
###############################################################################
def generate_bins(vector, bin_width, precision = CBM_PRECISION):
    """Starting from a discretized vector, yield bins.

    >>> list(generate_bins(numpy.array([1,1,2,2,3,4,4,1,1,1,5,6,9]), 0.4, 0.1))
    [(0.0, 0.4, 6 ),
     (0.4, 0.8, 12),
     (0.8, 1.2, 13),
     (1.2, 1.6, 9 )]
     """
    # Round to precision #
    bin_width = int(numpy.round(bin_width / precision))
    # Initialize #
    bin_left = 0
    # Iterate #
    while True:
        # Compute current bin end #
        bin_right = bin_left + bin_width
        # The bin total sum #
        bin = vector[bin_left:bin_right]
        val = bin.sum()
        # Return one bin #
        yield bin_left*precision, (bin_right)*precision, val
        # Next bin's start #
        bin_left = bin_right
        # End condition #
        if bin_left >= len(vector): break

###############################################################################
def binner(vector, sum_col, bin_width):
    """
    Starting from a discretized vector, create a data frame
    with each row describing a bin.
    """
    # Make bins #
    all_bins = generate_bins(vector, bin_width)
    # Make data frame #
    return pandas.DataFrame(all_bins, columns=['age_start', 'age_end', sum_col])
