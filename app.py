import streamlit as st
import networkx as nx
from db import *
import random

def representative(fields):
	middle = len(fields)//2 if len(fields)>4 else 1
	middle_ = middle + 1 if middle>1 else 1
	return middle, middle_
st.write("### Data entry")

input_mode = st.radio(options=["Basic data entry","Advanced functionality"])


if input_mode == "Basic data entry":
# node entry
	st.write("**Nodes**")
	field = st.text_input('Enter node name')
	add_button = st.button("Add node")
	del_button = st.button("Delete node")
	if field and add_button: 
		write_node(field)
	if field and del_button:
		found = del_node(field)
		if not found:
			st.write("(Node not found.)")
	st.write("----")
#edge entry
	st.write("**Connections**")
	fields = list(reversed(query_nodes()))
	u,v = representative(fields)
	field1 = st.selectbox("Source",fields,index=u)
	field2 = st.selectbox("Target",fields,index=v)
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if field1 and field2 and add_button: 
		write_edge(field1,field2)
	if field1 and field2 and del_button:
		found = del_edge(field1, field2)
		if not found:
			st.write("(Edge not found.)")
elif input_mode == "Advanced functionality":
	st.write("**Advanced functionality TK**")

st.write("### Graph visualization")

ego = st.checkbox("Full graph",value=True)
if ego:
	center = None
	radius = None
else:
	fields = query_nodes()
	u, _ = representative(fields)
	center = st.selectbox("Choose nodes",fields,index = u)
	radius = st.slider("Radius",1,10,1)

algo0 = "Large-scale structure"
algo1 = "Readability"
algo = st.radio("Prioritize",[algo0,algo1])

G = graph(center = center, radius = radius)
if algo == algo0:
    pos = nx.spring_layout(G)
else:
    pos = nx.kamada_kawai_layout(G)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8,width=0.2)

st.pyplot()

messages = [
f"{nx.number_of_nodes(G)} nodes, {nx.number_of_edges(G)} edges, {100*nx.density(G):2.2f}% density",
f"{100*nx.average_clustering(G):2.2f}% of triangles, {100*nx.algorithms.cluster.transitivity(G):2.2f}% of triads",
f"{nx.number_connected_components(G)} components",
]
for msg in messages:
	st.write(f"* {msg}")

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
