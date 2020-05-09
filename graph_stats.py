import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx 
import collections
import numpy as np
from scipy.optimize import curve_fit

def power_law(x,k,slope):
	return np.exp(k + slope*np.log(x))

def plot_degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	popt, _ = curve_fit(f=power_law,xdata=deg,ydata=cnt)
	k, slope = tuple(popt)
	plt.scatter(deg,cnt)
	plt.plot(deg,np.log(power_law(deg,k,slope)))
	plt.yscale('log')
	plt.grid(True)
	plt.title("Degree distribution")
	st.pyplot()
	st.write(\
f"Approximation: counts=${k:2.1f}\\times$ degree$\^{slope:2.1f}$")
def stats_view(graph):

	plot_degree_distribution(graph)