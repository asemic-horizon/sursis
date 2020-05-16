import networkx as nx 
import collections
import numpy as np
import scipy
#
from backend import physics as phys
from backend import graph_physics as chem

def degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	return deg, cnt 

def spectrum(graph):
	L = nx.laplacian_matrix(graph)
	eigvals = np.linalg.eigvals(L.toarray())
	return eigvals