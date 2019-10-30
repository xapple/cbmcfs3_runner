#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

###############################################################################
class Graphs(object):
    def __getitem__(self, key):
        return [i for i in self.instances if i.short_name == key][0]

    def __iter__(self): return iter(self.instances)
    def __len__(self):  return len(self.instances)

    def __init__(self):
        self.instances = []

    def __call__(self, *args, **kwargs):
        return [i(*args, **kwargs) for i in self.instances]

###############################################################################
def load_graphs_from_module(parent, submodule):
    """
    Sorry for the black magic. The result is an object whose attributes
    are all the graphs found in submodule.py initialized with the
    proper instance as only argument.
    """
    # Get all graphs of a submodule #
    graph_classes   = [getattr(submodule, g) for g in submodule.__all__]
    graph_instances = [g(parent)    for g in graph_classes]
    graph_names     = [g.short_name for g in graph_instances]
    # Create a container object #
    graphs = Graphs()
    # Set its attributes #
    for name, instance in zip(graph_names, graph_instances):
        setattr(graphs, name, instance)
        graphs.instances.append(instance)
    # Return result #
    return graphs