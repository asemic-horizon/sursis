import streamlit as st
import networkx as nx
import random
import layout
#
import db
import ui_modules as ui

node_mode = "Node entry"
conn_mode = "Connection entry"
merge_mode = "Merge"
view_mode = "Visualization"

st.write("## `sursis`")

op_mode = st.sidebar.radio(label="Operation mode",options=[view_mode,node_mode,conn_mode,merge_mode])

if op_mode == node_mode:
	node = st.text_input('Enter node name')
	confounders = ui.similar(node)
	if not node:
		go_ahead = False
	if node and not confounders:
		go_ahead = True
	if node and confounders:
		go_ahead = st.checkbox(f"(Checked similarly-named nodes: {','.join(confounders)})",value=False)
	if go_ahead:
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
	node_1 = st.selectbox("Source",nodes,index=3)
	node_2 = st.selectbox("Target",nodes,index=1)
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if node_1 and node_2 and add_button: 
		db.write_edge(node_1,node_2)
		ui.confirm()
	if node_1 and node_2 and del_button:
		found = db.del_edge(node_1, node_2)
		if found:
			ui.confirm()
		if not found:
			st.write("(Edge not found.)")
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

	ego = st.checkbox("Full graph",value=False)
	if ego:
		center = None
		radius = None
		alpha = 0.5
	else:
		fields = db.list_nodes()
		u = 1
		center = st.selectbox("Choose nodes",fields,index = u)
		radius = st.number_input("Radius",value=1)
		alpha = 1

	algo0 = "Large-scale structure"
	algo1 = "Readability"
	algo = st.radio("Prioritize",[algo0,algo1])

	G = db.graph(center = center, radius = radius)
	if algo == algo0:
	    pos = nx.spring_layout(G)
	else:
	    pos = nx.kamada_kawai_layout(G)
	nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8,width=0.2,alpha=alpha)

	st.pyplot()
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
	nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8,width=0.2)

	st.pyplot()

	J = nx.maximum_spanning_tree(G)
	if not same:
	    st.write("#### Maximum tree")
	    pos = nx.spring_layout(J)
	    nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8,width=0.2)

	st.pyplot()
