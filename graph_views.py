import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx 
import collections
import numpy as np
import physics as phys
import graph_physics as chem
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde
import ui_elems as ui
import viz, stats

cmap = "RdYlBu_r"

def power_law(x,k,slope):
	return np.exp(np.log(k) + slope*np.log(x))

def fit_power_distribution(deg,cnt):
	popt, _ = curve_fit(f=power_law,xdata=deg,ydata=cnt)
	k, slope = tuple(popt)
	return k, slope

def plot_degree_distribution(graph):
	deg, cnt = stats.degree_distribution(graph)
	k, slope = fit_power_distribution(graph)

	plt.scatter(deg,cnt)
	plt.plot(deg,power_law(deg,k,slope), linewidth=1,c='k',linestyle='dotted')
	plt.grid(True)
	plt.title("Degree distribution")
	st.pyplot()
	st.write(\
		f"* Approximation: k={k:2.1f}, slope={slope:2.1f}")

def eigenvalues(graph):
	eigvals = stats.spectrum(graph)
	plt.scatter(np.arange(len(eigvals)),eigvals, alpha = 0.5)
	plt.grid(True)
	plt.title("Laplacian eigenvalues")
	st.pyplot()
	st.write(f"* Spectral gap: {eigvals[0]-eigvals[1]:2.1f}")
	st.write(f"* Smallest nonzero eigenvalue: {np.min(eigvals[eigvals>1e-10]):e}")

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
	#m = phys.mass(graph)
	e = phys.energy(graph)
	grav = sorted(np.array(e))
	density = gaussian_kde(grav)
	plt.plot(grav,density(grav))
	plt.title("Potential energy")
	plt.grid(True);
	st.pyplot()
	st.write(f"* Mean energy {np.mean(e):e}")
	st.write(f"* % attractive {100*len(e[e>0])/len(e):2.1f}%")

def gravity(graph):
	m = phys.mass(graph)
	e = phys.energy(graph)
	grav = np.array(sorted(np.array(e)*np.array(m)))
	density = gaussian_kde(grav)
	plt.plot(grav,density(grav))
	plt.title("Gravity momentum")
	plt.grid(True);
	st.pyplot()
	st.write(f"* Mean gravity {np.mean(grav):e}")
	st.write(f"* % collapsing {100*len(grav[grav>0])/len(grav):2.1f}%")


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

def sufficient(graph):
	return graph.number_of_nodes() > 5

def graph_plot(G, conn, center, radius, communities = False):
	full_graph = center is None
	st.write(f"Net subgraph/full graph outwards momentum: **{-phys.net_gravity(G):2.3f}**/{-chem.total_energy(conn):2.3f}")
	viz.draw(G,conn,labels = not full_graph, cmap=cmap)

	out, coll = chem.gravity_partition(G,conn)
	ui.separator()

	if sufficient(G):
		st.write("### Collapsing")
		viz.draw(out,conn,cmap=cmap)
		st.write("### Expanding")
		viz.draw(coll,conn,cmap=cmap)

	if full_graph:
		ui.separator()
		st.write("### Components")
		S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap)
			ui.separator()

	if sufficient(G) and communities:
		u = nx.algorithms.community.label_propagation.label_propagation_communities(G)
		thresh = 4 if full_graph else 4
		S = [G.subgraph(c).copy() for c in u if len(c)>thresh]
		st.write("### Communities")
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap)
			ui.separator()

def mintree(G,conn):
	if sufficient(G):
		H = nx.minimum_spanning_tree(G)
		ui.separator()
		st.write("#### Minimum tree")
		viz.draw(H, conn, cmap = cmap)
		st.pyplot()

def maxtree(G,conn):
	if sufficient(G):
		J = nx.maximum_spanning_tree(G)
		st.write("#### Maximum tree")
		viz.draw(J, conn, cmap = cmap)
		st.pyplot()

def view_energy(G,conn):
	if sufficient(G):
		ui.separator()
		st.write("### Energy density")
		energy(G)

def view_gravity(G,conn):
	if sufficient(G):
		ui.separator()
		st.write("### Momentum")
		gravity(G)


def view_spectrum(G,conn):
	if sufficient(G):	
		ui.separator()
		st.write("### Laplacian spectrum")
		eigenvalues(G)


def view_degrees(G,conn):
	if sufficient(G):
		ui.separator()
		st.write("### Degree distribution")
		plot_degree_distribution(G)

	
