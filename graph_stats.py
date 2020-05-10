import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx 
import collections
import numpy as np
import physics as phys
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde,mode
import ui_elems as ui
import viz

cmap = "terrain_r"

def power_law(x,k,slope):
	return np.exp(np.log(k) + slope*np.log(x))

def plot_degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	popt, _ = curve_fit(f=power_law,xdata=deg,ydata=cnt)
	k, slope = tuple(popt)
	plt.scatter(deg,cnt)
	plt.plot(deg,power_law(deg,k,slope),\
		linewidth=1,c='k',linestyle='dotted')
		#plt.yscale('log')
	plt.grid(True)
	plt.title("Degree distribution")
	st.pyplot()
	st.write(\
		f"* Approximation: k={k:2.1f}, slope={slope:2.1f}")

def eigenvalues(graph):
	L = nx.laplacian_matrix(graph).todense()
	eigvals = np.linalg.eigvals(L)
	plt.scatter(np.arange(len(eigvals)),eigvals, alpha = 0.5)
	plt.grid(True)
	plt.title("Laplacian eigenvalues")
	st.pyplot()
	st.write(f"* Spectral gap: {eigvals[0]-eigvals[1]:2.1f}")
	st.write(f"* Smallest nonzero eigenvalue: {np.min(eigvals[eigvals>0]):e}")

def mass(graph):
	m = sorted(phys.mass(graph))
	density = gaussian_kde(m)
	plt.plot(m,density(m))
	plt.grid(True)
	plt.title("Mass")
	plt.xscale("log")
	st.pyplot()
	st.write(f"* Mean mass {np.mean(m):e}")

def energy(graph):
	m = sorted(phys.energy(graph))
	m = np.array(m)
	density = gaussian_kde(m)
	plt.plot(m,density(m))
	plt.title("Energy")
	plt.grid(True);
	st.pyplot()
	st.write(f"* Mean energy {np.mean(m):e}")
	st.write(f"* % attractive {100*len(m[m>0])/len(m):2.1f}%")

def phase(graph):
	plt.scatter(phys.mass(graph),phys.energy(graph))
	plt.xscale("log")
	plt.xlabel("Mass");plt.ylabel("Energy")
	st.pyplot()


def stats_view(graph):

	plot_degree_distribution(graph)
	eigenvalues(graph)
	mass(graph)
	energy(graph)
	phase(graph)

def graph_plot(G, conn, center, radius):
	full_graph = center is None

	viz.draw(G,conn,labels = not full_graph, cmap=cmap)
	if full_graph:
		ui.separator()
		st.write("### Components")
		S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap)
			ui.separator()

def mintree(G,conn):
		H = nx.minimum_spanning_tree(G)
		ui.separator()
		st.write("#### Minimum tree")
		viz.draw(H, conn, cmap = cmap)
		st.pyplot()

def maxtree(G,conn):
		J = nx.maximum_spanning_tree(G)
		st.write("#### Maximum tree")
		viz.draw(J, conn, cmap = cmap)
		st.pyplot

def view_energy(G,conn):
	ui.separator()
	st.write("### Energy density")
	energy(G)

def view_spectrum(G,conn):
	ui.separator()
	st.write("### Laplacian spectrum")
	eigenvalues(G)