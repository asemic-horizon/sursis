import networkx as nx 
import collections
import numpy as np
import physics as phys
import graph_physics as chem
import scipy

def degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	return deg, cnt 

def spectrum(graph):
	L = nx.laplacian_matrix(graph)
	eigvals = np.linalg.eigbals(L.toarray())
	return eigvals