import streamlit as st
import networkx as nx
import random
import layout
#
import db, viz
import physics as phys
import graph_physics as chem
import graph_stats
import ui_elems as ui
import dialogs as dlg
from db import nc

#cmap = "PuOr_r"


node_mode = "Nodes"
edge_mode = "Connections"
trail_mode = "Trailing"
dyad_mode = "Dyad"
triad_mode = "Triad"
merge_mode = "Merge"
view_mode = "Visualization"
stats_mode = "Advanced stats"

st.write("## `sursis`")

op_mode = st.radio(label="Operation mode",\
	options=[view_mode,node_mode,edge_mode, dyad_mode, triad_mode, trail_mode, merge_mode,stats_mode,])

if op_mode == node_mode:
	ui.separator()
	st.write("### Add/remove nodes")
	with nc() as conn: dlg.node_entry(conn)
elif op_mode == dyad_mode:
	ui.separator()
	st.write("### Add two nodes and connect them")
	with nc() as conn: dlg.dyad_entry(conn)
elif op_mode == triad_mode:
	ui.separator()
	st.write("### Add a parent node and two children")
	with nc() as conn: dlg.triad_entry(conn)
elif op_mode == edge_mode:
	ui.separator()
	st.write("### Add/remove connections")
	with nc() as conn: dlg.edge_entry(conn)
elif op_mode == trail_mode:
	ui.separator()
	st.write("### Add new node and connect to existing")
	with nc() as conn: dlg.trail_node_entry(conn)
elif op_mode == merge_mode:
	ui.separator()
	st.write("### Merge nodes")
	with nc() as conn: dlg.node_merge(conn)
elif op_mode == stats_mode:
	with nc() as conn: graph = chem.graph(conn)
	graph_stats.stats_view(graph)
elif op_mode == view_mode:
	ui.separator()
	full_graph = st.checkbox("Full graph",value=False)
	with nc() as conn: 
		chem.update_physics(conn)
		if full_graph:
			center, radius = None, None
		if not full_graph:
			fields = list(reversed(db.list_nodes(conn)))
			u = 1
			center = st.selectbox("Choose nodes",fields,index = u)
			radius = st.number_input("Radius",value=5)
		G = chem.graph(conn,center,radius)
		graph_stats.graph_plot(G, conn,center,radius)

	mintree = st.checkbox("Minimum tree", value = False)
	if mintree:
		with nc() as conn: graph_stats.mintree(G,conn)

	maxtree = st.checkbox("Maximum tree", value = True)
	if maxtree:
		with nc() as conn: graph_stats.maxtree(G,conn)

	energy_density = st.checkbox("Energy density", value = True)
	if energy_density:
		with nc() as conn: 
			graph_stats.view_energy(G,conn)
			graph_stats.view_gravity(G,conn)

	dd = st.checkbox("Degree distribution", value = False)
	if dd:
		with nc() as conn: 
			graph_stats.view_degrees(G,conn)

	spectrum = st.checkbox("Spectrum",value=False)
	if spectrum:
		with nc() as conn: graph_stats.view_spectrum(G,conn)