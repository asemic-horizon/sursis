import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np
from joblib import Memory
mem = Memory('./cache')

def boundary(graph,crit_degree):
	 return [n for n,f in enumerate(graph.nodes) if graph.degree[f]==crit_degree]

def test_boundary(graph,vector,crit_degree):
	return np.median(vector[boundary(graph,crit_degree)])

def boundary_condition(graph, value = 0.0, crit_degree=1, lower = -np.inf, higher = np.inf, eps = 1e-10):
	n = graph.number_of_nodes()
	lb = np.full((n,),lower)
	ub = np.full((n,),higher)
	gb = boundary(graph,crit_degree)
	lb[gb] = value-eps
	ub[gb] = value+eps
	#print(lb)
	return (lb,ub)

def mass(graph):
	#metric =np.array([1.0/len(node) for node in  graph.nodes()])#nx.degree_centrality(graph)
	#m0 = nx.algorithms.link_analysis.pagerank(graph)
	#m0 = np.array(list(dict(m0).values()))
	m1 = nx.betweenness_centrality(graph)
	m1 = np.array(list(dict(m1).values()))
	metric = m1#0.95*m1/np.sum(m1) + 0.05*m0/np.sum(m0)
	#metric = np.log(1+metric)
	metric = metric/np.sum(metric)
	return metric

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

#@mem.cache
def potential(graph: nx.Graph,
			  mass: np.ndarray, 
			  boundary_value,
			  crit_degree,
			  bracket,
			  fast = True):
	rho = mass.reshape(-1,)
	L = nx.laplacian_matrix(graph)
	bounds = boundary_condition(graph, boundary_value,crit_degree, *bracket)
	logging.info(f"Fast recalc: {fast}")
	sol = scipy.optimize.lsq_linear(
		L,
		-rho,
		bounds=bounds,
		max_iter = 10 if fast else 5000)
	logging.info("Optimality: " + sol.message)
	btest = '\n'.join([f"Effective {t}-nodes: {test_boundary(graph,sol.x,t)}" for t in range(1,1+crit_degree)])
	logging.info(btest)
	return sol.x

def physics(graph : nx.Graph,
			boundary_value = 0.025, model = None, bracket=(-np.inf,np.inf), crit_degree=2, fast = True ):
	m = mass(graph)	
	if model == "penrose":
		return m, least_squares_potential(graph,m)
	else: return m, potential(graph,m, boundary_value,crit_degree,bracket, fast)

def autophysics(graph, 
				initial_boundary = 0, 
				bracket=(-np.inf,np.inf),
				shrink = 0.8, n_iters = 2, fast = True):
	m = mass(graph); 
	grav = lambda b: m*(potential(graph,m,b,bracket,fast))
	sol = scipy.optimize.fsolve(func = grav, x0 = initial_boundary)
	e = potential(graph,m,sol.x[0],bracket,fast)
	logging.info(f"Fsolve: {sol.x}, {sol.ler}, {sol.mesg}")
	return m, e
