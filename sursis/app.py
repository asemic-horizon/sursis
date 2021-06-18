import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
#st.beta_set_page_config(layout="wide")

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
###


node_mode = "New node"
edge_mode = "Connect"
cluster_mode = "Cluster"
trail_mode = "Trailing new"
dyad_mode = "Dyad"
triad_mode = "Triad"
merge_mode = "Merge"
view_mode = "Visualization"
stats_mode = "Advanced"
spath_mode = "Spath"

with nc() as conn:
	st.write("## `sursis`")
	col1, col2 = st.beta_columns(2)

	major_mode = col1.radio(label="Major mode",\
                              options=["Browse","Edit"])
	if major_mode == "Browse":
		op_mode=col2.radio(label="Operation mode",\
			options=[view_mode, spath_mode, stats_mode])
	elif major_mode == "Edit":
		op_mode = col2.radio(label="Operation mode",\
			options=[trail_mode, dyad_mode, triad_mode,merge_mode, edge_mode,
			 node_mode,
		 	])

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
	elif op_mode== cluster_mode:
		ui.separator()
		st.write("### Cluster connect")
		dlg.cluster_connect(conn)
	elif op_mode == trail_mode:
		ui.separator()
		st.write("### Add new node and connect to existing")
		dlg.trail_node_entry(conn)
	elif op_mode == merge_mode:
		ui.separator()
		st.write("### Merge nodes")
		dlg.node_merge(conn)
	elif op_mode == spath_mode:
		dlg.spaths(conn)
	elif op_mode == stats_mode:
		dlg.advanced(conn)
	elif op_mode == view_mode:
		ui.separator()
		c1, c2 = st.beta_columns(2)
		full_graph = c1.checkbox("Full graph",value=False)
		communities = True if full_graph else False #st.checkbox("Communities", value = False)

		if full_graph:
			center, radius = None, None
		if not full_graph:
			order = c2.checkbox("Order by energy", value=False)
			fields = list(reversed(db.list_nodes(conn, order = order)))
			u = 0
			d1,d2 = st.beta_columns(2)
			center = d1.selectbox("Choose nodes",fields,index = u)
			radius = d2.number_input("Radius",value=3)
		G = chem.graph(conn,center,radius)
		gv.graph_plot(G, conn,center,radius, communities)

		mintree = st.checkbox("Minimum tree", value = False)
		if mintree:	gv.mintree(G,conn)

		maxtree = st.checkbox("Maximum tree", value = False)
		if maxtree: gv.maxtree(G,conn)

		energy_density = st.checkbox("Energy density", value = True)
		if energy_density:
			gv.view_energy(G,conn)
			#gv.view_gravity(G,conn)

		dd = st.checkbox("Degree distribution", value = True)
		if dd: gv.view_degrees(G,conn)

		spectrum = st.checkbox("Spectrum",value=False)
		if spectrum: gv.view_spectrum(G,conn)
