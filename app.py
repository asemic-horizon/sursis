import streamlit as st
import networkx as nx
from db import *
import random

mode = st.radio("Modality",
	["Enter new node","Connect nodes"])

if mode == "Enter new node":
	field = st.text_input('Text field')
	if field: 
		write_node(field)
if mode == "Connect nodes":
	fields = query_nodes()
	field1 = st.selectbox("Source",fields)
	field2 = st.selectbox("Target",fields)
	button = st.button("Connect")
	if field1 and field2 and button: 
		write_edge(field1,field2)

nx.draw(graph())
st.pyplot()