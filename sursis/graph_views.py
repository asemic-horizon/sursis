import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import networkx as nx 
import collections
import numpy as np
from backend import physics as phys
from backend import graph_physics as chem
from backend import stats
from scipy.stats import gaussian_kde
import ui_elems as ui
import viz

#cmap = "RdYlBu"
#cmap = "PuOr"
#cmap = "jet"
#cmap = "coolwarm"
cmap = "bwr"
#cmap = "gist_stern"
#cmap = "PiYG_r"
#cmap = "Spectral"
#cmap = "nipy_spectral_r"


def plot_degree_distribution(graph):
	deg, cnt = stats.degree_distribution(graph)
	deg = np.array(deg); cnt = np.array(cnt)
	k, slope = stats.fit_power_distribution(deg,cnt)
	plt.scatter(deg,cnt)
	plt.plot(deg,stats.power_law(deg,k,slope), linewidth=1,c='k',linestyle='dotted')
	plt.grid(True)
	plt.title("Degree distribution")

	st.pyplot()
	st.write(\
		f"* Approximation: $f \\approx {k:2.0f}x^"+"{"+f"{slope:2.2f}"+"}$")

def eigenvalues(graph):
	eigvals = stats.spectrum(graph)
	eigvals = eigvals[eigvals>1e-6]
	eigvals.sort()
	plt.scatter(np.arange(len(eigvals)),1/eigvals, alpha = 0.5)
	plt.yscale("log")
	plt.grid(True)
	plt.title("Inverse Laplacian eigenvalues")
	st.pyplot()
	st.write(f"* Spectral gap: {1/eigvals[0]-1/eigvals[1]:2.2f}")

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
	plt.axhline(0.5,c='g',linestyle="dotted")
	plt.axvline(np.median(grav),c='g',linestyle="dotted")
	plt.axvline(np.mean(grav),c='r',linestyle="dashed")
	plt.axvline(0,c='y',linestyle="dotted")

#	plt.axhline(np.where(grav==np.mean(grav))[0],c="r",linestyle="dashed")
	plt.title("Cumulative energy")
	# grav = np.array(sorted(np.array(e)*np.array(m)))
	# density = gaussian_kde(grav)
	# plt.plot(grav,density(grav))
	# plt.title("Gravity momentum")
	plt.grid(True);
	st.pyplot()
	st.write(f"* % expanding {100*len(grav[grav>1e-6])/len(grav):2.1f}%")



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
	if full_graph: pos = nx.kamada_kawai_layout
	# a = -chem.subgraph_energy(conn,G)
	# b = -chem.total_energy(conn)
	# st.write(f"Net gravity = **{a:2.3f}** - {b:2.3f} = {a-b:2.3f}")
	try:
		leaves, expected_leaves, slope = stats.leaf_analysis(G)
		st.write(f"{leaves}/{expected_leaves:1.0f} = {slope:1.2f}")
	except: pass
	viz.draw(G,conn,labels = not full_graph, cmap=cmap)
	try:
		out, coll = chem.gravity_partition(G,conn)
		ui.separator()
		st.write("### Expanding")
		viz.draw(out,conn,cmap=cmap)
		st.write("### Collapsing")
		viz.draw(coll,conn,cmap=cmap)
	except:
		st.write("Couldn't make expanding/collapsing subsets")

	if full_graph:
		ui.separator()
		st.write("### Components")
		S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap)
			ui.separator()

	if sufficient(G) and communities:
		u = nx.algorithms.community.kernighan_lin.kernighan_lin_bisection(G)
		thresh = 4 if full_graph else 4
		S = [G.subgraph(c).copy() for c in u if len(c)>thresh]
		st.write("### Communities")
		for subgraph in S:
			viz.draw(subgraph, conn, cmap = cmap)
			ui.separator()

def paths(G,conn, source, target):
	ps = nx.algorithms.shortest_paths.\
			generic.all_shortest_paths(G,source,target)

	spath = nx.Graph()
	for q in ps:
		for p in q:
			S = nx.ego_graph(G,n=p,radius = 1)
			spath = nx.compose(spath,S)
		st.write(f"Steps: {len(q)-1}")
		st.write(f" $\\to$ ".join(q))
		viz.draw(spath,conn,cmap=cmap)
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

	
