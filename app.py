import streamlit as st
import networkx as nx
from db import *
import random
st.write("### Data entry")
mode = st.radio("Mode",
	["Nodes","Connections"])

if mode == "Nodes":
	field = st.text_input('Enter node name')
	add_button = st.button("Add")
	del_button = st.button("Delete")
	if field and add_button: 
		write_node(field)
	if field and del_button:
		found = del_node(field)
		if not found:
			st.write("(Node not found.)")
if mode == "Connections":
	fields = list(reversed(query_nodes()))
	field1 = st.selectbox("Source",fields,index=0)
	field2 = st.selectbox("Target",fields,index=1)
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if field1 and field2 and add_button: 
		write_edge(field1,field2)
	if field1 and field2 and del_button:
		found = del_edge(field1, field2)
		if not found:
			st.write("(Edge not found.)")

st.write("### Graph visualization")

ego = st.checkbox("Full graph",value=True)
if ego:
	center = None
	radius = None
else:
	fields = query_nodes()
	chosen = random.randint(1,len(fields-1))
	center = st.selectbox("Choose nodes",fields,index=chosen)
	radius = st.slider("Radius",1,6,1)

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
