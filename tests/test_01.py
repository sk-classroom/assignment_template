# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy==2.2.6",
#     "python-igraph==0.11.9",
# ]
# ///

# %% Import
import numpy as np
import sys
import os
import igraph
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from assignment.assignment import compute_global_clustering

# %% Test ------------
# Create initial ring lattice (p=0)
n = 300
k = 4
g = igraph.Graph.Ring(n, directed=False, mutual=False, circular=True)

# Add additional edges to make each node have degree k
for i in range(n):
    for j in range(2, k // 2 + 1):
        neighbor = (i + j) % n
        if not g.are_adjacent(i, neighbor):
            g.add_edge(i, neighbor)

p = g.density()
random.seed(42)
g_er = igraph.Graph.Erdos_Renyi(n=n, p=p)

C = compute_global_clustering(g)
C_er = compute_global_clustering(g_er)

print(f"[Setup] Clustering — Ring: {C:.3f}, ER: {C_er:.3f} (n={n}, k={k}, p={p:.5f})")

# ------------------------------------------------------------
# Test 1 : Ring vs ER — Ring clustering should be higher
# ------------------------------------------------------------
print(f"[Test 1] Ring vs ER clustering: Ring {C:.3f} > ER {C_er:.3f}")
assert C > C_er, f"Clustering coefficient of the ring lattice should be greater than the clustering coefficient of the Erdős–Rényi random graph: {C} > {C_er}"

# ------------------------------------------------------------
# Test 2 : Ring clustering in expected range
# ------------------------------------------------------------
print(f"[Test 2] Ring clustering check: C={C:.3f}. Expected 0.5.")
assert np.isclose(C, 0.5), f"Clustering coefficient of the ring lattice should be 0.5: {C}"

# ------------------------------------------------------------
# Test 3 : ER clustering in expected range
# ------------------------------------------------------------
er_expected_high = 0.05
print(f"[Test 3] ER clustering upper bound: expected < {er_expected_high}, got {C_er:.3f}")
assert C_er < er_expected_high, f"Clustering coefficient of the Erdős–Rényi random graph should be less than 0.05: {C_er}"
