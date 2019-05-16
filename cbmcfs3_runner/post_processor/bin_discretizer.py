#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

When grouping rows from the simulated inventory we have to sum data
this is categorical (AveAge along with Area). To do this we need to
pass the data into discrete form for the addition then back to categorical.

To test this file you can proceed like this for instance:

    In [1]: from cbmcfs3_runner.core.continent import continent
    In [2]: inv = continent[('static_demand', 'LU', 0)].post_processor.inventory
    In [3]: inv.check_conservation(tolerance=1e-7)

Typically a CBM_PRECISION of 0.1 will lead to a discrepancy of 0.5% in area
      and a CBM_PRECISION of 0.01 will lead to a discrepancy of 0.05% in area
      but will be slower to compute.
"""

# Built-in modules #

# Third party modules #
import pandas, numpy

# First party modules #

# This value is in years and needs to be confirmed with Scott #
CBM_BIN_WIDTH = 20.0

# This value is in years and can be changed to adjust the granularity of the process #
CBM_PRECISION = 0.1

###############################################################################
def bin_to_discrete(bin_height, bin_center, bin_width):
    """This function is more or less the inverse of the pandas.cut method.
    Starting with binned data, we will assume a uniform distribution and
    transform it back to discrete data with a given precision.

    Given the center and width of a bin we will create a numpy vector
    with conservation of total mass (i.e. bin_height).

    We will check that we left bound cannot exceed zero.

    >>> categorical_to_discrete(4, 5, 6, 1)
    array([0., 0., 0., 5., 5.])
    >>> categorical_to_discrete(1, 6, 10, 1)
    array([1., 1., 1., 1., 1., 1.])
    """
    # Round to precision #
    bin_radius = bin_width / 2
    bin_radius = int(numpy.round(bin_radius / CBM_PRECISION))
    bin_center = int(numpy.round(bin_center / CBM_PRECISION))
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
    numpy.testing.assert_allclose(vector.sum(),  bin_height)
    # Return #
    return vector

###############################################################################
def apply_discretizer(row, height_key, center_key):
    """Given a row from our dataframe, return the discretized vector."""
    return bin_to_discrete(row[height_key], row[center_key], CBM_BIN_WIDTH)

###############################################################################
def aggregator(df, sum_col, bin_col):
    """The input df is a data frame with multiple rows and
    the grouping columns still present. One must return a
    vector representing the Area per Age. (i.e. the sum_col per bin_col)"""
    # Get the discretized version of all rows #
    all_vectors = df.apply(apply_discretizer, axis=1, height_key=sum_col, center_key=bin_col)
    # Instead of a Series of lists, make a DataFrame #
    # and then sum them up vertically to get a single numpy vector #
    return pandas.DataFrame(v for v in all_vectors).fillna(0.0).sum().values

###############################################################################
###############################################################################
###############################################################################
def generate_bins(vector, bin_width):
    """Starting from a discretized vector, yield bins."""
    # Round to precision #
    bin_width = int(numpy.round(bin_width / CBM_PRECISION))
    # Initialize #
    bin_left = 0
    # Iterate #
    while True:
        # Compute current bin end #
        bin_right = bin_left + bin_width - 1
        # The bin total sum #
        bin = vector[bin_left:bin_right]
        val = bin.sum()
        # Return one bin #
        yield bin_left*CBM_PRECISION, (bin_right+1)*CBM_PRECISION, val
        # Next bin's start #
        bin_left = bin_right + 1
        # End condition #
        if bin_left >= len(vector): break

###############################################################################
def binner(vector, sum_col, bin_width):
    """Starting from a discretized vector, create a dataframe
    with each row describing a bin."""
    # Make bins #
    all_bins = generate_bins(vector, bin_width)
    # Make data frame #
    return pandas.DataFrame(all_bins, columns=['age_start', 'age_end', sum_col])
