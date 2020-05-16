import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np
from joblib import Memory
mem = Memory('./cache')
def isolates(graph):
	 return [n for n,f in enumerate(graph.nodes) if graph.degree[f]==0]

def boundary(graph):
	 return [n for n,f in enumerate(graph.nodes) if graph.degree[f]==1]

def weaklink(graph):
	 return [n for n,f in enumerate(graph.nodes) if graph.degree[f]==2]

def test_boundary(graph,vector):
	return np.median(vector[boundary(graph)])

def boundary_condition(graph, value = 0.0, lower = -np.inf, higher = np.inf, eps = 1e-10):
	n = graph.number_of_nodes()
	gb = boundary(graph)
	lb = np.full((n,),lower)
	ub = np.full((n,),higher)
	lb[gb] = value-eps
	ub[gb] = value+eps
	#print(lb)
	return (lb,ub)

def mass(graph):
	metric = nx.betweenness_centrality(graph)
	metric = np.array(list(dict(metric).values()))
	return metric

def penrose_potential(graph : nx.Graph,mass : np.ndarray):
	rho = mass.reshape(1,-1)
	L = nx.laplacian_matrix(graph)
	L_inv = scipy.linalg.pinv(L.todense())
	return L_inv.dot(mass)

def least_squares_potential(graph: nx.Graph, mass : np.ndarray):
	rho = mass.reshape(-1,1)
	L = nx.la.placian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(L, -rho,damp=1e-3)
	return sol[0]

@mem.cache
def potential(graph: nx.Graph, mass: np.ndarray, boundary_value = 0.0, bracket=(-np.inf,np.inf)):
	rho = mass.reshape(-1,)
	L = nx.laplacian_matrix(graph)
	bounds = boundary_condition(graph, boundary_value, *bracket)
	sol = scipy.optimize.lsq_linear(
		L,
		-rho,
		bounds=bounds,
		max_iter = len(rho)*len(rho))
	logging.info("Optimality " + str(sol.status))
	logging.info(str(test_boundary(graph, sol.x)))
	return sol.x

def energy(graph : nx.Graph):
	return potential(graph,mass(graph))

def gravity(graph : nx.Graph):
	return mass(graph) * energy(graph)

def net_gravity(graph : nx.Graph):
	return np.sum(gravity(graph))

def rescale(y : np.ndarray):
	return y
