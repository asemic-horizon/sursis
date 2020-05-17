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
	#metric =np.array([1.0/len(node) for node in  graph.nodes()])#nx.degree_centrality(graph)
	metric = nx.betweenness_centrality(graph)
	metric = np.array(list(dict(metric).values()))
	#metric = metric/np.sum(metric)
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

#@mem.cache
def potential(graph: nx.Graph,
			  mass: np.ndarray, 
			  boundary_value,
			  bracket,
			  fast = True):
	rho = mass.reshape(-1,)
	L = nx.laplacian_matrix(graph)
	bounds = boundary_condition(graph, boundary_value, *bracket)
	logging.info(f"Fast recalc: {fast}")
	sol = scipy.optimize.lsq_linear(
		L,
		-rho,
		bounds=bounds,
		max_iter = 50 if fast else 5000)
	logging.info("Optimality: " + sol.message)
	logging.info("Effective boundary:" +  str(test_boundary(graph, sol.x)))
	return sol.x

def physics(graph : nx.Graph,
			boundary_value = 0.025, 
			bracket=(-np.inf,np.inf),
			fast = True ):
	m = mass(graph)	
	return m, potential(graph,m, boundary_value,bracket, fast)

def autophysics(graph, 
				initial_boundary = 0, 
				bracket=(-np.inf,np.inf),
				shrink = 0.8, n_iters = 2, fast = True):
	iter = 0
	boundary = initial_boundary
	m = mass(graph)
	e = potential(graph = graph, 
				mass = m,
				boundary_value = boundary,
				bracket=bracket,
				fast = fast)
	b0 = np.min(e); b1 = np.max(e)
	while iter <= n_iters:
		e = potential(graph = graph, 
					mass = m,
					boundary_value = boundary,
					bracket=bracket,
					fast = fast)
		gravity = np.sum(m*e)
		if gravity > 0:
			boundary = (b0 + boundary)/2
			b1 = boundary
		else:
			boundary = (boundary + b1)/2
			b0 = boundary
		logging.info(f"Autophysics: on iter {iter}, gravity is {gravity:3.2f}, recommended boundary value {boundary}")
		iter +=1
	return m, e