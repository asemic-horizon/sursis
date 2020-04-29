import streamlit as st
import networkx as nx
import random
import layout
#
import db
import ui_modules as ui
import viz, physical

db.calculate_potential()
node_mode = "Add/delete nodes"
conn_mode = "Add/delete connections"
nonn_mode = "Connect new node to existing"
merge_mode = "Merge"
view_mode = "Visualization"

st.write("## `sursis`")

op_mode = st.sidebar.radio(label="Operation mode",options=[view_mode,node_mode,conn_mode, nonn_mode, merge_mode])

if op_mode == node_mode:
	node = st.text_input('Enter node name')
	add_button = st.button("Add node")
	del_button = st.button("Delete node")
	if node and add_button: 
		db.write_node(node)
		ui.confirm()
		nodes = db.list_edges()
	if node and del_button:
		found = db.del_node(node)
		if found:
			ui.confirm()
		if not found:
			st.write("(Node not found.)")
elif op_mode == conn_mode:
	nodes = db.list_nodes()
	state = db.state()
	#u,v = state["last_add"], state["blast_add"]
	u = "jazz"
	v = "atomic blonde"
	node_1 = st.selectbox("Source",nodes,index=nodes.index(u))
	node_2 = st.selectbox("Target",nodes,index=nodes.index(v))
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if node_1 and node_2 and add_button: 
		db.write_edge(node_1,node_2)
		ui.confirm()
	if node_1 and node_2 and del_button:
		found = True
		while found:
			found = db.del_edge(node_1, node_2)
		st.write("(Edge deleted.)")
		ui.confirm()
elif op_mode == nonn_mode:
	nodes = db.list_nodes()
	node_1 = st.selectbox("Existing",nodes,index=nodes.index("jazz"))
	node_2 = st.text_input('New')

	nonn_button = st.button("Add and connect")
	if node_1 and node_2 and nonn_button:
		db.write_node(node_2); ui.confirm()
		db.write_edge(node_1,node_2); ui.confirm()
elif op_mode == merge_mode:
	nodes = db.list_nodes()
	u,v = 1,3
	node_1 = st.selectbox("Source 1",nodes,index=u)
	node_2 = st.selectbox("Source 2",nodes,index=v)
	if node_1 in nodes and node_2 in nodes:
		new_node = st.text_input("New node", value=f"{node_1}/{node_2}")
		merge_button = st.button("Merge")
		if merge_button:
			db.merge_nodes(node_1,node_2, new_node)
			ui.confirm()

elif op_mode == view_mode:
	cmap = "bone"
	ego = st.checkbox("Full graph",value=False)
	color = st.checkbox("Color",value = True)
	algo0 = "Large-scale structure"
	algo1 = "Readability"
	algo = st.radio("Prioritize",[algo0,algo1])

	if ego:
		center = None
		radius = None
		alpha = 0.5
	else:
		fields = db.list_nodes()
		u = fields.index("jerry")
		center = st.selectbox("Choose nodes",fields,index = u)
		radius = st.number_input("Radius",value=1)
		alpha = 1

	G = db.graph(center = center, radius = radius)
	pot = db.read_potential(G)
	if color:
		viz.draw_color(G,pot = pot, pos_fun = nx.spring_layout if algo==algo0 else nx.kamada_kawai_layout, cmap = cmap)	
	else:
		viz.draw_bw(G, pos_fun = nx.spring_layout if algo==algo0 else nx.kamada_kawai_layout)

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
	viz.draw_bw(G,nx.spring_layout)

	if not same:
	    st.write("#### Maximum tree")
	    pos = nx.spring_layout(J)
	    viz.draw_bw(J, nx.spring_layout)
	st.pyplot()
