import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

import networkx as nx 
import scipy
import numpy as np

def mass(graph):
	m1 = nx.closeness_centrality(graph)
	m1 = np.array(list(dict(m1).values()))
	
	return m1/np.sum(m1)

def physics(graph : nx.Graph, model : str, fast: bool = False,  *args, **kwargs):
	m = mass(graph).reshape(-1,1)
	graph.remove_edges_from(nx.selfloop_edges(graph))
	if model == "penrose":
		phi = lsq(graph,m, *args, **kwargs)
	elif model == "dirichlet": 
		phi = forced_boundary(graph,m, *args, **kwargs)
	else:
		phi = constrained_lsq(graph,m, *args, **kwargs)
	return m, phi

## SOLVERS

def lsq(graph: nx.Graph, mass : np.ndarray,*args, **kwargs):
	laplacian = nx.laplacian_matrix(graph)
	sol = scipy.sparse.linalg.lsmr(laplacian, -mass,damp=1e-3)
	return sol[0]

def constrained_lsq(graph: nx.Graph, mass: np.ndarray, 
		 		    outer_boundary_value: float,
		 		    core_boundary_value: float,
				    crit_degree: int,
				    crit_core_number: int,
				    max_iter: int = 50,
				    tol : float = 1e-6):

	n = graph.number_of_nodes()
	outer_boundary_nodes = outer_boundary(graph,crit_degree)
	core_boundary_nodes = core_boundary(graph,crit_core_number)
	lb = np.full((n,),lower); ub = np.full((n,),higher)
	lb[outer_boundary_nodes] = outer_boundary_value-eps
	ub[outer_boundary_nodes] = outer_boundary_value+eps
	lb[core_boundary_nodes] = core_boundary_value-eps
	ub[core_boundary_nodes] = outer_boundary_value+eps
	
	sol = scipy.optimize.lsq_linear(laplacian,-mass,bounds = (lb,ub), max_iter = max_iter )
	logging.info("Optimality: " + sol.message)
	return sol.x

def forced_boundary(graph: nx.Graph,
			mass: np.ndarray,
			outer_boundary_value: float,
			core_boundary_value: float,
			crit_degree: int,
			crit_core_number: int,
			max_iter = 330,
			tol = 1e-3):

	A = nx.adjacency_matrix(graph)
	deg = np.array(list(dict(graph.degree()).values()))
	deg = deg.reshape(-1,1)
	core_boundary_nodes = core_boundary(graph,crit_core_number)
	outer_boundary_nodes = outer_boundary(graph,crit_degree)

	interior_nodes = outer_interior(graph, crit_degree) \
					+ core_interior(graph,crit_core_number)

	# for error calculation

	L = nx.laplacian_matrix(graph)
	n = len(mass)
	# initial guess
	phi = lsq(graph,mass)
	#phi = np.random.uniform(low=-0.001, high=0.001, size=(graph.number_of_nodes(),))
	# fix boundary nodes
	phi[core_boundary_nodes] = core_boundary_value
	phi[outer_boundary_nodes] = outer_boundary_value

	# solve for interior nodes
	#
	# A fixed point of x[n+1]=C*x[n]+b is such that
	# x = Cx+b => (I-C) x = b =>x = inv(I-C)*b
	#
	# Apply this idea for L = (D-A) = D(I-inv(D)*A)
	# iteration is phi' = inv(D)*(A*phi) + (-mass)


	err = np.inf; iter = 0; eps = 0
	error_history = np.empty((max_iter,))
	while err>tol and iter < max_iter:
		err_ = err;
		phi_update = phi.copy()
		sweep = interior_nodes.copy(); np.random.shuffle(sweep)
		for row in sweep:
			forward = np.dot(A[row,:].todense(),phi).reshape(-1,1)[0]
			phi_update[row] = forward/deg[row] - mass[row]
			
		err = scipy.linalg.norm(L.multiply(phi_update) - mass)/n
		error_history[iter] = err
		if iter>10 and err>np.mean(error_history[iter-10:iter]):
			print(f"Difvergibg at iter {iter}, err={err}")
			break
		else:
			phi = phi_update.copy()
			print(iter,err)	
			iter += 1
	logging.info(f"After {iter} steps, estimate error of {err:.4e}")
	return phi

## TOPOLOGY UTILS

def outer_boundary(graph,crit_degree):
	return [n for n,f in enumerate(graph.nodes)\
	 	       if graph.degree[f]==crit_degree]

def outer_interior(graph,crit_degree):
	return [n for n,f in enumerate(graph.nodes)\
	 	       if graph.degree[f]!=crit_degree]


def core_boundary(graph,crit_core_number):
	cores = nx.algorithms.core.core_number(graph)
	return [n for n,f in enumerate(graph.nodes)\
				if cores[f]==crit_core_number]

def core_interior(graph,crit_core_number):
	cores = nx.algorithms.core.core_number(graph)
	return [n for n,f in enumerate(graph.nodes)\
				if cores[f]!=crit_core_number]

