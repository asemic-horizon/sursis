import streamlit as st
import networkx as nx
from db import *
import random
st.write("## Data entry")
mode = st.radio("Mode",
	["Nodes","Connections"])

if mode == "Nodes":
	field = st.text_input('Text field')
	add_button = st.button("Add")
	del_button = st.button("Delete")
	if field and add_button: 
		write_node(field)
	if field and del_button:
		found = del_node(field)
		if not found:
			st.write("(Node not found.)")
if mode == "Connections":
	fields = query_nodes()
	field1 = st.selectbox("Source",fields)
	field2 = st.selectbox("Target",fields)
	add_button = st.button("Connect")
	del_button = st.button("Disconnect")
	if field1 and field2 and add_button: 
		write_edge(field1,field2)
	if field1 and field2 and del_button:
		found = del_edge(field1, field2)
		if not found:
			st.write("(Edge nt found.)")

st.write("## Graph visualization")


G = graph()
pos = nx.kamada_kawai_layout(G)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()


H = nx.minimum_spanning_tree(G)
J = nx.maximum_spanning_tree(H)
same = H.edges()==J.edges()
if same:
    st.write("## Spanning tree")
else:
    st.write("## Minimum tree")
pos = nx.kamada_kawai_layout(H)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()

J = nx.maximum_spanning_tree(G)
if not same:
    st.write("## Maximum tree")
    pos = nx.planar_layout(J)
    nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()
