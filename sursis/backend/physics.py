import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np


def physics(graph : nx.Graph,
			boundary_value = 0.025, model = None,\
			bracket=(-np.inf,np.inf), crit_degree=2, fast = True ):
	m = mass(graph)	
	if model == "penrose":
		return m, lsq(graph,m)
	elif model == "dirichlet": 
		return m, forced_boundary(graph,
								  mass = m, 
								  boundary_value = boundary_value,
   								  crit_degree = crit_degree)
	else:
		return m, constrained_lsq(graph,
								  mass = m, 
								  boundary_value = boundary_value,
   								  crit_degree = crit_degree,
   								  fast=fast)

def boundary(graph,crit_degree):
	 return [n for n,f in enumerate(graph.nodes)\
	 	       if graph.degree[f]==crit_degree]

def internal(graph,crit_degree):
	 return [n\
	 			 for n,f in enumerate(graph.nodes)\
	 			 if graph.degree[f]!=crit_degree]

def lsq_boundary(graph, value = 0.0, crit_degree=1,
				 lower = -np.inf, higher = np.inf,\
				 eps = 1e-10):
	n = graph.number_of_nodes()
	lb = np.full((n,),lower); ub = np.full((n,),higher)
	gb = boundary(graph,crit_degree)
	lb[gb] = value-eps
	ub[gb] = value+eps
	return (lb,ub)

def mass(graph):
	m1 = nx.eigenvector_centrality(graph)
	m1 = np.array(list(dict(m1).values()))
	
	return m1/np.sum(m1)

def lsq(graph: nx.Graph, mass : np.ndarray):
	rho = mass.reshape(-1,1)
	L = nx.laplacian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(L, -rho,damp=1e-3)
	return sol[0]

def constrained_lsq(graph: nx.Graph,
			  mass: np.ndarray, 
			  boundary_value,
			  crit_degree,
			  bracket,
			  fast = True):
	rho = mass.reshape(-1,)
	L = nx.laplacian_matrix(graph)
	bounds = lsq_boundary(graph, boundary_value,\
														crit_degree, *bracket)
	logging.info(f"Fast recalc: {fast}")
	sol = scipy.optimize.lsq_linear(
		L,
		-rho,
		bounds=bounds,
		max_iter = 10 if fast else 5000)
	logging.info("Optimality: " + sol.message)
	return sol.x

def forced_boundary(graph: nx.Graph,
			mass: np.ndarray,
			boundary_value,
			crit_degree,
			max_iter = 30,
			tol = 1e-6):
	boundary_nodes = boundary(graph, crit_degree)
	internal_nodes  = internal(graph, crit_degree)
	deg = list(dict(graph.degree()).values())
	
	A = nx.adjacency_matrix(graph)
	phi = -0.1*np.ones((graph.number_of_nodes(),))
	
	phi[boundary_nodes] = boundary_value

	# A fixed point of x[n+1]=C*x[n]+b is such that
	# x = Cx+b => (I-C) x = b =>x = inv(I-C)*b
	# Hence this iteration can be used to invert I-C.
	#
	# Now, Ly = (D-A)y = D(I-inv(D)*A) = mass
	# Hence the iteration x(n+1)=inv(D)*A +mass
	#
	# But only on internal nodes. 

	err = np.inf; iter = 0
	while err>tol and iter < max_iter:
		phi_hat = phi.copy()
		for row in internal_nodes:
			z = np.dot(A[row,:].todense(),phi)
			phi_hat[row] = z.reshape(-1,)[0]/deg[row] - mass[row]
			
		err = scipy.linalg.norm(phi_hat - phi)
		print(iter,err)
		phi = phi_hat.copy()
		iter += 1
	logging.info(f"After {iter} steps, estimate change of {err:.4e}")
	return phi