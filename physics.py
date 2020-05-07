import networkx as nx 
import scipy
import numpy as np
from joblib import Memory

memory = Memory("./cache")

@memory.cache
def mass(graph):
	metric = nx.betweenness_centrality(graph)
	metric = np.array(list(dict(metric).values()))
	return metric


#@memory.cache
def penrose_potential(graph : nx.Graph,mass : np.ndarray):
	rho = mass.reshape(1,-1)
	L = nx.laplacian_matrix(graph)
	L_inv = scipy.linalg.pinv(L.todense())
	return L_inv.dot(mass)

#@memory.cache
def potential(graph: nx.Graph, mass : np.ndarray):
	rho = mass.reshape(-1,1)
	L = nx.laplacian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(L, rho)
	return sol[0]

def energy(graph : nx.Graph):
	return rescale(potential(graph,mass(graph)))

def rescale(y : np.ndarray):
	t = (y - y.mean())/y.std()
	return t/4
