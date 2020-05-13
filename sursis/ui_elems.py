import streamlit as st 
import networkx as nx 
import numpy as np
from time import ctime
from numpy.random import choice
from backend import db

def separator():
	st.write("----")

def confirm():
	st.write(f"Operation confirmed at {ctime()}.")

def if_confirm(pred,err="(Not found)"):
	if pred:
		confirm()
	else:
		st.write(err)

def known_field_input(conn,tag="Node", default=None, offset = None):
	nodes = list(reversed(db.list_nodes(conn)))
	if default:
		index = nodes.index(default)
	elif offset:
		index = 2
	else:
		index = 1
	field_input = st.selectbox(tag,nodes,index=index)
	return field_input

def add_del(tag1="Add",tag2="Delete"):
	add = st.button(tag1)
	rem = st.button(tag2)
	return add, rem


def similar(node,substring_length = 7, max_examples = 2):
	effective_length = min(len(node),substring_length)
	nodes = db.list_nodes()
	candidates = [n for n in nodes if n[:effective_length]==node[:effective_length] and n!=node]
	effective_num_candidates = min(len(candidates),max_examples)
	return list(set(np.random.choice(candidates,effective_num_candidates)))

# not currently used
def graph_views(G):
	messages = [
	f"{nx.number_of_nodes(G)} nodes, {nx.number_of_edges(G)} edges, {100*nx.density(G):2.2f}% density",
	f"{100*nx.average_clustering(G):2.2f}% of triangles, {100*nx.algorithms.cluster.transitivity(G):2.2f}% of triads",
	f"{nx.number_connected_components(G)} components",
	]
	for msg in messages:
		st.write(f"* {msg}")

