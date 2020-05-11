import networkx as nx 
import scipy
import numpy as np
from joblib import Memory

memory = Memory("./cache")

#@memory.cache
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
	sol = scipy.sparse.linalg.lsmr(L, -rho,damp=1e-3)
	return sol[0]

def energy(graph : nx.Graph):
	return potential(graph,mass(graph))

def gravity(graph : nx.Graph):
	return mass(graph) * energy(graph)

def net_gravity(graph : nx.Graph):
	return np.sum(gravity(graph))

def rescale(y : np.ndarray):
	return y
