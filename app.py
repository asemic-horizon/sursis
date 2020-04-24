import streamlit as st
import networkx as nx
import random
import layout
#
import db
import ui_modules as ui

st.write("### Data entry")

temp = db.list_nodes()
fst = len(temp)-1
snd = len(temp)-2

input_mode = st.radio(label="Mode",options=["Basic data entry","Advanced functionality"])


if input_mode == "Basic data entry":
# node entry
	st.write("**Nodes**")
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
			try:
				snd = fst; fst = nodes.index(node)
			except:
				st.write("(Minor failure setting defaults.)")
		if node and del_button:
			found = db.del_node(node)
			fst = snd
			if not found:
				st.write("(Node not found.)")
	ui.separator()
#edge entry
	st.write("**Connections**")
	nodes = db.list_nodes()
	node_1 = st.selectbox("Source",nodes,index=fst)
	node_2 = st.selectbox("Target",nodes,index=snd)
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if node_1 and node_2 and add_button: 
		db.write_edge(node_1,node_2)
		fst = nodes.index(node_1); snd = nodes.index(node_2)
		ui.confirm()
	if node_1 and node_2 and del_button:
		found = db.del_edge(node_1, node_2)
		if not found:
			st.write("(Edge not found.)")

elif input_mode == "Advanced functionality":
	st.write("**Node merge**")
	nodes = db.list_nodes()
	u,v = ui.representative(nodes)
	node_1 = st.selectbox("Source 1",nodes,index=u)
	node_2 = st.selectbox("Source 2",nodes,index=v)
	if node_1 in nodes and node_2 in nodes:
		new_node = st.text_input("New node", value=f"{node_1}/{node_2}")
		merge_button = st.button("Merge")
		if merge_button:
			db.merge_nodes(node_1,node_2, new_node)
			ui.confirm()

ui.separator()
st.write("### Graph visualization")

ego = st.checkbox("Full graph",value=True)
if ego:
	center = None
	radius = None
	alpha = 0.5
else:
	fields = db.list_nodes()
	u, _ = ui.representative(fields)
	center = st.selectbox("Choose nodes",fields,index = u)
	radius = st.slider("Radius",1,10,1)
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
