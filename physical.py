import networkx as nx 
import scipy
import numpy as np

def potential(graph : nx.Graph,density_vector : np.ndarray):
	rho = density_vector.reshape(1,-1)
	L = nx.laplacian_matrix(graph)
	L_inv = scipy.linalg.pinv(L.todense())

	return L_inv.dot(density_vector)

def graph_potential(graph : nx.Graph):
	degrees = np.array(list(dict(graph.degree()).values()))
	density = np.vectorize(lambda x: 0 if x==0 else 1/x)
	return potential(graph, density(degrees))

