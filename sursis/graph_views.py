import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import networkx as nx 
import collections
import numpy as np
from backend import physics as phys
from backend import graph_physics as chem
from backend import stats
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde
import ui_elems as ui
import viz

#cmap = "RdYlBu"
#cmap = "PuOr"
#cmap = "jet"
#cmap = "coolwarm"
#cmap = "bwr"
#cmap = "gist_stern"
cmap = "PiYG_r"

def power_law(x,k,slope):
	return np.exp(np.log(k) + slope*np.log(x))

def fit_power_distribution(deg,cnt):
	popt, _ = curve_fit(f=power_law,xdata=deg,ydata=cnt)
	k, slope = tuple(popt)
	return k, slope

def plot_degree_distribution(graph):
	deg, cnt = stats.degree_distribution(graph)
	k, slope = fit_power_distribution(deg,cnt)
	k_, slope_ = fit_power_distribution(deg[2:],cnt[2:])
	plt.scatter(deg,cnt)
	plt.plot(deg,power_law(deg,k,slope), linewidth=1,c='k',linestyle='dotted')
	plt.plot(deg,power_law(deg,k_,slope_), linewidth=1,c='b',linestyle='dotted')
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

def mass(graph,conn):
	m = chem.read_node_prop(conn,graph,"mass")
	density = gaussian_kde(m)
	plt.plot(m,density(m))
	plt.grid(True)
	plt.title("Mass")
	plt.xscale("log")
	st.pyplot()
	st.write(f"* Mean mass {np.mean(m):e}")

def energy(graph,conn):
	e = chem.read_node_prop(conn,graph,"energy")
	grav = np.array(sorted(np.array(e)/len(e)))
	qtile = np.linspace(0,1,len(grav))
	#density = gaussian_kde(grav)
	plt.plot(grav,qtile)
	plt.axhline(0.5)
	plt.axvline(np.median(grav),c='g',linestyle="dotted")
	plt.axvline(np.mean(grav),c='r',linestyle="dashed")
	plt.title("Cumulative energy")
	# grav = np.array(sorted(np.array(e)*np.array(m)))
	# density = gaussian_kde(grav)
	# plt.plot(grav,density(grav))
	# plt.title("Gravity momentum")
	plt.grid(True);
	st.pyplot()
	st.write(f"* % expanding {100*len(grav[grav>0])/len(grav):2.1f}%")



def stats_view(graph):

	plot_degree_distribution(graph)
	eigenvalues(graph)
	mass(graph)
	energy(graph)
	phase(graph)

def sufficient(graph):
	return graph.number_of_nodes() > 5

def graph_plot(G, conn, center, radius, communities = False):
	pos_fun = nx.kamada_kawai_layout
	full_graph = center is None
	if full_graph: pos = nx.spring_layout
	a = -chem.subgraph_energy(conn,G)
	b = -chem.total_energy(conn)
	st.write(f"Net gravity = **{a:2.3f}** - {b:2.3f} = {a-b:2.3f}")
	viz.draw(G,conn,labels = not full_graph, cmap=cmap,pos_fun = pos_fun)
	try:
		out, coll = chem.gravity_partition(G,conn)
		ui.separator()
		st.write("### Expanding")
		viz.draw(out,conn,cmap=cmap,pos_fun = pos_fun)
		st.write("### Collapsing")
		viz.draw(coll,conn,cmap=cmap,pos_fun = pos_fun)
	except:
		st.write("Couldn't make expanding/collapsing subsets")

	if full_graph:
		ui.separator()
		st.write("### Components")
		S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap, pos_fun = pos_fun)
			ui.separator()

	if sufficient(G) and communities:
		u = nx.algorithms.community.label_propagation.label_propagation_communities(G)
		thresh = 4 if full_graph else 4
		S = [G.subgraph(c).copy() for c in u if len(c)>thresh]
		st.write("### Communities")
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap, pos_fun = pos_fun)
			ui.separator()

def mintree(G,conn):
	if sufficient(G):
		H = nx.minimum_spanning_tree(G)
		ui.separator()
		st.write("#### Minimum tree")
		viz.draw(H, conn, cmap = cmap, pos_fun = lambda G: nx.spring_layout(G,k=0.2))
		st.pyplot()

def maxtree(G,conn):
	if sufficient(G):
		J = nx.maximum_spanning_tree(G)
		st.write("#### Maximum tree")
		viz.draw(J, conn, cmap = cmap, pos_fun = lambda G: nx.spring_layout(G,k=0.2))
		st.pyplot()

def view_energy(G,conn):
	if sufficient(G):
		ui.separator()
		st.write("### Energy density")
		energy(G,conn)

# def view_gravity(G,conn):
# 	if sufficient(G):
# 		ui.separator()
# 		st.write("### Momentum")
# 		gravity(G,conn)


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

	
