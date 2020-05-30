import streamlit as st
import networkx as nx
#
import backend.db as db
import backend.physics as phys
import backend.graph_physics as chem
#
import graph_views as gv
import ui_elems as ui
import dialogs as dlg
#
from backend.db import nc



node_mode = "Nodes"
edge_mode = "Connections"
cluster_mode = "Cluster"
trail_mode = "Trailing"
dyad_mode = "Dyad"
triad_mode = "Triad"
merge_mode = "Merge"
view_mode = "Visualization"
stats_mode = "Advanced stats"

with nc() as conn:
	st.write("## `sursis`")

	op_mode = st.radio(label="Operation mode",\
		options=[view_mode,node_mode,trail_mode, edge_mode, cluster_mode, dyad_mode, triad_mode, merge_mode,stats_mode,])

	if op_mode == node_mode:
		ui.separator()
		st.write("### Add/remove nodes")
		dlg.node_entry(conn)
	elif op_mode == dyad_mode:
		ui.separator()
		st.write("### Add two nodes and connect them")
		dlg.dyad_entry(conn)
	elif op_mode == triad_mode:
		ui.separator()
		st.write("### Add a parent node and two children")
		dlg.triad_entry(conn)
	elif op_mode == edge_mode:
		ui.separator()
		st.write("### Add/remove connections")
		dlg.edge_entry(conn)
	elif op_mode == trail_mode:
		ui.separator()
		st.write("### Add new node and connect to existing")
		dlg.trail_node_entry(conn)
	elif op_mode == merge_mode:
		ui.separator()
		st.write("### Merge nodes")
		dlg.node_merge(conn)
	elif op_mode == stats_mode:

		nb = chem.boundary(conn,"nodes")
		eb = chem.boundary(conn,"edges")
		st.write(f"Current boundary values - nodes: {nb}, edges: {eb}")
		node_boundary = st.number_input("Node boundary values",step=0.001,format="%2.4f")
		edge_boundary = st.number_input("Edge boundary values",step=0.001,format="%2.4f")

		chem.update_physics(conn,node_boundary, edge_boundary, fast=False)
		st.write(f"System energy: {chem.total_energy(conn):2.3f}")
		ui.confirm()
		G = chem.graph(conn)
		gv.view_energy(G,conn)
		gv.view_degrees(G,conn)
		gv.view_spectrum(G,conn)
	elif op_mode == view_mode:
		ui.separator()
		full_graph = st.checkbox("Full graph",value=False)
		communities = st.checkbox("Communities", value = False)
	
		if full_graph:
			center, radius = None, None
		if not full_graph:
			order = st.checkbox("Order by energy", value=False)
			fields = list(reversed(db.list_nodes(conn, order = order)))
			u = 0
			center = st.selectbox("Choose nodes",fields,index = u)
			radius = st.number_input("Radius",value=4)
		G = chem.graph(conn,center,radius)
		gv.graph_plot(G, conn,center,radius, communities)

		mintree = st.checkbox("Minimum tree", value = True)
		if mintree:	gv.mintree(G,conn)

		maxtree = st.checkbox("Maximum tree", value = False)
		if maxtree: gv.maxtree(G,conn)

		energy_density = st.checkbox("Energy density", value = True)
		if energy_density:
			gv.view_energy(G,conn)
			#gv.view_gravity(G,conn)

		dd = st.checkbox("Degree distribution", value = False)
		if dd: gv.view_degrees(G,conn)

		spectrum = st.checkbox("Spectrum",value=False)
		if spectrum: gv.view_spectrum(G,conn)
