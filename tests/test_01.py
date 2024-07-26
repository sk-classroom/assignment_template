# %% Import
from scipy import sparse
import pandas as pd
import igraph
import numpy as np

# %% Define utility functions

def to_igraph(src, trg):
    g = igraph.Graph.TupleList(list(zip(src, trg)), directed=False)
    return g

# %% Test -----------
