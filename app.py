import streamlit as st
import networkx as nx
import random
import layout
#
import db, viz
import physics as phys
import graph_physics as chem
import ui_elems as ui
import dialogs as dlg
from db import nc

cmap = "PuOr_r"

node_mode = "Nodes"
edge_mode = "Connections"
trail_mode = "Trailing"
dyad_mode = "Dyad"
triad_mode = "Triad"
merge_mode = "Merge"
view_mode = "Visualization"

st.write("## `sursis`")

op_mode = st.sidebar.radio(label="Operation mode",options=[view_mode,node_mode,edge_mode, dyad_mode, triad_mode, trail_mode, merge_mode])

if op_mode == node_mode:
	with nc() as conn: dlg.node_entry(conn)
elif op_mode == dyad_mode:
	with nc() as conn: dlg.dyad_entry(conn)
elif op_mode == triad_mode:
	with nc() as conn: dlg.triad_entry(conn)
elif op_mode == edge_mode:
	with nc() as conn: dlg.edge_entry(conn)
elif op_mode == trail_mode:
	with nc() as conn: dlg.trail_node_entry(conn)
elif op_mode == merge_mode:
	with nc() as conn: dlg.node_merge(conn)
elif op_mode == view_mode:
	with nc() as conn:
		chem.update_physics(conn)
		ego = st.checkbox("Full graph",value=False)
		color = st.checkbox("Color",value = True)
		algo0 = "Large-scale structure"
		algo1 = "Readability"
		algo = st.radio("Prioritize",[algo1,algo0])

		if ego:
			center = None
			radius = None
		else:
			fields = db.list_nodes(conn)
			u = fields.index("jazz")
			center = st.selectbox("Choose nodes",fields,index = u)
			radius = st.number_input("Radius",value=1)

		G = chem.graph(conn,center = center, radius = radius)

		viz.draw(
			G = G, conn=conn,
                        is_color = color,
			prop="energy",
			pos_fun = nx.spring_layout if algo==algo0 else\
				  nx.kamada_kawai_layout,
                        cmap = cmap)

		ui.separator()
		ui.graph_stats(G)

		H = nx.minimum_spanning_tree(G)
		J = nx.maximum_spanning_tree(H)
		same = H.edges()==J.edges()
		if same:
		    st.write("#### Spanning tree")
		else:
		    st.write("#### Minimum tree")
		pos = nx.spring_layout(H)
		viz.draw(G,conn=conn, is_color = color, pos_fun = nx.spring_layout, prop="mass")

		if not same:
		    st.write("#### Maximum tree")
		    pos = nx.spring_layout(J)
		    viz.draw(J,conn = conn, is_color = color,  pos_fun = nx.spring_layout, cmap = cmap, prop="mass")
		st.pyplot()
