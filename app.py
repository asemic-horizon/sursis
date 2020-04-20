import streamlit as st
import networkx as nx
from db import *
import random
st.write("## Data entry")
mode = st.radio("Modality",
	["Enter new node","Connect nodes"])

if mode == "Enter new node":
	field = st.text_input('Text field')
	add_button = st.button("Add")
	del_button = st.button("Delete")
	if field and add_button: 
		write_node(field)
	if field and del_button:
		found = del_node(field)
		if not found:
			st.write("(Node not found.)")
if mode == "Connect nodes":
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


layout = st.radio("Algorithm",["planar","spring"])
G = graph()
if layout == "spring":
	pos = nx.spring_layout(G)
if layout == "planar":
	pos = nx.planar_layout(G)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()

st.write("## Minimum tree")


layout_min = "spring"
H = nx.minimum_spanning_tree(G)
if layout_min == "spring":
	pos = nx.spring_layout(H)
if layout_min == "planar":
	pos = nx.planar_layout(H)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()

st.write("## Maximum tree")


layout_min = "spring"
J = nx.maximum_spanning_tree(G)
if layout_min == "spring":
	pos = nx.spring_layout(J)
if layout_min == "planar":
	pos = nx.planar_layout(J)
nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=8)

st.pyplot()