import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np

def boundary(graph,crit_degree):
	 return [n\
	 			 for n,f in enumerate(graph.nodes)\
	 			 if graph.degree[f]==crit_degree]

def least_squares_boundary(graph, value = 0.0, crit_degree=1,\
										 lower = -np.inf, higher = np.inf,\
										 eps = 1e-10):
	n = graph.number_of_nodes()
	lb = np.full((n,),lower); ub = np.full((n,),higher)
	gb = boundary(graph,crit_degree)
	lb[gb] = value-eps
	ub[gb] = value+eps
	return (lb,ub)

def mass(graph):
	m1 = nx.betweenness_centrality(graph)
	m1 = np.array(list(dict(m1).values()))
	return m1/np.sum(m1)

def penrose_potential(graph : nx.Graph,mass : np.ndarray):
	rho = mass.reshape(1,-1)
	L = nx.laplacian_matrix(graph)
	L_inv = scipy.linalg.pinv(L.todense())
	return L_inv.dot(mass)

def least_squares_potential(graph: nx.Graph, mass : np.ndarray):
	rho = mass.reshape(-1,1)
	L = nx.laplacian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(L, -rho,damp=1e-3)
	return sol[0]

def constrained_potential(graph: nx.Graph,
			  mass: np.ndarray, 
			  boundary_value,
			  crit_degree,
			  bracket,
			  fast = True):
	rho = mass.reshape(-1,)
	L = nx.laplacian_matrix(graph)
	bounds = least_squares_boundary(graph, boundary_value,\
														crit_degree, *bracket)
	logging.info(f"Fast recalc: {fast}")
	sol = scipy.optimize.lsq_linear(
		L,
		-rho,
		bounds=bounds,
		max_iter = 10 if fast else 5000)
	logging.info("Optimality: " + sol.message)
	return sol.x

def physics(graph : nx.Graph,
			boundary_value = 0.025, model = None, bracket=(-np.inf,np.inf), crit_degree=2, fast = True ):
	m = mass(graph)	
	if model == "penrose":
		return m, least_squares_potential(graph,m)
	else: return m, constrained_potential(graph,m, boundary_value,crit_degree,bracket, fast)
