import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np

def mass(graph):
	m1 = nx.eigenvector_centrality(graph)
	m1 = np.array(list(dict(m1).values()))
	
	return m1/np.sum(m1)

def physics(graph : nx.Graph, model : str, *args, **kwargs):
	m = mass(graph).reshape(-1,1)

	if model == "penrose":
		phi = lsq(graph,m, *args, **kwargs)
	elif model == "dirichlet": 
		phi = forced_boundary(graph,m, *args, **kwargs)
	else:
		phi = constrained_lsq(graph,m, *args, **kwargs)
	return m, phi

## SOLVERS

def lsq(graph: nx.Graph, mass : np.ndarray):
	laplacian = nx.laplacian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(laplacian, -mass,damp=1e-3)
	return sol[0]

def constrained_lsq(graph: nx.Graph, mass: np.ndarray, 
		 		    boundary_value: float,
				    crit_degree: int,
				    bracket,
				    fast = True):
	sol = scipy.optimize.lsq_linear(
		laplacian,
		-mas,
		bounds = boundary_bounds(graph, boundary_value, crit_degree, *bracket),
		max_iter = 10 if fast else 5000)
	logging.info("Optimality: " + sol.message)
	return sol.x

def forced_boundary(graph: nx.Graph,
			mass: np.ndarray,
			boundary_value: float,
			crit_degree: int,
			max_iter = 30,
			tol = 1e-6):

	A = nx.adjacency_matrix(graph)
	deg = list(dict(graph.degree()).values())

	boundary_nodes = boundary(graph, crit_degree)
	interior_nodes  = interior(graph, crit_degree)

	# initial guess
	phi = -0.1*np.ones((graph.number_of_nodes(),))

	# fix boundary nodes
	phi[boundary_nodes] = boundary_value

	# solve for interior nodes
	#
	# A fixed point of x[n+1]=C*x[n]+b is such that
	# x = Cx+b => (I-C) x = b =>x = inv(I-C)*b
	#
	# Apply this idea for L = (D-A) = D(I-inv(D)*A)
	# iteration is phi' = inv(D)*(A*phi) + (-mass)

	err = np.inf; iter = 0
	while err>tol and iter < max_iter:
		phi_update = phi.copy()
		for row in interior_nodes:
			forward = np.dot(A[row,:].todense(),phi).reshape(-1,1)[0]
			phi_update[row] = forward/deg[row] - mass[row]
			
		err = scipy.linalg.norm(phi_update - phi)
		phi = phi_update.copy()
		iter += 1
	logging.info(f"After {iter} steps, estimate change of {err:.4e}")
	return phi

## TOPOLOGY UTILS

def boundary(graph,crit_degree):
	return [n for n,f in enumerate(graph.nodes)\
	 	       if graph.degree[f]==crit_degree]

def interior(graph,crit_degree):
	return [n for n,f in enumerate(graph.nodes)\
	 	       if graph.degree[f]!=crit_degree]

def boundary_bounds(graph, value = 0.0, crit_degree=1,
				 lower = -np.inf, higher = np.inf,\
				 eps = 1e-10):
	n = graph.number_of_nodes()
	lb = np.full((n,),lower); ub = np.full((n,),higher)
	gb = boundary(graph,crit_degree)
	lb[gb] = value-eps
	ub[gb] = value+eps
	return (lb,ub)


