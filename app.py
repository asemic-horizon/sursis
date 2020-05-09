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
cmap = "terrain_r"

node_mode = "Nodes"
edge_mode = "Connections"
trail_mode = "Trailing"
dyad_mode = "Dyad"
triad_mode = "Triad"
merge_mode = "Merge"
view_mode = "Visualization"
stats_mode = "Stats"

st.write("## `sursis`")

op_mode = st.radio(label="Operation mode",\
	options=[stats_mode,view_mode,node_mode,edge_mode, dyad_mode, triad_mode, trail_mode, merge_mode])

if op_mode == node_mode:
	st.write("### Add/remove nodes")
	with nc() as conn: dlg.node_entry(conn)
elif op_mode == dyad_mode:
	st.write("### Add two nodes and connect them")
	with nc() as conn: dlg.dyad_entry(conn)
elif op_mode == triad_mode:
	st.write("### Add a parent node and two children")
	with nc() as conn: dlg.triad_entry(conn)
elif op_mode == edge_mode:
	st.write("### Add/remove connections")
	with nc() as conn: dlg.edge_entry(conn)
elif op_mode == trail_mode:
	st.write("### Add new node and connect to existing")
	with nc() as conn: dlg.trail_node_entry(conn)
elif op_mode == merge_mode:
	st.write("### Merge nodes")
	with nc() as conn: dlg.node_merge(conn)
elif op_mode == stats_mode:
	with nc() as conn: graph = chem.graph(conn)
	graph_stats.stats_view(graph)
elif op_mode == view_mode:
	with nc() as conn:
		chem.update_physics(conn)
		ego = st.checkbox("Full graph",value=False)
		color = st.checkbox("Color",value = True)
		algo0 = "Spectral"
		algo1 = "Force-directed"

		algo = st.radio("Plot",[algo1,algo0])

		if ego:
			center = None
			radius = None
		else:
			fields = db.list_nodes(conn)
			u = db.count_nodes(conn)-1
			center = st.selectbox("Choose nodes",fields,index = u)
			radius = st.number_input("Radius",value=1)

		G = chem.graph(conn,center = center, radius = radius)
		spectral = lambda *args: nx.spectral_layout(scale=10,*args)
		viz.draw(
			G = G, conn=conn,
                        is_color = color,
                        labels = center is not None,
			prop="energy",
			pos_fun = spectral if algo==algo0 else\
				  nx.kamada_kawai_layout,
                        cmap = cmap)

		if ego:
			S = [G.subgraph(c).copy() for c in connected_components(G)]
			for s in S:				
				viz.draw(
					G = s, conn=conn,
		                        is_color = color,
		                        labels = True,
					prop="energy",
					pos_fun = spectral if algo==algo0 else\
						  nx.kamada_kawai_layout,
		                        cmap = cmap)
			ui.separator()
		ui.graph_stats(G)

		H = nx.minimum_spanning_tree(G)
		J = nx.maximum_spanning_tree(G)
		same = H.edges()==J.edges()
		if same:
		    st.write("#### Spanning tree")
		else:
		    st.write("#### Minimum tree")
		viz.draw(H,conn=conn, labels = center is not None, is_color = color, pos_fun = nx.kamada_kawai_layout, cmap = cmap, prop="energy")

		if not same:
		    st.write("#### Maximum tree")
		    viz.draw(J,conn = conn, labels = center is not None, is_color = color,  pos_fun = nx.kamada_kawai_layout, cmap = cmap, prop="energy")
		st.pyplot()
