import networkx as nx 
import collections
import numpy as np
import scipy
#
from backend import physics as phys
from backend import graph_physics as chem
from scipy.optimize import curve_fit

def degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	return deg, cnt 

def spectrum(graph):
	L = nx.laplacian_matrix(graph)
	eigvals = np.linalg.eigvals(L.toarray())
	return eigvals

def power_law(x,k,slope):
	x = np.array(x)
	return k*(x**slope)

def fit_power_distribution(deg,cnt):
	popt, _ = curve_fit(f=power_law,xdata=deg[:-1],ydata=cnt[:-1])
	k, slope = tuple(popt)
	return k, slope

def leaf_analysis(graph):
	deg, cnt = degree_distribution(graph)
	k, slope = fit_power_distribution(deg,cnt)
	return cnt[0],k,slope

